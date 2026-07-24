import requests
import streamlit as st

# ==========================================================
# Configuration
# ==========================================================

API_BASE_URL = "http://localhost:8001/api/v1"
SESSION_ID = "streamlit_session_001"

st.set_page_config(
    page_title="Enterprise AI Knowledge Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Enterprise AI Knowledge Assistant")
st.caption("Retrieval Augmented Generation (RAG) using Groq + PostgreSQL + pgvector")

# ==========================================================
# Sidebar
# ==========================================================

with st.sidebar:

    st.header("📂 Document Management")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
    )

    if uploaded_file:

        if st.button(
            "🚀 Upload & Process",
            use_container_width=True,
        ):

            with st.spinner("Processing PDF..."):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/upload",
                        files=files,
                    )

                    if response.status_code == 201:

                        result = response.json()

                        st.success("Document uploaded successfully.")

                        st.info(
                            f"Chunks Created : "
                            f"{result.get('total_chunks_processed',0)}"
                        )

                        st.rerun()

                    else:

                        st.error(
                            response.text
                        )

                except Exception as ex:

                    st.error(str(ex))

    st.divider()

    st.subheader("📑 Documents")

    selected_doc_id = None

    try:

        response = requests.get(
            f"{API_BASE_URL}/documents"
        )

        if response.status_code == 200:

            documents = response.json().get(
                "documents",
                [],
            )

            if documents:

                options = {
                    f"{doc['pdf_name']} ({doc['document_id'][:8]})":
                    doc["document_id"]
                    for doc in documents
                }

                selected_name = st.selectbox(
                    "Select Document",
                    options.keys(),
                )

                selected_doc_id = options[selected_name]

                st.divider()

                top_k = st.slider(
                    "Top K Retrieval",
                    min_value=1,
                    max_value=10,
                    value=5,
                )

                st.caption(
                    "Number of document chunks retrieved."
                )

                st.divider()

                if st.button(
                    "🗑 Delete Document",
                    use_container_width=True,
                    type="primary",
                ):

                    delete_response = requests.delete(
                        f"{API_BASE_URL}/documents/{selected_doc_id}"
                    )

                    if delete_response.status_code == 200:

                        st.success("Deleted Successfully")

                        st.rerun()

                    else:

                        st.error(
                            delete_response.text
                        )

            else:

                st.info("No documents uploaded.")

        else:

            st.error("Unable to load documents.")

    except Exception as ex:

        st.error(str(ex))

# ==========================================================
# No document selected
# ==========================================================

if not selected_doc_id:

    st.warning(
        "Upload a PDF and select a document from the sidebar."
    )

    st.stop()
# ==========================================================
# Current Document
# ==========================================================

st.success(
    f"Current Document : `{selected_doc_id}`"
)

# ==========================================================
# Load History When Document Changes
# ==========================================================

if (
    "loaded_document_id" not in st.session_state
    or st.session_state.loaded_document_id != selected_doc_id
):

    st.session_state.loaded_document_id = selected_doc_id
    st.session_state.messages = []

    try:

        response = requests.get(
            f"{API_BASE_URL}/history",
            params={
                "session_id": SESSION_ID,
                "document_id": selected_doc_id,
            },
            timeout=30,
        )

        if response.status_code == 200:

            history = response.json().get(
                "history",
                [],
            )

            # oldest -> newest
            history.reverse()

            for item in history:

                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": item["question"],
                    }
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": item["answer"],
                        "citations": item.get(
                            "citations",
                            [],
                        ),
                    }
                )

        else:

            st.error(
                f"History API Error ({response.status_code})"
            )

            try:
                st.json(response.json())
            except Exception:
                st.text(response.text)

    except Exception as ex:

        st.error(
            f"Unable to load history:\n{ex}"
        )

# ==========================================================
# Display Chat History
# ==========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("citations")
        ):

            with st.expander(
                f"📚 Retrieved Sources ({len(message['citations'])})",
                expanded=False,
            ):

                for idx, cite in enumerate(
                    message["citations"],
                    start=1,
                ):

                    chunk_confidence = cite.get("chunk_confidence", 0.0)

                    similarity = float(
                        cite.get("similarity", 0.0)
                    )

                    rerank = float(
                        cite.get("rerank_score", 0.0)
                    )

                    keyword = float(
                        cite.get("keyword_score", 0.0)
                    )

                    rrf = float(
                        cite.get("rrf_score", 0.0)
                    )

                    with st.container():

                        st.markdown(
                            f"### 📄 Source {idx}"
                        )

                        st.markdown(
                            f"### 🎯 Chunk Confidence : {chunk_confidence:.2f}%"
                        )

                        st.progress(
                            min(chunk_confidence / 100, 1.0)
                        )

                        st.markdown(
                                    f"""
                        <div style="
                        background:#f8f9fa;
                        border-left:5px solid #4CAF50;
                        padding:16px;
                        border-radius:8px;
                        font-size:15px;
                        line-height:1.7;
                        color:#262730;
                        ">
                        {cite.get("chunk_text", "")}
                        </div>
                        """,
                                    unsafe_allow_html=True,
                                )

                        c1, c2, c3 = st.columns(3)

                        c1.metric(
                            "Pages",
                            (
                                str(cite["page_start"])
                                if cite.get("page_start") == cite.get("page_end")
                                else f'{cite.get("page_start")} - {cite.get("page_end")}'
                            ),
                        )

                        c2.metric(
                            "Chunk",
                            cite.get(
                                "chunk_number",
                                "-",
                            ),
                        )

                        c3.metric(
                            "Lines",
                            f"{cite.get('line_start','-')} - {cite.get('line_end','-')}",
                        )

                        st.caption(
                            f"📄 {cite.get('pdf_name','')}"
                        )

                        st.divider()

                        
                                            
