import fitz  # PyMuPDF
import requests
import tempfile
import os
from PIL import Image
import pytesseract
import re


def chunk_text(text, max_length=800):
    words = text.split()
    chunks, chunk = [], []
    for word in words:
        if len(" ".join(chunk + [word])) <= max_length:
            chunk.append(word)
        else:
            chunks.append(" ".join(chunk))
            chunk = [word]
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks


def extract_pdf_with_ocr_and_tables(file_path):
    text_blocks, ocr_blocks, table_blocks = [], [], []

    with fitz.open(file_path) as doc:
        for i, page in enumerate(doc):
            page_number = i + 1

            # --- Text Extraction ---
            text = page.get_text()
            if text.strip():
                for idx, chunk in enumerate(chunk_text(text.strip())):
                    text_blocks.append({
                        "type": "text",
                        "page": page_number,
                        "chunk_id": f"text_{page_number}_{idx}",
                        "content": chunk
                    })

            # --- OCR from Images ---
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]
                img_path = os.path.join(tempfile.gettempdir(), f"page_{page_number}_img_{img_index}.{ext}")

                with open(img_path, "wb") as img_file:
                    img_file.write(image_bytes)

                try:
                    image = Image.open(img_path)
                    ocr_text = pytesseract.image_to_string(image)
                    if ocr_text.strip():
                        ocr_blocks.append({
                            "type": "image_ocr",
                            "page": page_number,
                            "chunk_id": f"ocr_{page_number}_{img_index}",
                            "content": ocr_text.strip(),
                            "image_path": img_path
                        })
                except Exception as e:
                    print("OCR error:", e)

            # --- Table-like Layout Extraction ---
            dict_layout = page.get_text("dict")
            for b in dict_layout.get("blocks", []):
                if b["type"] == 5:
                    rows = []
                    for line in b.get("lines", []):
                        row_text = " | ".join(span["text"] for span in line["spans"]).strip()
                        if row_text:
                            rows.append(row_text)
                    if len(rows) >= 2:
                        table_blocks.append({
                            "type": "table",
                            "page": page_number,
                            "chunk_id": f"table_{page_number}_{len(table_blocks)}",
                            "content": "\n".join(rows)
                        })

    print(f"✅ Extracted: {len(text_blocks)} text chunks, {len(table_blocks)} tables, {len(ocr_blocks)} OCR chunks")
    return text_blocks + table_blocks + ocr_blocks


def extract_text_from_pdf_url(url):
    response = requests.get(url)
    if response.status_code == 200 and "pdf" in response.headers.get("Content-Type", "").lower():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        chunks = extract_pdf_with_ocr_and_tables(tmp_path)
        os.remove(tmp_path)
        return chunks
    else:
        raise ValueError("Invalid PDF URL or content-type.")


# --- Additional Utilities ---

def classify_topic(text: str, topic_list: list[str]) -> str:
    text_lower = text.lower()
    for topic in topic_list:
        if topic.lower() in text_lower:
            return topic
    return "Uncategorized"


def extract_key_phrases(text: str) -> list[str]:
    phrases = re.findall(r"(?:we propose|we present|we introduce|this paper (?:proposes|presents))(.{0,150})", text, re.IGNORECASE)
    phrases += re.findall(r"(?:method|model|approach) called ([A-Z][A-Za-z0-9_\-]{2,})", text)
    return [p.strip() for p in phrases]


def paper_processing_and_extraction_agent(input: dict) -> dict:
    chunks = input.get("chunks", [])
    topic_list = input.get("topic_list", [])

    classified_chunks = []
    text_chunks, table_chunks, ocr_chunks = [], [], []
    key_phrases_all = []

    for chunk in chunks:
        content = chunk.get("content", "")
        chunk_type = chunk.get("type", "text")

        # Topic classification
        if topic_list:
            topic = classify_topic(content, topic_list)
            chunk["classified_topic"] = topic

        # Key phrase extraction (only for text)
        if chunk_type == "text":
            key_phrases = extract_key_phrases(content)
            if key_phrases:
                chunk["key_phrases"] = key_phrases
                key_phrases_all.extend(key_phrases)

        # Categorize by type
        if chunk_type == "text":
            text_chunks.append(chunk)
        elif chunk_type == "table":
            table_chunks.append(chunk)
        elif chunk_type == "image_ocr":
            ocr_chunks.append(chunk)

        classified_chunks.append(chunk)

    return {
        "classified_chunks": classified_chunks,
        "segmented": {
            "text": text_chunks,
            "tables": table_chunks,
            "ocr": ocr_chunks
        },
        "key_phrases": list(set(key_phrases_all))
    }
