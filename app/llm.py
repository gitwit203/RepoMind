import ollama

MODEL_NAME = "qwen2.5:3b"


def generate_answer(question: str, chunks: list) -> str:
    """Takes retrieved chunks and a question, returns a structured markdown answer."""
    context = _format_context(chunks)

    prompt = f"""You are a precise code analysis assistant. Answer the question using ONLY the code context below.

STRICT RULES:
- If the evidence does not support a claim, DO NOT make that claim.
- If the evidence is insufficient to answer part or all of the question, say "Insufficient evidence" for that part instead of guessing.
- Do not infer things not explicitly shown in the code (e.g. do not guess which AI provider is used unless the provider name literally appears in the context).
- Every claim in your Evidence section must reference a specific class or method name from the context.

Respond in EXACTLY this format, nothing before or after it:

## Answer
<one short paragraph answering the question>

## Evidence
1. `<class_or_method_name>` — <one line explaining what it does, based only on the code shown>
2. `<class_or_method_name>` — <one line explaining what it does, based only on the code shown>
(add more numbered points only if the context supports them)

Context:
{context}

Question: {question}"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )

    llm_output = response["message"]["content"].strip()
    sources_section = _format_source_locations(chunks)

    return f"{llm_output}\n\n{sources_section}"


def _format_context(chunks: list) -> str:
    """Formats retrieved chunks into readable context for the prompt."""
    parts = []
    for chunk in chunks:
        parts.append(
            f"File: {chunk['file_path']}\n"
            f"{chunk['type']} {chunk['name']} (lines {chunk['start_line']}-{chunk['end_line']})\n"
            f"```\n{chunk['code']}\n```"
        )
    return "\n\n".join(parts)


def _format_source_locations(chunks: list) -> str:
    """Builds the Source locations section directly from chunk metadata (not LLM-generated)."""
    lines = ["## Source locations"]
    for chunk in chunks:
        file_name = chunk["file_path"].split("\\")[-1].split("/")[-1]  # handle both OS path styles
        lines.append(f"- {file_name}: {chunk['start_line']}-{chunk['end_line']}")
    return "\n".join(lines)