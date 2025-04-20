---
title: Research Paper Summarization
emoji: 📊
colorFrom: gray
colorTo: indigo
sdk: streamlit
sdk_version: 1.44.1
app_file: app.py
pinned: false
---

A multi-agent AI system that helps researchers, students, and enthusiasts quickly summarize research papers, generate audio podcasts, and discover insights across multiple academic articles.

---

## Demo Video

[Click here to watch the demo video](./demo.webm)

---

## Features

### 1. Multi-modal Research Input
- **Topic Search**: Search academic repositories (Semantic Scholar, arXiv) using a topic.
- **PDF Upload**: Upload research papers for direct summarization.
- **PDF URL**: Provide a URL to a research paper in PDF format.

### 2. Modular Multi-Agent Pipeline
- **Search Agent**: Fetches papers using topic, URL, or upload.
- **Processing Agent**: Extracts text, OCR, and tables from PDFs.
- **Topic Classification Agent**: Classifies paper sections based on a user-defined topic list.
- **Summarizer Agent**: Generates concise summaries using Gemini.
- **Synthesizer Agent**: Creates cross-paper synthesis from multiple papers.
- **Audio Agent**: Converts summaries and syntheses into MP3 format.

### 3. Summary and Podcast Generation
- Generates abstract-style summaries.
- Downloads and plays audio versions of individual and collective summaries.

### 4. Simple UI via Streamlit
- User-friendly frontend to search, upload, summarize, listen, and download.

---

##  Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python (modular agents)
- **LLM**: Google Gemini
- **Embeddings**: None (lightweight summarization)
- **Audio**: gTTS
- **PDF Parsing**: PyMuPDF, pytesseract

---

##  File Structure
```
project-root/
│
├── app.py                           # Streamlit interface
├── pipeline_graph.py               # Controls agent execution
├── requirements.txt
│
├── Agents/
│   ├── search_agent.py             # Handles topic, PDF, and URL fetch
│   ├── processing_agent.py         # Extracts text, tables, OCR
│   ├── topic_classification_agent.py
│   ├── summarizer_agent.py         # Summary + cross-paper synthesis
│   ├── audio_citation_agent.py     # gTTS-based audio generator
│
└── output/                         # Stores generated audio
```

---

## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/Swetha-Creater/Research-Paper-Summarization-Multi-Agent-System.git
cd Research-Paper-Summarization-Multi-Agent-System
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run Locally
```bash
streamlit run app.py
```

---

## Example Use Cases
- Upload a PDF from an academic journal and get a summary with podcast.
- Paste a URL from arXiv and listen to the paper's abstract.
- Search "Generative AI" and synthesize findings from 5 papers.

---

## Paper Processing Methodology
- PDFs are parsed using PyMuPDF for layout-based text and table extraction.
- Embedded images are OCR-processed via Tesseract to extract visual text.
- All extracted content is chunked (800-word max) and processed for summarization.

## Audio Generation Implementation
- Text summaries are passed to gTTS (Google Text-to-Speech) for MP3 audio generation.
- Each paper and synthesis gets a separate downloadable audio file.

## Limitations and Future Improvements
- Limited citation tracing; currently metadata-level only.
- No multilingual or language-detection support.
- Future: add vector-based QA, keyword search within papers, and author-level summarization.

---
