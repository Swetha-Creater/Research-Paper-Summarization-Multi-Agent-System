import fitz  # PyMuPDF
import requests
import tempfile
import os
from PIL import Image
import pytesseract
from bs4 import BeautifulSoup

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

def paper_search_and_discovery_agent(input: dict) -> dict:
    if input.get("pdf_file"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(input["pdf_file"].read())
            file_path = temp.name
        chunks = extract_pdf_with_ocr_and_tables(file_path)
        os.remove(file_path)
        if not chunks:
            return {"mode": "error", "error": "No extractable content found in uploaded PDF."}
        return {
            "mode": "pdf",
            "chunks": chunks,
            "metadata": {
                "title": input.get("topic", "Uploaded Paper"),
                "url": ""
            }
        }

    elif input.get("pdf_url"):
        try:
            chunks = extract_text_from_pdf_url(input["pdf_url"])
            return {
                "mode": "pdf",
                "chunks": chunks,
                "metadata": {
                    "title": input.get("topic", "URL-based PDF"),
                    "url": input["pdf_url"]
                }
            }
        except Exception as e:
            return {"mode": "error", "error": str(e)}

    elif input.get("topic"):
        topic = input["topic"]
        limit = input.get("limit", 5)
        sort = input.get("sort", "relevance")
        s2_results = search_semantic_scholar(topic, limit, sort)
        arxiv_results = search_arxiv(topic, limit)
        papers = s2_results + arxiv_results
        return {"mode": "search", "papers": papers[:limit * 2]}

    return {"mode": "error", "error": "No valid input provided."}

def search_semantic_scholar(query, limit=5, sort="relevance"):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,url,abstract,authors,year,venue",
        "sort": sort
    }
    response = requests.get(url, params=params)
    results = []
    if response.status_code == 200:
        for item in response.json().get("data", []):
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "abstract": item.get("abstract"),
                "authors": [author["name"] for author in item.get("authors", [])],
                "year": item.get("year"),
                "venue": item.get("venue", "N/A"),
                "source": "Semantic Scholar"
            })
    return results

def search_arxiv(query, limit=5):
    search_query = f"search_query=all:{query}&start=0&max_results={limit}"
    response = requests.get(f"http://export.arxiv.org/api/query?{search_query}")
    results = []
    if response.status_code == 200:
        feed = BeautifulSoup(response.content, features="xml")
        for entry in feed.find_all("entry"):
            results.append({
                "title": entry.title.text.strip(),
                "url": entry.id.text.strip(),
                "abstract": entry.summary.text.strip(),
                "authors": [author.find("name").text for author in entry.find_all("author")],
                "year": entry.published.text[:4],
                "venue": "arXiv",
                "source": "arXiv"
            })
    return results
