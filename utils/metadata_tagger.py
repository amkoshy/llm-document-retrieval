# utils/metadata_tagger.py

import json
import uuid
import os

def detect_section_heading(line):
    return line.isupper() and len(line.split()) < 10

def tag_chunks_with_metadata(input_json_path, output_jsonl_path, doc_title):
    with open(input_json_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    chunks = []
    for page in pages:
        lines = [line.strip() for line in page["text"].split("\n") if line.strip()]
        current_section = "Introduction"
        for line in lines:
            if detect_section_heading(line):
                current_section = line.strip()
                continue
            chunk = {
                "id": str(uuid.uuid4()),
                "title": doc_title,
                "page": page["page"],
                "section": current_section,
                "text": line
            }
            chunks.append(chunk)

    with open(output_jsonl_path, "w", encoding="utf-8") as out_file:
        for chunk in chunks:
            out_file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"[✓] Metadata-tagged chunks saved to {output_jsonl_path}")
    return output_jsonl_path
