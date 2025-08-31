#!/usr/bin/env python3
"""
pathology.py: A Unified Preprocessing and Embedding Pipeline for Pathological Data.

This script provides an end-to-end workflow for processing structured pathological data
from a JSON file into 512-dimensional embeddings. It is designed to be robust,
user-friendly, and ready for integration into larger machine learning packages.

The pipeline executes two main stages in a single run:

1.  **Advanced Preprocessing**:
    -   Loads raw pathological data from a user-specified JSON file.
    -   Cleans and preprocesses raw data, including handling numeric-like strings.
    -   Automatically identifies and encodes numeric and categorical features.
    -   Performs a sophisticated imputation ensemble to handle missing data, using:
        -   K-Nearest Neighbors (KNN) imputation as a baseline.
        -   A Variational Autoencoder (VAE) for probabilistic, multi-sample imputation.
        -   Graph smoothing to refine imputations based on patient similarity.
    -   Aggregates the multiple imputations to compute mean and variance, capturing uncertainty.
    -   Saves the processed features and metadata to `pathological_preprocessed_advanced.h5`.

2.  **Embedding Generation**:
    -   Constructs an input matrix from the preprocessed features (mean, variance, and missingness mask).
    -   Trains a Denoising Autoencoder (AE) to learn a compressed, 512-dimensional representation.
    -   Uses Principal Component Analysis (PCA) as a deterministic fallback if PyTorch is unavailable.
    -   Saves the final 512-d embeddings to `pathological_embedding_512.h5`.

Usage:
    python pathology.py --input_json /path/to/your/pathological_data.json --out_dir /path/to/output_directory
"""

import os
import json
import argparse
import warnings
from pathlib import Path

import h5py
import joblib
import numpy as np
import pandas as pd

# Machine Learning Imports
from sklearn.decomposition import PCA
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.preprocessing import StandardScaler

# Optional PyTorch Import
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# --- Configuration ---
SEED = 42
EMBED_DIM = 512
M_IMPUTATIONS = 5
GRAPH_ALPHA = 0.6
DEVICE = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"

# Set seeds for reproducibility
np.random.seed(SEED)
if TORCH_AVAILABLE:
    torch.manual_seed(SEED)

# Suppress common warnings for cleaner output
warnings.filterwarnings("ignore")


# ---------- PyTorch Model Definitions ----------

