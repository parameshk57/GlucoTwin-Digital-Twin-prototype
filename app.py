"""Streamlit Cloud root entry point for GlucoTwin.

Configure Streamlit Community Cloud to run this file (app.py). The actual UI
lives in app/app.py; its model module and data paths are relative to the project.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
APP_DIR = PROJECT_ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Importing this module runs the Streamlit UI on the normal Streamlit script thread.
import runpy; runpy.run_path(str(APP_DIR / "app.py"))
