import subprocess
import tempfile

def clone_repo(repo_url: str) -> str:
    """Clones repo_url into a temp dir and returns the path."""
    temp_dir = tempfile.mkdtemp()
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, temp_dir],
        check=True,
        capture_output=True,
        text=True,
    )
    return temp_dir