#!/usr/bin/env python3
"""
spatial.py: A Unified Pipeline for Spatial Histopathology Embedding Generation.

This script provides an end-to-end workflow for processing and aggregating patch-level
whole slide image (WSI) data from HDF5 files into 512-dimensional, patient-level
spatial embeddings. It is designed to be robust, user-friendly, and ready for
integration into larger machine learning packages.

The pipeline features a novel, spatially-aware approach:

1.  **Data Ingestion and Patch Selection**:
    -   Loads patch-level features and coordinates from H5 files across multiple
        user-specified WSI directories.
    -   If a slide contains more patches than a set maximum (e.g., 1024), it uses
        MiniBatchKMeans clustering on both feature and spatial data to select a
        representative subset of patches. This preserves spatial and feature diversity
        while ensuring computational efficiency.

2.  **Spatially-Aware Transformer Aggregation**:
    -   **Feature Projection**: Projects patch features into a 512-d space.
    -   **Spatial Bias Injection**: A positional MLP encodes the (x, y) coordinates of each
        patch, adding a spatial bias to the feature representation. This makes the
        model aware of the tissue architecture.
    -   **Transformer Encoder**: A Transformer with a [CLS] token aggregates information
        across all selected patches to produce a single, global WSI embedding.

3.  **Uncertainty Quantification**:
    -   **Monte-Carlo Dropout**: During inference, the script performs multiple forward
        passes with dropout enabled. This generates a distribution of embeddings, from
        which a mean (the final embedding) and a variance (an uncertainty score) are calculated.

4.  **Output Generation**:
    -   Aggregates multiple WSI embeddings for the same patient (if any) into a single
        patient-level representation.
    -   Saves the final 512-d patient embeddings, variance vectors, and quality scores
        to `spatial_embedding_512.h5`.

Usage:
    python spatial.py --wsi_dirs /path/to/lymph_nodes /path/to/primary_tumor \
                      --dir_names lymph primary \
                      --out_dir /path/to/output_directory --use_gpu
"""

import re
import json
import argparse
import warnings
from pathlib import Path
from collections import defaultdict

import h5py
import joblib
import numpy as np
from tqdm import tqdm

# Machine Learning Imports
from sklearn.cluster import MiniBatchKMeans

# Optional PyTorch Import
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# --- Configuration ---
SEED = 42
DEFAULT_MODEL_DIM = 512
DEVICE = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"

# Set seeds for reproducibility
np.random.seed(SEED)
if TORCH_AVAILABLE:
    torch.manual_seed(SEED)

# Suppress common warnings for cleaner output
warnings.filterwarnings("ignore")


# ---------- PyTorch Model Definitions ----------

if TORCH_AVAILABLE:
    class PatchProjector(nn.Module):
        """Projects high-dimensional patch features to the model's dimension."""
        def __init__(self, feat_dim, model_dim):
            super().__init__()
            self.proj = nn.Sequential(
                nn.Linear(feat_dim, model_dim),
                nn.GELU(),
                nn.LayerNorm(model_dim)
            )
        def forward(self, x): return self.proj(x)

    class PositionalMLP(nn.Module):
        """Encodes 2D coordinates into a spatial bias vector."""
        def __init__(self, model_dim):
            super().__init__()
            self.mlp = nn.Sequential(
                nn.Linear(2, model_dim),
                nn.GELU(),
                nn.Linear(model_dim, model_dim)
            )
        def forward(self, coords_norm): return self.mlp(coords_norm)

    class SpatialTransformerAggregator(nn.Module):
        """Aggregates patch embeddings using a Transformer encoder."""
        def __init__(self, model_dim, n_heads, n_layers, dropout):
            super().__init__()
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=model_dim, nhead=n_heads, dim_feedforward=model_dim * 4,
                dropout=dropout, activation='gelu', batch_first=True
            )
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
            self.cls_token = nn.Parameter(torch.randn(1, 1, model_dim) * 0.02)

        def forward(self, patch_embs):
            # Prepend the [CLS] token to the patch sequence
            cls_tokens = self.cls_token.expand(patch_embs.shape[0], -1, -1)
            x = torch.cat([cls_tokens, patch_embs], dim=1)
            x = self.transformer(x)
            # Return the embedding of the [CLS] token
            return x[:, 0, :]

