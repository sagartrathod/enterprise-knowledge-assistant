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
# Load Chat History
# ==========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []

    try:

        response = requests.get(
            f"{API_BASE_URL}/history",
            params={
                "session_id": SESSION_ID,
            },
        )

        if response.status_code == 200:

            history = response.json().get(
                "history",
                [],
            )

            for item in reversed(history):

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

    except Exception:
        pass
# ==========================================================
# Display Existing Messages
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

                    similarity = float(
                        cite.get("similarity", 0.0)
                    )

                    # Convert to percentage if stored as decimal
                    similarity_percent = (
                        similarity * 100
                        if similarity <= 1
                        else similarity
                    )

                    st.markdown(f"### 📄 Source {idx}")

                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(
                            f"""
**File:** `{cite.get("pdf_name")}`

**Page:** {cite.get("page_number")}

**Chunk:** {cite.get("chunk_number")}

**Lines:** {cite.get("line_start")} - {cite.get("line_end")}
"""
                        )

                    with col2:
                        st.metric(
                            "Similarity",
                            f"{similarity_percent:.2f}%"
                        )

                    st.progress(
                        min(similarity_percent / 100, 1.0)
                    )

                    st.code(
                        cite.get("chunk_text", ""),
                        language="text",
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

                    answer = data.get(
                        "answer",
                        "No answer returned.",
                    )

                    citations = data.get(
                        "citations",
                        [],
                    )

                    total_chunks = data.get(
                        "total_chunks_used",
                        0,
                    )

                    # -----------------------------
                    # Answer
                    # -----------------------------

                    st.markdown("## 🤖 Answer")

                    st.write(answer)

                    # -----------------------------
                    # Retrieval Statistics
                    # -----------------------------

                    st.markdown("---")

                    st.subheader("📊 Retrieval Statistics")

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            label="Chunks Used",
                            value=total_chunks,
                        )

                    with col2:

                        if citations:

                            average_similarity = (
                                sum(
                                    c.get(
                                        "similarity",
                                        0,
                                    )
                                    for c in citations
                                )
                                / len(citations)
                            )

                            st.metric(
                                "Average Similarity",
                                f"{average_similarity:.2%}",
                            )

                        else:

                            st.metric(
                                "Average Similarity",
                                "0%",
                            )

                    # -----------------------------
                    # Sources
                    # -----------------------------

                    if citations:

                        st.markdown("---")

                        st.subheader(
                            "📚 Supporting Sources"
                        )

                        for index, cite in enumerate(
                            citations,
                            start=1,
                        ):

                            similarity = cite.get(
                                "similarity",
                                0,
                            )

                            with st.expander(
                                f"📄 Source {index} • {cite['pdf_name']} • {similarity:.2%}"
                            ):

                                c1, c2, c3 = st.columns(3)

                                c1.metric(
                                    "Page",
                                    cite["page_number"],
                                )

                                c2.metric(
                                    "Chunk",
                                    cite["chunk_number"],
                                )

                                c3.metric(
                                    "Similarity",
                                    f"{similarity:.2%}",
                                )

                                st.caption(
                                    f"Lines {cite['line_start']} - {cite['line_end']}"
                                )

                                st.code(
                                    cite["chunk_text"],
                                    language="text",
                                )

                    else:

                        st.info(
                            "No supporting document chunks were used."
                        )

                    # -----------------------------
                    # Save to chat history
                    # -----------------------------

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "citations": citations,
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