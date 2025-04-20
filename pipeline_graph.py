from Agents.search_agent import paper_search_and_discovery_agent
from Agents.processing_agent import paper_processing_and_extraction_agent
from Agents.topic_classification_agent import topic_classification_agent
from Agents.summarizer_agent import summarizer_agent, synthesizer_agent
from Agents.audio_citation_agent import summary_audio_agent


def run_pipeline(input_data: dict) -> dict:
    # Step 1: Fetch papers (by topic, DOI, PDF, or URL)
    input_data["fetched"] = paper_search_and_discovery_agent(input_data)

    # --- MODE: PDF --- (Uploaded File or URL)
    if input_data["fetched"].get("mode") == "pdf":
        chunks = input_data["fetched"].get("classified_chunks", []) or input_data["fetched"].get("chunks", [])
        input_data["processed"] = paper_processing_and_extraction_agent({
            "chunks": chunks,
            "topic_list": input_data.get("topic_list", [])
        })

        # Topic classification
        items = [
            {"id": c["chunk_id"], "text": c["content"]}
            for c in input_data["processed"]["classified_chunks"]
        ]
        input_data["classified"] = topic_classification_agent({
            "items": items,
            "topic_list": input_data.get("topic_list", [])
        })["classified"]

        # Summarization (fallback to OCR chunks if no text found)
        text_chunks = input_data["processed"]["segmented"].get("text", [])
        if not text_chunks:
            text_chunks = input_data["processed"]["segmented"].get("ocr", [])

        input_data["summary"] = summarizer_agent({"chunks": text_chunks})

        # 🎷 Generate audio summary (English)
        summary_text = input_data["summary"].get("summary_text", "")
        if summary_text.strip():
            metadata = input_data["fetched"].get("metadata", {
                "title": input_data.get("topic", "Untitled"),
                "authors": ["Unknown"],
                "doi": "",
                "source": ""
            })
            input_data["audio"] = summary_audio_agent({
                "text": summary_text,
                "filename": metadata["title"].replace(" ", "_"),
                "language": "en"
            })
        else:
            input_data["audio"] = {"status": "error", "error": "Summary text is empty."}

    # --- MODE: SEARCH (Topic-based search across multiple papers)
    elif input_data["fetched"].get("mode") == "search":
        papers = input_data["fetched"].get("papers", [])
        paper_summaries = [
            paper.get("abstract", "") or "" 
            for paper in papers 
            if (paper.get("abstract") or "").strip()
        ]
        input_data["summaries"] = paper_summaries

        # 📄 Individual summary audio per paper
        input_data["individual_audios"] = []
        for i, (paper, summary) in enumerate(zip(papers, paper_summaries)):
            audio_result = summary_audio_agent({
                "text": summary,
                "filename": f"paper_{i+1}_summary",
                "language": "en"
            })
            input_data["individual_audios"].append({
                "title": paper.get("title", f"Paper {i+1}"),
                "summary": summary,
                "audio_path": audio_result.get("audio_path", ""),
                "status": audio_result.get("status", "error"),
                "error": audio_result.get("error", "")
            })

        # 🔄 Cross-paper synthesis + audio
        if len(paper_summaries) >= 2:
            input_data["synthesis"] = synthesizer_agent({
                "topic": input_data.get("topic", "General"),
                "summaries": paper_summaries
            })

            synthesis_text = input_data["synthesis"].get("synthesis_text", "")
            if synthesis_text.strip():
                input_data["synthesis_audio"] = summary_audio_agent({
                    "text": synthesis_text,
                    "filename": f"synthesis_{input_data.get('topic', 'summary').replace(' ', '_')}",
                    "language": "en"
                })
            else:
                input_data["synthesis_audio"] = {
                    "status": "error",
                    "error": "Synthesis text is empty."
                }
        else:
            input_data["synthesis"] = {
                "status": "error",
                "message": "Too few papers for synthesis."
            }
            input_data["synthesis_audio"] = {
                "status": "error",
                "error": "Insufficient papers for audio generation."
            }

    # Final flag for UI
    input_data["status"] = "complete"
    print("✅ Final output keys:", list(input_data.keys()))
    return input_data