# ---------- Helper Function Definitions ----------

def load_patch_h5(path):
    """Loads features and coordinates from a patch-level H5 file."""
    try:
        with h5py.File(path, "r") as f:
            # Find feature dataset
            for key in ("features", "feature", "embeddings"):
                if key in f:
                    feats = np.array(f[key], dtype=np.float32)
                    break
            else: return None, None # Could not find features

            # Find coordinate dataset
            for key in ("coords", "coordinates"):
                if key in f:
                    coords = np.array(f[key], dtype=np.float32)
                    break
            else: # Fallback: create dummy grid coordinates if none are found
                coords = np.array(np.meshgrid(np.arange(np.sqrt(feats.shape[0])), np.arange(np.sqrt(feats.shape[0])))).T.reshape(-1, 2)
            return feats, coords
    except Exception as e:
        print(f"Warning: Could not load H5 file {path}. Error: {e}")
        return None, None

def filename_to_patient_id(filename):
    """Extracts a patient ID from a filename using regex."""
    match = re.search(r'(\d+)', Path(filename).stem)
    return match.group(1).zfill(3) if match else Path(filename).stem

# ---------- Main Pipeline ----------

def main(args):
    """Main function to run the complete spatial preprocessing pipeline."""
    print("--- Starting Spatial Data Processing Pipeline ---")

    # --- Stage 1: File Discovery and Data Loading ---
    all_files = []
    for dir_path in args.wsi_dirs:
        if not dir_path.is_dir():
            print(f"Warning: Input directory not found, skipping: {dir_path}")
            continue
        all_files.extend(list(dir_path.glob("*.h5")))

    if not all_files:
        print("Error: No .h5 files found in the specified directories. Exiting.")
        exit(1)

    print(f"Found {len(all_files)} H5 files to process.")
    
    # --- Stage 2: Model Initialization ---
    use_torch = args.use_gpu and TORCH_AVAILABLE
    aggregator, pos_mlp = None, None
    if use_torch:
        print(f"Using PyTorch on device: {DEVICE}")
        aggregator = SpatialTransformerAggregator(
            args.model_dim, args.n_heads, args.n_layers, args.dropout
        ).to(DEVICE)
        pos_mlp = PositionalMLP(args.model_dim).to(DEVICE)
    else:
        print("Running in CPU/fallback mode (no PyTorch). Embeddings will be generated via mean pooling and random projection.")

    # --- Stage 3: Per-Slide Processing and Embedding ---
    slide_results = defaultdict(list)
    
    for h5_path in tqdm(all_files, desc="Processing Slides"):
        feats, coords = load_patch_h5(h5_path)
        if feats is None or feats.shape[0] == 0:
            continue

        # L2 Normalize patch features for stability
        feats /= np.linalg.norm(feats, axis=1, keepdims=True) + 1e-6
        # Min-Max scale coordinates to [0, 1] range
        coords_norm = (coords - coords.min(axis=0)) / (coords.max(axis=0) - coords.min(axis=0) + 1e-6)

        # Patch reduction via clustering if necessary
        if feats.shape[0] > args.max_patches:
            kmeans = MiniBatchKMeans(n_clusters=args.max_patches, random_state=SEED, batch_size=256)
            # Cluster on both features and coordinates to preserve spatial information
            cluster_data = np.hstack([feats, coords_norm])
            kmeans.fit(cluster_data)
            sel_feats = kmeans.cluster_centers_[:, :feats.shape[1]]
            sel_coords = kmeans.cluster_centers_[:, feats.shape[1]:]
        else:
            sel_feats, sel_coords = feats, coords_norm
            
        quality_score = sel_feats.shape[0] / feats.shape[0]

        # Generate embedding for the slide
        if use_torch:
            projector = PatchProjector(sel_feats.shape[1], args.model_dim).to(DEVICE)
            with torch.no_grad():
                patch_embs = projector(torch.from_numpy(sel_feats).float().to(DEVICE))
                pos_bias = pos_mlp(torch.from_numpy(sel_coords).float().to(DEVICE))
                final_embs = (patch_embs + pos_bias).unsqueeze(0)

                # Monte-Carlo Dropout for uncertainty estimation
                aggregator.train() # Enable dropout
                mc_embs = [aggregator(final_embs).cpu().numpy() for _ in range(args.mc_samples)]
                mc_embs = np.vstack(mc_embs)
                mean_emb, var_emb = mc_embs.mean(axis=0), mc_embs.var(axis=0)
        else: # Fallback mode
            rng = np.random.RandomState(SEED)
            proj_matrix = rng.randn(sel_feats.shape[1], args.model_dim).astype(np.float32)
            projected_feats = sel_feats @ proj_matrix
            mean_emb, var_emb = projected_feats.mean(axis=0), projected_feats.var(axis=0)

        pid = filename_to_patient_id(h5_path.name)
        slide_results[pid].append({
            "mean": mean_emb, "var": var_emb, "quality": quality_score
        })

    # --- Stage 4: Aggregate Slide Embeddings to Patient-Level ---
    print("Aggregating slide embeddings to patient-level...")
    patient_ids, embeddings_mean, embeddings_var, quality_scores = [], [], [], []
    for pid, results in slide_results.items():
        # Weighted average of slide embeddings by quality score
        means = np.array([r["mean"] for r in results])
        qualities = np.array([r["quality"] for r in results])
        
        patient_mean = np.average(means, axis=0, weights=qualities)
        # For variance, we take the mean variance (simplification)
        patient_var = np.array([r["var"] for r in results]).mean(axis=0)
        
        patient_ids.append(pid)
        embeddings_mean.append(patient_mean)
        embeddings_var.append(patient_var)
        quality_scores.append(qualities.mean())

    # --- Stage 5: Save Outputs ---
    output_h5_path = args.out_dir / "spatial_embedding_512.h5"
    print(f"Saving final patient embeddings to: {output_h5_path}")
    with h5py.File(output_h5_path, "w") as f:
        f.create_dataset("patient_id", data=np.array(patient_ids, dtype="S"))
        f.create_dataset("embedding_mean_512", data=np.array(embeddings_mean, dtype=np.float32))
        f.create_dataset("embedding_var_512", data=np.array(embeddings_var, dtype=np.float32))
        f.create_dataset("quality_score", data=np.array(quality_scores, dtype=np.float32))

    print("\n--- Pipeline Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A unified pipeline for spatial histopathology embedding generation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--wsi_dirs", type=Path, required=True, nargs='+',
                        help="One or more paths to directories containing WSI .h5 files.")
    parser.add_argument("--out_dir", type=Path, required=True,
                        help="Directory to save the final HDF5 embedding file.")
    parser.add_argument("--max_patches", type=int, default=1024,
                        help="Maximum number of patches to use per slide before clustering.")
    parser.add_argument("--model_dim", type=int, default=DEFAULT_MODEL_DIM,
                        help="The dimension of the internal transformer models and final embeddings.")
    parser.add_argument("--n_layers", type=int, default=4, help="Number of layers in the Transformer encoder.")
    parser.add_argument("--n_heads", type=int, default=8, help="Number of attention heads in the Transformer.")
    parser.add_argument("--dropout", type=float, default=0.1, help="Dropout rate for the Transformer.")
    parser.add_argument("--mc_samples", type=int, default=16,
                        help="Number of Monte-Carlo samples for uncertainty estimation.")
    parser.add_argument("--use_gpu", action="store_true",
                        help="If set, attempts to use a GPU for processing (requires PyTorch).")

    args = parser.parse_args()

    if args.use_gpu and not TORCH_AVAILABLE:
        print("Warning: --use_gpu was specified, but 'torch' is not installed. Running in CPU mode.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    main(args)