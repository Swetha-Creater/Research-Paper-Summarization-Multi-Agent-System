import streamlit as st
from pipeline_graph import run_pipeline
import base64
import os

st.set_page_config(page_title=" AI Research Paper Assistant", layout="wide")
st.title(" Research Paper Summarizer & Podcast Generator")

# --- Sidebar Configuration ---
st.sidebar.title(" Configuration")
input_type = st.sidebar.radio("Choose Input Type:", ["Topic", "PDF Upload", "PDF URL"])
topic_list = st.sidebar.text_area(" Topic Categories (comma-separated)", "NLP, Computer Vision, Healthcare AI")
topic_list = [t.strip() for t in topic_list.split(",") if t.strip()]
input_data = {"topic_list": topic_list}

# --- Input Fields ---
if input_type == "Topic":
    topic = st.text_input(" Enter a Research Topic")
    if topic:
        input_data["topic"] = topic

elif input_type == "PDF Upload":
    uploaded_file = st.file_uploader(" Upload a research paper (PDF)", type=["pdf"])
    if uploaded_file:
        input_data["pdf_file"] = uploaded_file

elif input_type == "PDF URL":
    pdf_url = st.text_input(" Enter PDF URL")
    if pdf_url:
        input_data["pdf_url"] = pdf_url

# --- Run Button ---
if st.button(" Run Research"):
    with st.spinner("Running your research..."):
        result = run_pipeline(input_data)

    st.success(" Pipeline Completed!")

    # ========== MODE: ERROR ==========
    if result.get("fetched", {}).get("mode") == "error":
        st.error(f" Error: {result['fetched'].get('error', 'Unknown error occurred.')}")
        st.stop()

    # ========== MODE: PDF ==========
    if result.get("fetched", {}).get("mode") == "pdf":
        title = result.get("metadata", {}).get("title", input_data.get("topic", "Untitled Paper"))
        st.subheader(" Summary for Uploaded Paper")
        st.markdown(f"**Title:** {title}")

        url = result.get("metadata", {}).get("url")
        if url:
            st.markdown(f"🔗 [View Paper]({url})")

        summary_text = result.get("summary", {}).get("summary_text", "")
        st.text(f" Debug: summary text length = {len(summary_text)}")

        if summary_text.strip():
            st.markdown(summary_text)
        else:
            st.warning(" No summary generated or the document contained no readable text.")

        audio_result = result.get("audio", {})
        if audio_result.get("status") == "success":
            st.subheader("🎧 Audio Summary")
            audio_path = audio_result["audio_path"]
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                b64 = base64.b64encode(audio_bytes).decode()
                filename = os.path.basename(audio_path)
                href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">⬇️ Download Audio ({filename})</a>'
                st.markdown(href, unsafe_allow_html=True)
        elif audio_result.get("status") == "error":
            st.warning(f" Audio error: {audio_result.get('error')}")

    # ========== MODE: SEARCH ==========
    elif result.get("fetched", {}).get("mode") == "search":
        st.subheader(" Individual Paper Summaries + Audio")

        papers = result["fetched"].get("papers", [])
        individual_audios = result.get("individual_audios", [])
        summaries = result.get("summaries", [])

        for i, paper in enumerate(papers):
            title = paper.get("title", f"Paper {i+1}")
            summary = summaries[i] if i < len(summaries) else ""
            url = paper.get("url", "")

            st.markdown(f"### {i+1}. {title}")
            if url:
                st.markdown(f"[View Paper]({url})")
            if summary:
                st.markdown(f" **Summary:** {summary}")

            if i < len(individual_audios):
                audio_path = individual_audios[i].get("audio_path", "")
                if os.path.exists(audio_path):
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        b64 = base64.b64encode(audio_bytes).decode()
                        filename = os.path.basename(audio_path)
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">⬇️ Download Audio</a>'
                        st.markdown(href, unsafe_allow_html=True)
                elif individual_audios[i].get("status") == "error":
                    st.warning(f"Audio error: {individual_audios[i].get('error')}")

            st.markdown("---")

        # Cross-paper synthesis
        synthesis = result.get("synthesis", {})
        if synthesis.get("synthesis_text"):
            topic = synthesis.get("topic", input_data.get("topic", "Unknown Topic"))
            st.subheader(f"Cross-Paper Synthesis on: :green[{topic}]")
            st.markdown(synthesis["synthesis_text"])

        # Synthesis audio
        synthesis_audio = result.get("synthesis_audio", {})
        if synthesis_audio.get("status") == "success":
            st.subheader("Cross-Paper Podcast")
            audio_path = synthesis_audio["audio_path"]
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                b64 = base64.b64encode(audio_bytes).decode()
                filename = os.path.basename(audio_path)
                href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">⬇️ Download Podcast ({filename})</a>'
                st.markdown(href, unsafe_allow_html=True)
        elif synthesis_audio.get("status") == "error":
            st.warning(f"Synthesis audio error: {synthesis_audio.get('error')}")








