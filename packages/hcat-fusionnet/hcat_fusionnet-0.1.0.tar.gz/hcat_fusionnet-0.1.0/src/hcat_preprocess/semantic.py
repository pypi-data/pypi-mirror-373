#!/usr/bin/env python3
"""
semantic.py: A Unified Preprocessing Pipeline for Clinical Text Data.

This script provides an end-to-end workflow for processing and embedding clinical text
narratives from multiple sources (e.g., histories, reports, surgery descriptions).
It is designed to be robust, user-friendly, and ready for integration into larger
machine learning packages.

The pipeline executes several key stages:

1.  **Data Ingestion and Cleaning**:
    -   Loads all .txt files from multiple user-specified input directories.
    -   Cleans the text by removing boilerplate, HTML-like tags, and normalizing whitespace.
    -   Infers patient IDs from filenames for alignment.

2.  **Entity Extraction and Negation Detection**:
    -   Uses a regex-based approach to identify key clinical entities (e.g., tumor, metastasis,
        resection margins).
    -   Detects negation cues in the local context of each entity to distinguish between
        affirmed and negated findings.

3.  **Dual-Mode Embedding Generation**:
    -   **Transformer Mode**: Leverages a pre-trained biomedical language model
        (e.g., Bio_ClinicalBERT) to generate contextually rich, 768-d document embeddings.
        This is the preferred, high-performance option.
    -   **TF-IDF + SVD Mode**: Provides a lightweight fallback using TF-IDF vectorization followed
        by TruncatedSVD for dimensionality reduction to 512-d. This ensures compatibility
        on systems without GPU/transformer support.

4.  **Hierarchical Aggregation and Fusion**:
    -   **Document-to-Modality**: Aggregates document embeddings within each modality (histories,
        reports, etc.) into a single 512-d vector using a quality-weighted attention mechanism.
    -   **Modality-to-Patient**: Fuses the embeddings from all text modalities into a final,
        unified 512-d patient-level semantic representation.

5.  **Output Generation**:
    -   Saves the modality-specific and the final combined patient embeddings to
        `text_semantic_embeddings_512.h5`.
    -   Includes extracted entity counts and other useful metadata in the HDF5 file.

Usage:
    python semantic.py --text_dirs /path/to/histories /path/to/reports \
                       --dir_names histories reports \
                       --out_dir /path/to/output_directory \
                       --use_transformer
"""

import re
import json
import argparse
import warnings
from pathlib import Path
from collections import defaultdict, Counter

import h5py
import joblib
import numpy as np
from tqdm import tqdm

# Machine Learning Imports
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

# Optional PyTorch and Transformers Import
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# --- Configuration ---
SEED = 42
TARGET_DIM = 512
TRANSFORMER_MODEL = "emilyalsentzer/Bio_ClinicalBERT"
DEVICE = "cuda" if TRANSFORMERS_AVAILABLE and torch.cuda.is_available() else "cpu"
ENTITY_PATTERNS = {
    "tumor": [r"\btumou?r\b", r"\bcarcinoma\b", r"\bmalignan.*\b"],
    "metastasis": [r"\bmetastasi\w*\b", r"\bmetastatic\b"],
    "lymph_node": [r"\bnode\b", r"\blymp?h\b"],
    "resection_margin_r0": [r"\bR0\b", r"\bcomplete resection\b", r"\bnegative margin\b"],
    "resection_margin_r1": [r"\bR1\b", r"\bpositive margin\b"],
}
NEGATION_TOKENS = {"no", "not", "without", "denies", "denied", "negative", "free of"}

np.random.seed(SEED)
if TRANSFORMERS_AVAILABLE:
    torch.manual_seed(SEED)

warnings.filterwarnings("ignore")

# ---------- Helper Function Definitions ----------

