import os
import json
import uuid
import argparse
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# === Load and Merge Chunks ===
def load_chunks(jsonl_path):
    chunks = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line.strip()))
    return chunks

def merge_chunks(chunks, max_tokens=150):
    merged = []
    buffer = []
    token_count = 0

    for chunk in chunks:
        chunk_tokens = len(chunk["text"].split())
        if token_count + chunk_tokens > max_tokens:
            merged_text = " ".join(c["text"] for c in buffer)
            merged.append({
                "id": str(uuid.uuid4()),
                "title": buffer[0]["title"],
                "page": buffer[0]["page"],
                "section": buffer[0]["section"],
                "text": merged_text
            })
            buffer = []
            token_count = 0
        buffer.append(chunk)
        token_count += chunk_tokens

    if buffer:
        merged_text = " ".join(c["text"] for c in buffer)
        merged.append({
            "id": str(uuid.uuid4()),
            "title": buffer[0]["title"],
            "page": buffer[0]["page"],
            "section": buffer[0]["section"],
            "text": merged_text
        })

    return merged

def save_jsonl(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"[✓] Saved merged chunks to {path}")

# === Embedding and FAISS ===
def embed_texts(texts, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    return model.encode(texts, convert_to_numpy=True)

def build_faiss_index(embeddings, index_path):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    print(f"[✓] FAISS index saved to {index_path}")

# === Main Pipeline ===
def main(input_chunks, output_jsonl, faiss_index):
    chunks = load_chunks(input_chunks)
    merged_chunks = merge_chunks(chunks)
    save_jsonl(merged_chunks, output_jsonl)

    texts = [c["text"] for c in merged_chunks]
    embeddings = embed_texts(texts)
    build_faiss_index(embeddings, faiss_index)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build FAISS index from document chunks")
    parser.add_argument("--input_chunks", required=True, help="Path to .jsonl chunked input")
    parser.add_argument("--output_jsonl", required=True, help="Path to save merged .jsonl")
    parser.add_argument("--faiss_index", required=True, help="Path to save FAISS index")
    args = parser.parse_args()

    main(args.input_chunks, args.output_jsonl, args.faiss_index)
