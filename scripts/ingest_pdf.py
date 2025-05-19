import json
import os
from utils.pdf_extractor import save_extracted_text
from utils.metadata_tagger import tag_chunks_with_metadata

def main(input_list_path):
    with open(input_list_path, "r", encoding="utf-8") as f:
        pdf_dict = json.load(f)

    for pdf_path, title in pdf_dict.items():
        if not os.path.exists(pdf_path):
            print(f"[✗] File not found: {pdf_path}")
            continue

        print(f"[→] Processing: {pdf_path}  Title: {title}")
        
        try:
            # Step 1: Extract raw text per page
            json_path = save_extracted_text(pdf_path, "data/extracted_texts")

            # Step 2: Chunk + tag metadata
            base_name = title or os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = f"data/chunks/{base_name}_chunks.jsonl"

            tag_chunks_with_metadata(
                input_json_path=json_path,
                output_jsonl_path=output_path,
                doc_title=base_name
            )

            print(f"[✓] Done: {output_path}")
        except Exception as e:
            print(f"[✗] Failed to process {pdf_path}: {str(e)}")

if __name__ == "__main__":
    main("data/input_list.json")