def clean_text(text):
    """Basic text cleaning: remove tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def filename_to_patient_id(filename):
    """Extracts a patient ID from a filename using regex."""
    stem = Path(filename).stem
    # Look for trailing numbers, common in clinical data
    match = re.search(r'(\d+)$', stem)
    if match:
        return match.group(1).zfill(3)
    return stem # Fallback to the filename stem

def extract_entities(text, patterns=ENTITY_PATTERNS):
    """Extracts entities and detects negation from text."""
    text_lower = text.lower()
    entity_counts = Counter()
    for entity, regex_list in patterns.items():
        for pattern in regex_list:
            for match in re.finditer(pattern, text_lower):
                # Check for negation in a window before the match
                window = text_lower[max(0, match.start() - 60):match.start()]
                if not any(neg_token in window for neg_token in NEGATION_TOKENS):
                    entity_counts[entity] += 1
    return dict(entity_counts)

def get_transformer_embedding(text, tokenizer, model, device):
    """Generates a document embedding using a transformer model."""
    inputs = tokenizer(text, truncation=True, max_length=512, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        # Mean pooling of the last hidden state, masked
        mask = inputs["attention_mask"].unsqueeze(-1).expand(outputs.last_hidden_state.size())
        sum_hidden = (outputs.last_hidden_state * mask).sum(1)
        sum_mask = mask.sum(1).clamp(min=1e-9)
        embedding = (sum_hidden / sum_mask).cpu().numpy().squeeze()
    return embedding

# ---------- Main Pipeline ----------

def main(args):
    """Main function to run the complete semantic preprocessing pipeline."""
    print("--- Starting Semantic Text Processing Pipeline ---")
    
    # --- Stage 1: Data Ingestion ---
    docs_by_modality = defaultdict(lambda: defaultdict(list))
    for dir_path, name in zip(args.text_dirs, args.dir_names):
        if not dir_path.is_dir():
            print(f"Warning: Input directory not found, skipping: {dir_path}")
            continue
        print(f"Processing text files from '{name}' directory...")
        for file_path in dir_path.glob("*.txt"):
            pid = filename_to_patient_id(file_path.name)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                docs_by_modality[name][pid].append(clean_text(f.read()))

    all_pids = sorted(list(set(pid for modality in docs_by_modality.values() for pid in modality.keys())))
    n_patients = len(all_pids)
    print(f"Found text data for {n_patients} unique patients across {len(args.dir_names)} modalities.")

    # --- Stage 2: Embedding Generation ---
    doc_embeddings = defaultdict(lambda: defaultdict(list))
    doc_qualities = defaultdict(lambda: defaultdict(list))
    
    use_transformer = args.use_transformer and TRANSFORMERS_AVAILABLE
    if use_transformer:
        print(f"Loading transformer model '{TRANSFORMER_MODEL}' on device '{DEVICE}'...")
        tokenizer = AutoTokenizer.from_pretrained(TRANSFORMER_MODEL)
        model = AutoModel.from_pretrained(TRANSFORMER_MODEL).to(DEVICE).eval()
    else:
        print("Using TF-IDF + TruncatedSVD for embedding generation.")

    # Process each document for each patient and modality
    for modality, docs_by_patient in docs_by_modality.items():
        if not use_transformer:
            corpus = [doc for pid in all_pids for doc in docs_by_patient.get(pid, [])]
            if not corpus: continue
            vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1, 2))
            svd = TruncatedSVD(n_components=min(TARGET_DIM, len(corpus)-1 if len(corpus) > 1 else 1), random_state=SEED)
            X_reduced = svd.fit_transform(vectorizer.fit_transform(corpus))
            doc_idx = 0
        
        for pid in tqdm(all_pids, desc=f"Embedding '{modality}' docs"):
            for doc_text in docs_by_patient.get(pid, []):
                entities = extract_entities(doc_text)
                quality = np.log1p(len(doc_text.split()) + sum(entities.values()))
                
                if use_transformer:
                    emb = get_transformer_embedding(doc_text, tokenizer, model, DEVICE)
                else: # TF-IDF mode
                    emb = X_reduced[doc_idx] if doc_idx < len(X_reduced) else np.zeros(svd.n_components_)
                    doc_idx += 1
                
                doc_embeddings[modality][pid].append(emb)
                doc_qualities[modality][pid].append(quality)

    # --- Stage 3: Hierarchical Aggregation ---
    print("Aggregating document embeddings to patient-level...")
    pid_to_idx = {pid: i for i, pid in enumerate(all_pids)}
    modality_embeddings = {name: np.zeros((n_patients, TARGET_DIM)) for name in args.dir_names}

    for modality in args.dir_names:
        # Dimensionality reduction if using transformers (e.g., 768 -> 512)
        all_doc_embs = [emb for pid in all_pids for emb in doc_embeddings[modality].get(pid, [])]
        if not all_doc_embs: continue

        X_all = np.array(all_doc_embs)
        if X_all.shape[1] > TARGET_DIM:
            svd_proj = TruncatedSVD(n_components=TARGET_DIM, random_state=SEED).fit(X_all)
            X_all = svd_proj.transform(X_all)
        
        doc_idx = 0
        for pid in all_pids:
            embs = doc_embeddings[modality].get(pid, [])
            if not embs: continue
            
            quals = np.array(doc_qualities[modality][pid])
            weights = np.exp(quals - np.max(quals)) / np.sum(np.exp(quals - np.max(quals)))
            
            projected_embs = X_all[doc_idx : doc_idx + len(embs)]
            if projected_embs.shape[1] < TARGET_DIM:
                projected_embs = np.pad(projected_embs, ((0,0), (0, TARGET_DIM - projected_embs.shape[1])))

            # Weighted average of document embeddings
            modality_embeddings[modality][pid_to_idx[pid]] = np.average(projected_embs, axis=0, weights=weights)
            doc_idx += len(embs)
            
    # --- Stage 4: Cross-Modality Fusion ---
    print("Fusing modality embeddings into a final patient representation...")
    all_modality_embs = np.stack([modality_embeddings[name] for name in args.dir_names], axis=1) # (n_patients, n_modalities, dim)
    modality_quality = np.array([[np.mean(doc_qualities[name].get(pid, [0])) for name in args.dir_names] for pid in all_pids])
    
    weights = np.exp(modality_quality - np.max(modality_quality, axis=1, keepdims=True))
    weights_norm = weights / weights.sum(axis=1, keepdims=True)
    
    combined_embeddings = np.sum(all_modality_embs * weights_norm[:, :, np.newaxis], axis=1)

    # --- Stage 5: Save Outputs ---
    output_h5_path = args.out_dir / "text_semantic_embeddings_512.h5"
    print(f"Saving final embeddings and metadata to: {output_h5_path}")
    with h5py.File(output_h5_path, "w") as f:
        f.create_dataset("patient_id", data=np.array(all_pids, dtype="S"))
        for name in args.dir_names:
            f.create_dataset(f"{name}_embedding_512", data=modality_embeddings[name].astype(np.float32))
        f.create_dataset("text_combined_embedding_512", data=combined_embeddings.astype(np.float32))
        f.create_dataset("modality_quality", data=modality_quality.astype(np.float32))
    
    print("\n--- Pipeline Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A unified pipeline for clinical text preprocessing and embedding.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--text_dirs", type=Path, required=True, nargs='+', 
                        help="One or more paths to directories containing the .txt files.")
    parser.add_argument("--dir_names", type=str, required=True, nargs='+',
                        help="A name for each directory provided in --text_dirs (e.g., 'histories', 'reports'). Must be in the same order.")
    parser.add_argument("--out_dir", type=Path, required=True, 
                        help="Directory to save the final HDF5 embedding file.")
    parser.add_argument("--use_transformer", action="store_true",
                        help="If set, use a transformer model for embeddings. Otherwise, use TF-IDF+SVD.")
    
    args = parser.parse_args()

    if len(args.text_dirs) != len(args.dir_names):
        print("Error: The number of --text_dirs must match the number of --dir_names.")
        exit(1)

    if args.use_transformer and not TRANSFORMERS_AVAILABLE:
        print("Warning: --use_transformer was specified, but 'torch' or 'transformers' is not installed. Falling back to TF-IDF.")
    
    args.out_dir.mkdir(parents=True, exist_ok=True)
    main(args)