if TORCH_AVAILABLE:
    class VAEImputer(nn.Module):
        """A Variational Autoencoder for probabilistic imputation of missing data."""
        def __init__(self, inp_dim, latent_dim=64):
            super().__init__()
            hid = max(128, inp_dim // 2)
            self.encoder = nn.Sequential(nn.Linear(inp_dim, hid), nn.ReLU(),
                                         nn.Linear(hid, 128), nn.ReLU())
            self.fc_mu = nn.Linear(128, latent_dim)
            self.fc_logvar = nn.Linear(128, latent_dim)
            self.decoder = nn.Sequential(nn.Linear(latent_dim, 128), nn.ReLU(),
                                         nn.Linear(128, hid), nn.ReLU(),
                                         nn.Linear(hid, inp_dim))

        def reparameterize(self, mu, logvar):
            std = (0.5 * logvar).exp()
            eps = torch.randn_like(std)
            return mu + eps * std

        def forward(self, x):
            h = self.encoder(x)
            mu, logvar = self.fc_mu(h), self.fc_logvar(h)
            z = self.reparameterize(mu, logvar)
            recon = self.decoder(z)
            return recon, mu, logvar

    class DenoisingAE(nn.Module):
        """A Denoising Autoencoder to learn compact 512-d embeddings."""
        def __init__(self, inp_dim, bottleneck=EMBED_DIM):
            super().__init__()
            self.enc = nn.Sequential(
                nn.Linear(inp_dim, max(512, inp_dim // 2)), nn.GELU(),
                nn.Linear(max(512, inp_dim // 2), 1024), nn.GELU(),
                nn.Linear(1024, bottleneck)
            )
            self.dec = nn.Sequential(
                nn.Linear(bottleneck, 1024), nn.GELU(),
                nn.Linear(1024, max(512, inp_dim // 2)), nn.GELU(),
                nn.Linear(max(512, inp_dim // 2), inp_dim)
            )
        def forward(self, x):
            z = self.enc(x)
            rec = self.dec(z)
            return rec, z

    class IdxDataset(Dataset):
        """Helper Dataset to return indices, useful for batching."""
        def __init__(self, n): self.n = n
        def __len__(self): return self.n
        def __getitem__(self, idx): return idx

# ---------- Helper Function Definitions ----------

def load_json_df(path):
    """Loads a JSON file into a pandas DataFrame, handling potential errors."""
    try:
        return pd.read_json(path)
    except FileNotFoundError:
        print(f"Error: Input JSON file not found at {path}")
        exit(1)
    except ValueError as e:
        print(f"Error: Could not parse JSON file. Ensure it is valid. Details: {e}")
        exit(1)

def clean_numeric_string(x):
    """Cleans strings that represent numeric values, like '<0.1'."""
    if pd.isna(x): return np.nan
    if isinstance(x, (int, float)): return x
    s = str(x).strip()
    if not s: return np.nan
    try:
        return float(s)
    except ValueError:
        if s.startswith("<"):
            try:
                return float(s[1:]) / 2.0
            except ValueError:
                return np.nan
        return np.nan

def auto_select_columns(df):
    """Automatically selects numeric and categorical columns."""
    skip = {"patient_id"}
    numeric, categorical = [], []
    for c in df.columns:
        if c in skip: continue
        if pd.api.types.is_numeric_dtype(df[c]) or \
           (pd.to_numeric(df[c], errors="coerce").notna().sum() / len(df) > 0.5):
            numeric.append(c)
        else:
            categorical.append(c)
    return numeric, categorical

def frequency_encode(series):
    """Encodes a categorical series based on the frequency of its values."""
    s_filled = series.fillna("<<MISSING>>").astype(str)
    freq_map = s_filled.value_counts(normalize=True)
    return s_filled.map(freq_map)

def train_vae_imputer(X_filled, mask, latent_dim, epochs, batch_size, lr, device):
    """Trains the VAEImputer model."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required for VAE-based imputation.")
    n, d = X_filled.shape
    dl = DataLoader(IdxDataset(n), batch_size=batch_size, shuffle=True)
    model = VAEImputer(inp_dim=d, latent_dim=latent_dim).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    X_t, M_t = torch.from_numpy(X_filled).float().to(device), torch.from_numpy(mask).float().to(device)

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for idx in dl:
            xb, mb = X_t[idx], M_t[idx]
            recon, mu, logvar = model(xb)
            recon_loss = ((recon - xb)**2 * mb).sum() / (mb.sum() + 1e-8)
            kld_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / xb.size(0)
            loss = recon_loss + 1e-3 * kld_loss
            opt.zero_grad(); loss.backward(); opt.step()
            total_loss += loss.item() * xb.size(0)
        if epoch % 10 == 0 or epoch == 1:
            print(f"  VAE Epoch {epoch}/{epochs} | Loss: {total_loss/n:.6f}")
    return model

def sample_from_vae(model, X_filled, mask, n_samples, device):
    """Generates multiple imputation samples from the trained VAE."""
    model.eval()
    X_t = torch.from_numpy(X_filled).float().to(device)
    imputations = []
    with torch.no_grad():
        for _ in range(n_samples):
            recon, _, _ = model(X_t)
            recon_np = recon.cpu().numpy()
            filled_sample = X_filled.copy()
            filled_sample[mask == 0] = recon_np[mask == 0]
            imputations.append(filled_sample)
    return imputations

def smooth_with_graph(X, missing_mask, alpha, n_iter=10):
    """Refines imputed values using a patient similarity graph."""
    n, d = X.shape
    robust_cols = np.where(missing_mask.mean(axis=0) >= 0.5)[0]
    if len(robust_cols) == 0: robust_cols = np.arange(min(5, d))
    
    # Handle zero variance columns for RBF kernel
    sub_X = X[:, robust_cols]
    var = sub_X.var()
    gamma = 1.0 / (var + 1e-6) if var > 0 else 1.0

    S = rbf_kernel(sub_X, gamma=gamma)
    np.fill_diagonal(S, 0.0)
    row_sums = S.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    P = S / row_sums
    
    Xs = X.copy()
    for _ in range(n_iter):
        X_neighbors = P.dot(Xs)
        Xs[missing_mask == 0] = alpha * X_neighbors[missing_mask == 0] + (1 - alpha) * Xs[missing_mask == 0]
    return Xs

def train_denoising_ae(X, epochs, batch_size, lr, device):
    """Trains the DenoisingAE to generate embeddings."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required for Autoencoder-based embedding.")
    
    inp_dim = X.shape[1]
    model = DenoisingAE(inp_dim=inp_dim, bottleneck=EMBED_DIM).to(device)
    X_t = torch.from_numpy(X).float().to(device)
    dl = DataLoader(TensorDataset(X_t), batch_size=batch_size, shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-6)
    loss_fn = nn.MSELoss()

    for ep in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for (batch,) in dl:
            noisy_batch = batch * (torch.rand_like(batch) > 0.15).float()
            reconstructed, _ = model(noisy_batch)
            loss = loss_fn(reconstructed, batch)
            opt.zero_grad(); loss.backward(); opt.step()
            total_loss += loss.item() * batch.size(0)
        if ep % 10 == 0 or ep == 1:
            print(f"  AE Epoch {ep}/{epochs} | Loss: {total_loss/len(X):.6f}")

    model.eval()
    with torch.no_grad():
        _, embeddings = model(torch.from_numpy(X).float().to(device))
        return model, embeddings.cpu().numpy()


# ---------- Main Pipeline ----------

def main(args):
    """Main function to run the complete preprocessing and embedding pipeline."""
    # --- STAGE 1: PREPROCESSING ---
    print("--- Stage 1: Preprocessing Pathological Data ---")
    df = load_json_df(args.input_json)
    
    if "patient_id" not in df.columns:
        print("Error: 'patient_id' column is required in the input JSON.")
        exit(1)

    df["patient_id"] = df["patient_id"].astype(str)
    df = df.drop_duplicates(subset=["patient_id"]).set_index("patient_id")
    patient_ids = df.index.values
    n_patients = len(df)
    print(f"Loaded data for {n_patients} unique patients.")
    
    # Data cleaning for specific pathological fields
    if "closest_resection_margin_in_cm" in df.columns:
        df["closest_resection_margin_in_cm"] = df["closest_resection_margin_in_cm"].apply(clean_numeric_string)
    
    numeric_cols, categorical_cols = auto_select_columns(df)
    
    feat_df = pd.DataFrame(index=df.index)
    if numeric_cols:
        feat_df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    for col in categorical_cols:
        feat_df[f"freq__{col}"] = frequency_encode(df[col])
    for col in list(feat_df.columns):
        feat_df[f"miss__{col}"] = feat_df[col].isna().astype(int)

    feature_names = list(feat_df.columns)
    X_raw = feat_df.values.astype(float)
    mask = (~np.isnan(X_raw)).astype(int)
    print(f"Created feature matrix with shape: {X_raw.shape}")

    median_imputer = SimpleImputer(strategy="median")
    X_median = median_imputer.fit_transform(X_raw)
    scaler = StandardScaler()
    X_std = scaler.fit_transform(X_median)

    print("Running KNN imputer baseline...")
    knn_imputer = KNNImputer(n_neighbors=5)
    X_knn_unscaled = scaler.inverse_transform(knn_imputer.fit_transform(X_std))
    
    imputations, vae_model = [], None
    if not args.no_vae:
        if TORCH_AVAILABLE:
            print("Training VAE for probabilistic imputation...")
            X_filled_std = np.nan_to_num(X_std)
            latent_dim = min(64, max(8, X_std.shape[1] // 4))
            vae_model = train_vae_imputer(X_filled_std, mask, latent_dim, args.vae_epochs, args.batch_size, args.learning_rate, DEVICE)
            vae_samples_std = sample_from_vae(vae_model, X_filled_std, mask, M_IMPUTATIONS, DEVICE)
            imputations = [scaler.inverse_transform(s) for s in vae_samples_std]
        else:
            print("Warning: --no_vae=False but PyTorch is not available. Falling back to KNN.")
            args.no_vae = True

    if args.no_vae:
        imputations = [X_knn_unscaled.copy() for _ in range(M_IMPUTATIONS)]

    print("Applying graph smoothing to refine imputations...")
    smoothed_imputations = [smooth_with_graph(imp, mask, GRAPH_ALPHA) for imp in imputations]
    smoothed_imputations.append(X_knn_unscaled)

    Imps_stack = np.stack(smoothed_imputations, axis=0)
    mean_imp, var_imp = Imps_stack.mean(axis=0), Imps_stack.var(axis=0)
    mean_imp[mask == 1], var_imp[mask == 1] = X_raw[mask == 1], 0.0

    preproc_h5_path = args.out_dir / "pathological_preprocessed_advanced.h5"
    print(f"Saving preprocessed data to: {preproc_h5_path}")
    with h5py.File(preproc_h5_path, "w") as f:
        f.create_dataset("patient_id", data=np.array(patient_ids, dtype="S"))
        f.create_dataset("feature_names", data=np.array(feature_names, dtype="S"))
        f.create_dataset("features_mean", data=mean_imp.astype(np.float32))
        f.create_dataset("features_var", data=var_imp.astype(np.float32))
        f.create_dataset("missing_mask", data=mask.astype(np.int8))
    
    # --- STAGE 2: EMBEDDING GENERATION ---
    print("\n--- Stage 2: Generating 512-d Embeddings ---")
    X_for_embedding = np.concatenate([mean_imp, var_imp, mask.astype(np.float32)], axis=1)
    scaler_emb = StandardScaler()
    Xs = scaler_emb.fit_transform(X_for_embedding)
    
    embeddings, ae_model = None, None
    if args.embed_mode == "ae":
        if TORCH_AVAILABLE:
            print("Training Denoising Autoencoder for embeddings...")
            ae_model, embeddings = train_denoising_ae(Xs, args.embed_epochs, args.batch_size, args.learning_rate, DEVICE)
        else:
            print("Warning: --embed_mode='ae' but PyTorch not available. Falling back to PCA.")
            args.embed_mode = "pca"

    if args.embed_mode == "pca":
        print("Using PCA to generate embeddings...")
        n_comp = min(EMBED_DIM, Xs.shape[1])
        pca = PCA(n_components=n_comp, random_state=SEED)
        Z = pca.fit_transform(Xs)
        if n_comp < EMBED_DIM:
            Z = np.pad(Z, ((0, 0), (0, EMBED_DIM - n_comp)), 'constant')
        embeddings = Z.astype(np.float32)

    embed_h5_path = args.out_dir / "pathological_embedding_512.h5"
    print(f"Saving final embeddings to: {embed_h5_path}")
    with h5py.File(embed_h5_path, "w") as f:
        f.create_dataset("patient_id", data=np.array(patient_ids, dtype="S"))
        f.create_dataset("embedding_512", data=embeddings)

    print("\n--- Pipeline Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A unified pipeline for pathological data preprocessing and embedding generation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--input_json", type=Path, required=True, help="Path to the input pathological_data.json file.")
    parser.add_argument("--out_dir", type=Path, required=True, help="Directory to save all output files.")
    parser.add_argument("--no_vae", action="store_true", help="If set, skips VAE imputation and uses only KNN.")
    parser.add_argument("--vae_epochs", type=int, default=50, help="Number of epochs for VAE imputer training.")
    parser.add_argument("--embed_mode", choices=["ae", "pca"], default="ae", help="Method for embedding generation.")
    parser.add_argument("--embed_epochs", type=int, default=40, help="Number of epochs for Denoising AE training.")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size for training models.")
    parser.add_argument("--learning_rate", type=float, default=1e-3, help="Learning rate for training models.")

    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    main(args)