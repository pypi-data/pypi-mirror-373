import subprocess


def start(process_filepath: str, **kwargs):
    """
    Interface to start a general process.
    """
    proc_args = [process_filepath, *kwargs]
    subprocess.run(proc_args)
