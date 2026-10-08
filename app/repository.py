from pathlib import Path
from collections import Counter

from code_parser import parse_file

# --- Phase 1: extension -> language grouping ---

EXTENSION_TO_LANGUAGE = {
    "java": "Java",
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "xml": "XML",
    "yml": "YAML",
    "yaml": "YAML",
    "md": "Markdown",
    "json": "JSON",
    "html": "HTML",
    "css": "CSS",
    "sql": "SQL",
    "sh": "Shell",
}

# --- Phase 2: which extensions actually get AST-parsed ---
# grow this list as you add more tree-sitter langs later
PARSEABLE_EXTENSIONS = {"java", "py"}

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".idea", "target", "build"}


def analyze_repo(repo_path: str):
    """Returns (total_files, language_counts) as a Counter grouped by language."""
    language_counts = Counter()
    total_files = 0

    for path in Path(repo_path).rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        total_files += 1
        ext = path.suffix.lstrip(".").lower()
        language = EXTENSION_TO_LANGUAGE.get(ext, "Other")
        language_counts[language] += 1

    return total_files, language_counts


def parse_repo(repo_path: str):
    """Walks the repo and returns all chunks from all parseable files.

    Each chunk dict has: name, type, code, start_line, end_line, file_path
    """
    all_chunks = []

    for path in Path(repo_path).rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        ext = path.suffix.lstrip(".").lower()
        if ext not in PARSEABLE_EXTENSIONS:
            continue

        file_chunks = parse_file(path)
        for chunk in file_chunks:
            chunk["file_path"] = str(path.relative_to(repo_path))
            all_chunks.append(chunk)

    return all_chunks