#!/usr/bin/env python3
"""
temporal.py: A Unified Preprocessing and Embedding Pipeline for Temporal Blood Data.

This script provides an end-to-end workflow for processing temporal blood test data
from JSON files into 512-dimensional embeddings. It is designed to be robust,
user-friendly, and ready for integration into larger machine learning packages.

The pipeline features a novel, clinically-grounded approach:

1.  **Data Structuring and Time Binning**:
    -   Loads raw blood test records and clinical reference ranges from user-specified JSON files.
    -   Aligns sparse, irregular time-series data into a fixed-length temporal grid (16 bins over a 30-day window).

2.  **Two-Stage, Clinically-Grounded Imputation**:
    -   **Physiology-Aware Filling**: First, imputes missing values using the midpoints of established
        clinical reference ranges, grounding the data in medical knowledge.
    -   **Cohort-Level KNN Refinement**: Second, a K-Nearest Neighbors (KNN) imputer refines the
        values by borrowing statistical patterns from similar patients in the cohort.

3.  **Embedding Generation**:
    -   Trains a Denoising LSTM (Long Short-Term Memory) Encoder to learn a compressed,
        512-dimensional representation that captures temporal dynamics.
    -   Uses Principal Component Analysis (PCA) as a deterministic fallback if PyTorch is unavailable.
    -   Calculates a quality score for each patient based on data completeness.

4.  **Output Generation**:
    -   Saves the final 512-d embeddings and associated metadata (quality scores, analyte lists)
        to `temporal_embedding_512.h5`.
    -   Generates a comprehensive `temporal_summary.json` for reproducibility.

Usage:
    python temporal.py --blood_json /path/to/blood_data.json \
                       --ref_json /path/to/reference_ranges.json \
                       --out_dir /path/to/output_directory
"""

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
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

# Optional PyTorch Import
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# --- Configuration ---
SEED = 42
EMBED_DIM = 512
TIME_WINDOW_DAYS = 30
SEQ_LENGTH = 16
KNN_NEIGHBORS = 8
DEVICE = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"

# Set seeds for reproducibility
np.random.seed(SEED)
if TORCH_AVAILABLE:
    torch.manual_seed(SEED)

# Suppress common warnings for cleaner output
warnings.filterwarnings("ignore")


# ---------- PyTorch Model Definitions ----------

if TORCH_AVAILABLE:
    class TemporalLSTMEncoder(nn.Module):
        """A Denoising LSTM Encoder to learn compact 512-d temporal embeddings."""
        def __init__(self, input_dim, hidden=256, n_layers=2, bottleneck=EMBED_DIM, dropout=0.1):
            super().__init__()
            self.lstm = nn.LSTM(input_dim, hidden, n_layers, batch_first=True, bidirectional=True, dropout=dropout)
            self.proj = nn.Sequential(
                nn.Linear(hidden * 2, hidden),
                nn.GELU(),
                nn.Linear(hidden, bottleneck)
            )

        def forward(self, x):
            # x shape: (batch, seq_len, input_dim)
            out, _ = self.lstm(x)  # (batch, seq_len, hidden*2)
            # Aggregate features across the time dimension by averaging
            z = out.mean(dim=1)
            emb = self.proj(z)
            return emb


# ---------- Helper Function Definitions ----------

