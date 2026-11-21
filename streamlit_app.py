"""Streamlit Cloud entry point for ApexRent AI."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rent_agent.ui.dashboard import render_app

if __name__ == "__main__":
    render_app()