# ==========================================================
# Chat Input
# ==========================================================

if prompt := st.chat_input(
    "Ask a question about the selected document..."
):

    # --------------------------------------------
    # Display user message
    # --------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    # --------------------------------------------
    # Assistant
    # --------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Searching document and generating answer..."):

            payload = {
                "document_id": selected_doc_id,
                "session_id": SESSION_ID,
                "question": prompt,
                "top_k": top_k,
            }

            try:

                response = requests.post(
                    f"{API_BASE_URL}/query",
                    json=payload,
                    headers={
                        "Content-Type": "application/json"
                    },
                )

                # ------------------------------------
                # Success
                # ------------------------------------

                if response.status_code == 200:

                    data = response.json()

                    answer = data.get("answer", "No answer returned.")
                    citations = data.get("citations", [])

                    confidence = data.get("confidence", 0.0)
                    pipeline_time = data.get("pipeline_time", 0.0)
                    search_time = data.get("search_time", 0.0)
                    rerank_time = data.get("rerank_time", 0.0)
                    context_time = data.get("context_time", 0.0)
                    llm_time = data.get("llm_time", 0.0)

                    st.write(answer)

                    st.divider()

                    st.subheader("📊 Answer Quality")

                    c1, c2 = st.columns(2)

                    c1.metric(
                        "Confidence",
                        f"{confidence:.2f}%",
                    )

                    c2.progress(
                        min(confidence / 100, 1.0)
                    )

                    if confidence >= 90:
                        st.success("Excellent confidence")

                    elif confidence >= 75:
                        st.success("High confidence")

                    elif confidence >= 60:
                        st.warning("Medium confidence")

                    elif confidence >= 40:
                        st.warning("Low confidence")

                    else:
                        st.error("Very Low confidence")

                    st.divider()

                    # st.subheader("⚡ Pipeline Performance")

                    # c1, c2, c3 = st.columns(3)

                    # c1.metric(
                    #     "Search",
                    #     f"{search_time:.2f}s",
                    # )

                    # c2.metric(
                    #     "Reranker",
                    #     f"{rerank_time:.2f}s",
                    # )

                    # c3.metric(
                    #     "Context",
                    #     f"{context_time:.2f}s",
                    # )

                    # c4, c5 = st.columns(2)

                    # c4.metric(
                    #     "LLM",
                    #     f"{llm_time:.2f}s",
                    # )

                    # c5.metric(
                    #     "Total",
                    #     f"{pipeline_time:.2f}s",
                    # )

                    # st.divider()

                    if citations:

                        with st.expander(
                            f"📚 Retrieved Sources ({len(citations)})",
                            expanded=False,
                        ):

                            for idx, cite in enumerate(citations, start=1):

                                chunk_confidence = cite.get("chunk_confidence", 0.0)

                                similarity = float(
                                    cite.get("similarity", 0.0)
                                )

                                rerank = float(
                                    cite.get("rerank_score", 0.0)
                                )

                                keyword = float(
                                    cite.get("keyword_score", 0.0)
                                )

                                rrf = float(
                                    cite.get("rrf_score", 0.0)
                                )

                                st.markdown(
                                    f"### 📄 Source {idx}"
                                )

                                st.markdown(
                                    f"### 🎯 Chunk Confidence : {chunk_confidence:.2f}%"
                                )

                                st.progress(
                                    min(chunk_confidence / 100, 1.0)
                                )

                                st.markdown(
                                    f"""
                        <div style="
                        background:#f8f9fa;
                        border-left:5px solid #4CAF50;
                        padding:16px;
                        border-radius:8px;
                        font-size:15px;
                        line-height:1.7;
                        color:#262730;
                        ">
                        {cite.get("chunk_text", "")}
                        </div>
                        """,
                                    unsafe_allow_html=True,
                                )

                                st.markdown("")

                                col1, col2, col3 = st.columns(3)

                                col1.metric(
                                    "Pages",
                                    (
                                        str(cite["page_start"])
                                        if cite.get("page_start") == cite.get("page_end")
                                        else f'{cite.get("page_start")} - {cite.get("page_end")}'
                                    ),
                                )

                                col2.metric(
                                    "Chunk",
                                    cite["chunk_number"],
                                )

                                col3.metric(
                                    "Lines",
                                    f"{cite['line_start']} - {cite['line_end']}",
                                )

                                st.caption(
                                    f"📄 {cite['pdf_name']}"
                                )

                                c1, c2, c3, c4 = st.columns(4)

                                c1.metric(
                                    "Similarity",
                                    f"{similarity:.4f}",
                                )

                                c2.metric(
                                    "Rerank",
                                    f"{rerank:.4f}",
                                )

                                c3.metric(
                                    "Keyword",
                                    f"{keyword:.4f}",
                                )

                                c4.metric(
                                    "RRF",
                                    f"{rrf:.4f}",
                                )

                                st.divider()

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "citations": citations,
                            "confidence": confidence,
                            "pipeline_time": pipeline_time,
                        }
                    )

                # ------------------------------------
                # API Error
                # ------------------------------------

                else:

                    st.error(
                        f"API Error ({response.status_code})"
                    )

                    try:
                        st.json(
                            response.json()
                        )
                    except Exception:
                        st.text(
                            response.text
                        )

            except Exception as ex:

                st.error(
                    f"Connection Error: {str(ex)}"
                )