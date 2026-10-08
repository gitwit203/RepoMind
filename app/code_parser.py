from tree_sitter_languages import get_parser
from pathlib import Path

# node types that count as a "chunk" per language
CHUNK_NODE_TYPES = {
    "java": {"method_declaration", "class_declaration", "constructor_declaration"},
    "python": {"function_definition", "class_definition"},
}

EXTENSION_TO_TS_LANG = {
    "java": "java",
    "py": "python",
}

def parse_file(file_path: Path):
    """Returns a list of chunks: {name, type, code, start_line, end_line}"""
    ext = file_path.suffix.lstrip(".").lower()
    lang = EXTENSION_TO_TS_LANG.get(ext)
    if lang is None:
        return []  # unsupported language, skip entirely in phase 2

    parser = get_parser(lang)
    source = file_path.read_bytes()
    tree = parser.parse(source)

    chunks = []
    _walk(tree.root_node, source, lang, chunks)

    if not chunks:
        # nothing matched (no functions/classes found) — fall back to whole file
        text = source.decode("utf-8", errors="ignore")
        if text.strip():
            chunks.append({
                "name": file_path.name,
                "type": "file",
                "code": text,
                "start_line": 1,
                "end_line": len(text.splitlines()),
            })

    return chunks


def _walk(node, source, lang, chunks):
    if node.type in CHUNK_NODE_TYPES.get(lang, set()):
        code = source[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
        name = _extract_name(node, source)
        chunks.append({
            "name": name,
            "type": node.type,
            "code": code,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
        })
        # don't recurse into children of a matched node, avoids
        # capturing a method twice (once alone, once inside its class)
        return

    for child in node.children:
        _walk(child, source, lang, chunks)


def _extract_name(node, source):
    for child in node.children:
        if child.type == "identifier":
            return source[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
    return "anonymous"