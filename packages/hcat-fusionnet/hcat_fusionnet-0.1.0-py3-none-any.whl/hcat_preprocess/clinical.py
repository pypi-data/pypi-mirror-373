#!/usr/bin/env python3
"""
clinical.py: A Unified Preprocessing and Embedding Pipeline for Clinical Data.

This script provides an end-to-end workflow for processing structured clinical data
from a JSON file into 512-dimensional embeddings. It is designed to be robust,
user-friendly, and ready for integration into larger machine learning packages.

The pipeline executes two main stages:

1.  **Advanced Preprocessing**:
    -   Loads raw clinical data from a user-specified JSON file.
    -   Derives survival and recurrence labels based on clinical definitions.
    -   Automatically identifies and encodes numeric and categorical features.
    -   Performs a sophisticated imputation ensemble to handle missing data, using:
        -   K-Nearest Neighbors (KNN) imputation as a baseline.
        -   A Variational Autoencoder (VAE) for probabilistic, multi-sample imputation.
        -   Graph smoothing to refine imputations based on patient similarity.
    -   Aggregates the multiple imputations to compute mean and variance, capturing uncertainty.
    -   Saves the processed features and metadata to `clinical_preprocessed_advanced.h5`.

2.  **Embedding Generation**:
    -   Constructs an input matrix from the preprocessed features (mean, variance, and missingness mask).
    -   Trains a Denoising Autoencoder (AE) to learn a compressed, 512-dimensional representation.
    -   Uses Principal Component Analysis (PCA) as a deterministic fallback if PyTorch is unavailable.
    -   Evaluates the quality of the generated embeddings on downstream survival and recurrence prediction tasks.
    -   Saves the final 512-d embeddings to `clinical_embedding_512.h5`.

Usage:
    python clinical.py --input_json /path/to/your/clinical_data.json --out_dir /path/to/output_directory

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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.model_selection import train_test_split
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
# These can be overridden by command-line arguments
SEED = 42
EMBED_DIM = 512
M_IMPUTATIONS = 5
GRAPH_ALPHA = 0.6
DEVICE = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"

# Time windows for label derivation
DAYS_5Y = 5 * 365
DAYS_2Y = 2 * 365

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

def derive_three_state_labels(df):
    """Derives 5-year survival and 2-year recurrence labels from raw clinical fields."""
    df = df.copy()
    surv_stat = df.get("survival_status", pd.Series(["unknown"] * len(df))).astype(str).str.lower()
    surv_cause = df.get("survival_status_with_cause", pd.Series([""] * len(df))).astype(str).str.lower()
    followup = pd.to_numeric(df.get("days_to_last_information"), errors="coerce")
    rec_flag = df.get("recurrence", pd.Series(["unknown"] * len(df))).astype(str).str.lower()
    days_rec = pd.to_numeric(df.get("days_to_recurrence"), errors="coerce")

    n = len(df)
    surv, rec = np.full(n, -1, dtype=np.int8), np.full(n, -1, dtype=np.int8)

    is_deceased_tumor = surv_cause.str.contains("tumor", na=False)
    died_within_5y = is_deceased_tumor & (followup <= DAYS_5Y)
    died_after_5y = is_deceased_tumor & (followup > DAYS_5Y)
    surv[died_within_5y] = 0
    surv[died_after_5y] = 1
    surv[(surv_stat == "living") & (followup >= DAYS_5Y)] = 1

    recurred_within_2y = (rec_flag == "yes") & (days_rec <= DAYS_2Y)
    no_recurrence_after_2y = (rec_flag == "no") & (followup >= DAYS_2Y)
    rec[recurred_within_2y] = 1
    rec[no_recurrence_after_2y] = 0

    return surv, rec

def auto_select_columns(df):
    """Automatically selects numeric and categorical columns for processing."""
    skip_cols = {
        "patient_id", "survival_status", "survival_status_with_cause",
        "days_to_last_information", "days_to_recurrence", "recurrence"
    }
    numeric_cols, categorical_cols = [], []
    for col in df.columns:
        if col in skip_cols:
            continue
        # If a column can be coerced to numeric for >50% of its values, treat as numeric
        if pd.to_numeric(df[col], errors='coerce').notna().sum() / len(df) > 0.5:
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)
    return numeric_cols, categorical_cols

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
    ds = IdxDataset(n)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=True)
    model = VAEImputer(inp_dim=d, latent_dim=latent_dim).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    X_t = torch.from_numpy(X_filled).float().to(device)
    M_t = torch.from_numpy(mask).float().to(device)

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for idx_batch in dl:
            idx = idx_batch.to(device)
            xb, mb = X_t[idx], M_t[idx]
            recon, mu, logvar = model(xb)
            recon_loss = ((recon - xb)**2 * mb).sum() / (mb.sum() + 1e-8)
            kld_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / xb.size(0)
            loss = recon_loss + 1e-3 * kld_loss # Small weight for KL divergence
            opt.zero_grad()
            loss.backward()
            opt.step()
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
            missing_indices = (mask == 0)
            filled_sample[missing_indices] = recon_np[missing_indices]
            imputations.append(filled_sample)
    return imputations

def smooth_with_graph(X, missing_mask, alpha, n_iter=10):
    """Refines imputed values using a patient similarity graph."""
    n, d = X.shape
    # Use columns with high observation rates to build the similarity graph
    robust_cols = np.where(missing_mask.mean(axis=0) >= 0.5)[0]
    if len(robust_cols) == 0:
        robust_cols = np.arange(min(5, d)) # Fallback to first 5 columns

    gamma = 1.0 / (X[:, robust_cols].var() + 1e-6)
    S = rbf_kernel(X[:, robust_cols], gamma=gamma)
    np.fill_diagonal(S, 0.0)
    row_sums = S.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0 # Avoid division by zero
    P = S / row_sums
    
    Xs = X.copy()
    for _ in range(n_iter):
        X_neighbors = P.dot(Xs)
        # Update only the originally missing values
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
            # Apply dropout noise
            noisy_batch = batch * (torch.rand_like(batch) > 0.15).float()
            reconstructed, _ = model(noisy_batch)
            loss = loss_fn(reconstructed, batch)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item() * batch.size(0)

        if ep % 10 == 0 or ep == 1:
            print(f"  AE Epoch {ep}/{epochs} | Loss: {total_loss/len(X):.6f}")

    model.eval()
    with torch.no_grad():
        _, embeddings = model(torch.from_numpy(X).float().to(device))
        return model, embeddings.cpu().numpy()

def evaluate_embeddings(Z, labels, task_name="task"):
    """Evaluates embedding quality on a downstream classification task."""
    known_mask = labels != -1
    if known_mask.sum() < 10: # Require at least 10 labels for a meaningful split
        print(f"[{task_name}] Insufficient labels ({known_mask.sum()}) to evaluate.")
        return
    
    Xk, yk = Z[known_mask], labels[known_mask]
    stratify = yk if np.unique(yk).size > 1 else None
    Xtr, Xte, ytr, yte = train_test_split(Xk, yk, test_size=0.2, random_state=SEED, stratify=stratify)

    clf = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED)
    clf.fit(Xtr, ytr)
    ypred = clf.predict(Xte)
    acc = accuracy_score(yte, ypred)
    f1 = f1_score(yte, ypred, average='binary', zero_division=0)
    print(f"  [{task_name}] Evaluation | Accuracy: {acc:.4f} | F1-score: {f1:.4f}")


# ---------- Main Pipeline ----------

def main(args):
    """Main function to run the complete preprocessing and embedding pipeline."""

    # --- STAGE 1: PREPROCESSING ---
    print("--- Stage 1: Preprocessing Clinical Data ---")
    df = load_json_df(args.input_json)

    if "patient_id" not in df.columns:
        print("Error: 'patient_id' column is required in the input JSON.")
        exit(1)
        
    df["patient_id"] = df["patient_id"].astype(str)
    df = df.drop_duplicates(subset=["patient_id"]).set_index("patient_id")
    patient_ids = df.index.values
    n_patients = len(df)
    print(f"Loaded data for {n_patients} unique patients.")

    surv_labels, rec_labels = derive_three_state_labels(df)
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

    # Imputation steps
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
        print("Using repeated KNN imputations as samples.")
        imputations = [X_knn_unscaled.copy() for _ in range(M_IMPUTATIONS)]

    print("Applying graph smoothing to refine imputations...")
    smoothed_imputations = [smooth_with_graph(imp, mask, GRAPH_ALPHA) for imp in imputations]
    smoothed_imputations.append(X_knn_unscaled) # Also include baseline KNN

    # Aggregate imputations
    Imps_stack = np.stack(smoothed_imputations, axis=0)
    mean_imp = Imps_stack.mean(axis=0)
    var_imp = Imps_stack.var(axis=0)
    # Restore original observed values
    mean_imp[mask == 1] = X_raw[mask == 1]
    var_imp[mask == 1] = 0.0

    # Save preprocessed data
    preproc_h5_path = args.out_dir / "clinical_preprocessed_advanced.h5"
    print(f"Saving preprocessed data to: {preproc_h5_path}")
    with h5py.File(preproc_h5_path, "w") as f:
        f.create_dataset("patient_id", data=np.array(patient_ids, dtype="S"))
        f.create_dataset("feature_names", data=np.array(feature_names, dtype="S"))
        f.create_dataset("features_mean", data=mean_imp.astype(np.float32))
        f.create_dataset("features_var", data=var_imp.astype(np.float32))
        f.create_dataset("missing_mask", data=mask.astype(np.int8))
        f.create_dataset("surv_5yr_label", data=surv_labels)
        f.create_dataset("rec_2yr_label", data=rec_labels)

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

    print("Evaluating embedding quality...")
    evaluate_embeddings(embeddings, surv_labels, task_name="5-Year Survival")
    evaluate_embeddings(embeddings, rec_labels, task_name="2-Year Recurrence")

    # Save final embeddings
    embed_h5_path = args.out_dir / "clinical_embedding_512.h5"
    print(f"Saving final embeddings to: {embed_h5_path}")
    with h5py.File(embed_h5_path, "w") as f:
        f.create_dataset("patient_id", data=np.array(patient_ids, dtype="S"))
        f.create_dataset("embedding_512", data=embeddings)
        f.create_dataset("surv_5yr_label", data=surv_labels)
        f.create_dataset("rec_2yr_label", data=rec_labels)

    print("\n--- Pipeline Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A unified pipeline for clinical data preprocessing and embedding generation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Input/Output Arguments
    parser.add_argument("--input_json", type=Path, required=True, help="Path to the input clinical_data.json file.")
    parser.add_argument("--out_dir", type=Path, required=True, help="Directory to save all output files.")

    # VAE Imputation Arguments
    parser.add_argument("--no_vae", action="store_true", help="If set, skips VAE imputation and uses only KNN.")
    parser.add_argument("--vae_epochs", type=int, default=60, help="Number of epochs for VAE imputer training.")

    # Embedding Generation Arguments
    parser.add_argument("--embed_mode", choices=["ae", "pca"], default="ae", help="Method for embedding generation: 'ae' (Autoencoder) or 'pca'.")
    parser.add_argument("--embed_epochs", type=int, default=40, help="Number of epochs for Denoising AE training.")

    # General Training Arguments
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size for training both VAE and AE models.")
    parser.add_argument("--learning_rate", type=float, default=1e-3, help="Learning rate for training both VAE and AE models.")

    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    args.out_dir.mkdir(parents=True, exist_ok=True)
    
    main(args)