import streamlit as st
from github import clone_repo
from repository import analyze_repo, parse_repo
from embeddings import index_chunks, search_chunks
from llm import generate_answer

st.title("Repo Q&A")

repo_url = st.text_input("GitHub repo URL")

if st.button("Analyze") and repo_url:
    with st.spinner("Cloning repository..."):
        try:
            repo_path = clone_repo(repo_url)
        except Exception as e:
            st.error(f"Failed to clone repo: {e}")
            st.stop()

    total_files, language_counts = analyze_repo(repo_path)
    st.success("Repository downloaded successfully.")
    st.write(f"**Files:** {total_files}")
    for language, count in language_counts.most_common():
        st.write(f"**{language}:** {count}")

    with st.spinner("Parsing code into chunks..."):
        chunks = parse_repo(repo_path)
    st.success(f"Parsed {len(chunks)} chunks from the codebase.")

    with st.spinner("Embedding and indexing chunks..."):
        index_chunks(chunks)
    st.success("Repo indexed. You can now search below.")

    st.session_state["indexed"] = True

    # quick sanity-check view of parsed chunks
    with st.expander("Preview parsed chunks"):
        for chunk in chunks[:20]:  # only show first 20 so the UI doesn't choke
            st.markdown(f"**{chunk['file_path']}** — `{chunk['type']}` — `{chunk['name']}` "
                        f"(lines {chunk['start_line']}–{chunk['end_line']})")
            st.code(chunk["code"][:300])

# --- Query section ---
if st.session_state.get("indexed"):
    st.divider()
    query = st.text_input("Ask something about the repo")

    if st.button("Search") and query:
        results = search_chunks(query, top_k=5)

        with st.spinner("Generating answer..."):
            answer = generate_answer(query, results)

        st.markdown(answer)

        with st.expander("Sources used"):
            for r in results:
                st.markdown(f"**{r['file_path']}** — `{r['type']}` — `{r['name']}` "
                            f"(lines {r['start_line']}–{r['end_line']})")
                st.code(r["code"])
                st.divider()