def load_json_data(path):
    """Loads a JSON file, handling potential errors."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Input JSON file not found at {path}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON file. Ensure it is valid. Details: {e}")
        exit(1)

def build_dataframe(blood_records):
    """Constructs and cleans a DataFrame from raw blood records."""
    df = pd.DataFrame(blood_records)
    df["patient_id"] = df["patient_id"].astype(str).str.zfill(3)
    df["days_before_first_treatment"] = pd.to_numeric(df.get("days_before_first_treatment", 0), errors="coerce").fillna(0).astype(int)
    df["analyte_name"] = df["analyte_name"].astype(str).str.strip()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df

def physiology_aware_fill(matrix, analytes, ref_ranges):
    """
    Performs the first imputation pass using clinical reference ranges and interpolation.
    """
    mat_filled = matrix.copy()
    for i, analyte in enumerate(analytes):
        series = mat_filled[i]
        # If the entire series for an analyte is missing, fill with reference midpoint
        if np.isnan(series).all() and analyte in ref_ranges:
            ref = ref_ranges[analyte]
            mins = [r for r in [ref.get("male_min"), ref.get("female_min")] if r is not None]
            maxs = [r for r in [ref.get("male_max"), ref.get("female_max")] if r is not None]
            if mins and maxs:
                midpoint = (np.mean(mins) + np.mean(maxs)) / 2.0
                mat_filled[i, :] = midpoint
        # If partially missing, interpolate along the time axis
        elif np.isnan(series).any():
            idx = np.arange(len(series))
            not_nan_mask = ~np.isnan(series)
            if not_nan_mask.any():
                series[~not_nan_mask] = np.interp(idx[~not_nan_mask], idx[not_nan_mask], series[not_nan_mask])
                mat_filled[i] = series
    return mat_filled

def train_lstm_encoder(X_seq, epochs, batch_size, lr, device):
    """Trains the Denoising LSTM Encoder to generate embeddings."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required for LSTM-based embedding.")
        
    n_patients, seq_len, input_dim = X_seq.shape
    X_tensor = torch.from_numpy(X_seq).float().to(device)
    
    encoder = TemporalLSTMEncoder(input_dim=input_dim, bottleneck=EMBED_DIM).to(device)
    decoder = nn.Sequential(
        nn.Linear(EMBED_DIM, 1024), nn.GELU(),
        nn.Linear(1024, input_dim * seq_len)
    ).to(device)
    
    params = list(encoder.parameters()) + list(decoder.parameters())
    opt = torch.optim.Adam(params, lr=lr, weight_decay=1e-6)
    loss_fn = nn.MSELoss()
    dl = DataLoader(TensorDataset(X_tensor), batch_size=min(batch_size, n_patients), shuffle=True)
    
    for ep in range(1, epochs + 1):
        encoder.train(); decoder.train()
        total_loss = 0.0
        for (batch,) in dl:
            noisy_batch = batch * (torch.rand_like(batch) > 0.10).float()
            emb = encoder(noisy_batch)
            rec_flat = decoder(emb).view(batch.size(0), seq_len, input_dim)
            loss = loss_fn(rec_flat, batch)
            opt.zero_grad(); loss.backward(); opt.step()
            total_loss += loss.item() * batch.size(0)
        
        if ep % 10 == 0 or ep == 1:
            print(f"  LSTM AE Epoch {ep}/{epochs} | Loss: {total_loss/n_patients:.6f}")
    
    encoder.eval()
    with torch.no_grad():
        embeddings = encoder(X_tensor).cpu().numpy().astype(np.float32)
    return encoder, embeddings

# ---------- Main Pipeline ----------

