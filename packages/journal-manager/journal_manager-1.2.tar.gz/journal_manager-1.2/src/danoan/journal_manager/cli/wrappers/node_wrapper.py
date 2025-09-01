import subprocess
from pathlib import Path
import os


def install_dependencies(http_server_location: Path):
    """
    Install dependencies for node.js.
    """
    cwd = os.getcwd()
    os.chdir(http_server_location.expanduser().as_posix())
    npm_args = ["npm", "install"]
    subprocess.run(npm_args)
    os.chdir(cwd)


def start_server(init_script: Path):
    """
    Start a node.Js application.
    """
    node_args = ["node", init_script.expanduser().as_posix()]
    subprocess.run(node_args)
