import google.generativeai as genai
import os

def summarizer_agent(input: dict) -> dict:
    chunks = input.get("chunks", [])
    style = input.get("style", "abstract")
    model_name = "gemini-2.0-flash"
    metadata = input.get("metadata", {})

    # Combine all text chunks
    text_blocks = [chunk["content"] for chunk in chunks if chunk["type"] == "text"]
    if not text_blocks:
        return {
            "status": "error",
            "message": "No text-based content found for summarization.",
            "summary_text": "",
        }

    full_text = "\n".join(text_blocks)[:12000]

    prompt = f"""
You are an expert academic summarizer.

Summarize the following research paper content into a concise {style}-style summary (100-150 words). Focus on:
- Problem tackled
- Proposed method
- Key results
- Conclusion

TEXT:
\"\"\"{full_text}\"\"\"
"""

    try:
        genai.configure(api_key="AIzaSyA0djFQGSdwoS9mSSnHh4YItHvniEATq3o")  # replace or use env
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        summary = response.text.strip()

        return {
            "status": "success",
            "summary_text": summary,
            "style": style,
            "model_used": model_name,
            "metadata": metadata
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini summarization failed: {str(e)}",
            "summary_text": ""
        }


def synthesizer_agent(input: dict) -> dict:
    topic = input.get("topic", "General")
    summaries = input.get("summaries", [])
    model_name = "gemini-2.0-flash"

    if len(summaries) < 2:
        return {
            "status": "error",
            "message": "At least two summaries are required for synthesis.",
            "synthesis_text": "",
        }

    combined_text = "\n\n".join([f"- {s}" for s in summaries])

    prompt = f"""
You are a domain expert summarizer.

You are given multiple research paper summaries on the topic: **{topic}**.

Your task is to:
- Compare and synthesize insights across papers
- Highlight common trends, differing methods, and collective findings
- Write a 2-paragraph synthesis suitable for a literature review

Summaries:
{combined_text}
"""

    try:
        genai.configure(api_key="AIzaSyA0djFQGSdwoS9mSSnHh4YItHvniEATq3o")  # Replace as needed
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        synthesis = response.text.strip()

        return {
            "status": "success",
            "topic": topic,
            "synthesis_text": synthesis,
            "model_used": model_name,
            "num_summarized": len(summaries),
            "metadata": {
                "title": f"Synthesis on {topic}",
                "source": "Multiple papers",
                "year": "2024"
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Synthesis generation failed: {str(e)}",
            "synthesis_text": ""
        }