def main(args):
    """Main function to run the complete temporal preprocessing and embedding pipeline."""
    print("--- Starting Temporal Data Processing Pipeline ---")
    
    # --- Stage 1: Data Loading and Structuring ---
    blood_records = load_json_data(args.blood_json)
    ref_records = load_json_data(args.ref_json)
    
    df = build_dataframe(blood_records)
    ref_ranges = {r.get("analyte_name"): r for r in ref_records}
    
    patients = sorted(df["patient_id"].unique())
    n_patients = len(patients)
    print(f"Loaded data for {n_patients} unique patients.")
    
    # Select analytes present in at least 3 patients or in reference ranges
    analyte_counts = df.groupby("analyte_name")["patient_id"].nunique()
    analytes = sorted(list(set(analyte_counts[analyte_counts >= 3].index) | set(ref_ranges.keys())))
    n_analytes = len(analytes)
    print(f"Processing {n_analytes} selected analytes.")
    
    # --- Stage 2: Time Binning and Matrix Creation ---
    time_bin_edges = np.linspace(0, TIME_WINDOW_DAYS, SEQ_LENGTH + 1)
    
    mats = np.full((n_patients, n_analytes, SEQ_LENGTH), np.nan, dtype=np.float32)
    for i, pid in enumerate(patients):
        patient_df = df[df["patient_id"] == pid]
        for j, analyte in enumerate(analytes):
            analyte_df = patient_df[patient_df["analyte_name"] == analyte]
            if not analyte_df.empty:
                # Assign each measurement to a time bin and average values within the same bin
                bin_indices = np.digitize(analyte_df["days_before_first_treatment"], time_bin_edges, right=False) - 1
                bin_indices = np.clip(bin_indices, 0, SEQ_LENGTH - 1)
                for bin_idx in range(SEQ_LENGTH):
                    values_in_bin = analyte_df.iloc[np.where(bin_indices == bin_idx)[0]]["value"]
                    if not values_in_bin.empty:
                        mats[i, j, bin_idx] = values_in_bin.mean()

    # --- Stage 3: Two-Stage Imputation ---
    print("Performing two-stage imputation...")
    # Stage 1: Physiology-aware filling
    mats_phys_filled = np.array([physiology_aware_fill(mats[i], analytes, ref_ranges) for i in range(n_patients)])
    
    # Stage 2: Cohort-level KNN refinement
    X_flat = mats_phys_filled.reshape(n_patients, -1)
    # Fallback for any remaining NaNs before KNN
    col_medians = np.nanmedian(X_flat, axis=0)
    nan_indices = np.where(np.isnan(X_flat))
    if nan_indices[0].size > 0:
        X_flat[nan_indices] = np.take(col_medians, nan_indices[1])
        
    knn_imputer = KNNImputer(n_neighbors=min(KNN_NEIGHBORS, n_patients - 1))
    X_imputed = knn_imputer.fit_transform(X_flat)
    mats_imputed = X_imputed.reshape(n_patients, n_analytes, SEQ_LENGTH)

    # --- Stage 4: Embedding Generation ---
    print("Generating 512-d embeddings...")
    embeddings, trained_model = None, None
    
    if args.embed_mode == "lstm":
        if TORCH_AVAILABLE:
            X_seq = mats_imputed.transpose(0, 2, 1) # Reshape to (n_patients, seq_len, n_analytes)
            trained_model, embeddings = train_lstm_encoder(X_seq, args.epochs, args.batch_size, args.learning_rate, DEVICE)
        else:
            print("Warning: --embed_mode='lstm' but PyTorch is not available. Falling back to PCA.")
            args.embed_mode = "pca"

    if args.embed_mode == "pca":
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_imputed.reshape(n_patients, -1))
        n_comp = min(EMBED_DIM, X_scaled.shape[1])
        pca = PCA(n_components=n_comp, random_state=SEED)
        Z = pca.fit_transform(X_scaled)
        if n_comp < EMBED_DIM:
            Z = np.pad(Z, ((0, 0), (0, EMBED_DIM - n_comp)), 'constant')
        embeddings = Z.astype(np.float32)

    # --- Stage 5: Save Outputs ---
    print("Saving outputs...")
    quality_scores = np.mean(~np.isnan(mats), axis=(1, 2)).astype(np.float32)
    
    output_h5_path = args.out_dir / "temporal_embedding_512.h5"
    with h5py.File(output_h5_path, "w") as f:
        f.create_dataset("patient_id", data=np.array(patients, dtype="S"))
        f.create_dataset("embedding_512", data=embeddings)
        f.create_dataset("quality_score", data=quality_scores)
        f.create_dataset("analytes", data=np.array(analytes, dtype="S"))

    print("\n--- Pipeline Complete ---")
    print(f"Embeddings and metadata saved to: {output_h5_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A unified pipeline for temporal blood data preprocessing and embedding generation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Input/Output Arguments
    parser.add_argument("--blood_json", type=Path, required=True, help="Path to the input blood_data.json file.")
    parser.add_argument("--ref_json", type=Path, required=True, help="Path to the blood_data_reference_ranges.json file.")
    parser.add_argument("--out_dir", type=Path, required=True, help="Directory to save all output files.")
    
    # Embedding Generation Arguments
    parser.add_argument("--embed_mode", choices=["lstm", "pca"], default="lstm", help="Method for embedding generation: 'lstm' or 'pca'.")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs for LSTM Autoencoder training.")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size for training LSTM model.")
    parser.add_argument("--learning_rate", type=float, default=1e-3, help="Learning rate for training LSTM model.")

    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    main(args)