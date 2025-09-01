from pathlib import Path
import os
import subprocess


def create(journal_location: Path):
    """
    Create a mkdocs journal.
    """
    subprocess.run(["mkdocs", "new", journal_location])


def build(journal_location: Path, build_location: Path):
    """
    Build a static html page with mkdocs.
    """
    cwd = os.getcwd()

    os.chdir(journal_location)
    # By default, mkdocs uses a clean build. Files present in the
    # build location are removed before the new build starts.
    subprocess.run(["mkdocs", "build", "-d", build_location])

    os.chdir(cwd)
