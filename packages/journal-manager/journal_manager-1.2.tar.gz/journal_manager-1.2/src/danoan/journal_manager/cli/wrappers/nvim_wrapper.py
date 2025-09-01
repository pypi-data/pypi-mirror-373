from pathlib import Path
import subprocess
from typing import Optional


def edit_file(
    filepath: Path,
    nvim_path: Path = Path("nvim"),
    working_dir: Optional[Path] = None,
):
    """
    Interface to open a file in nvim.
    """
    if working_dir is None:
        working_dir = Path(filepath).parent

    subprocess.run([nvim_path, "--cmd", f"cd {working_dir}", filepath])
