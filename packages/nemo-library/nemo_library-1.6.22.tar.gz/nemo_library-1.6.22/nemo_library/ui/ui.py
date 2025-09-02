"""
UI launcher for the nemo_library package.
This module provides a function to run the Streamlit UI for the application.
"""

import logging
import os
import subprocess
from pathlib import Path


def run_streamlit_ui():
    """
    Launches the Streamlit UI by running the ui_main.py script with the correct PYTHONPATH.
    """
    this_file = Path(__file__).resolve()
    ui_script = str(this_file.with_name("ui_main.py"))

    # Calculate package root (folder containing `nemo_library`)
    package_root = str(this_file.parent.parent.parent)

    env = os.environ.copy()
    env["PYTHONPATH"] = package_root + os.pathsep + env.get("PYTHONPATH", "")

    logging.info("Running Streamlit UI from script: %s", ui_script)
    logging.info("Using PYTHONPATH: %s", env["PYTHONPATH"])
    subprocess.run(["streamlit", "run", ui_script], check=True, env=env)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Starting Streamlit UI for nemo_library")
    # Run the Streamlit UI
    run_streamlit_ui()
