import sys
from pathlib import Path

# Ensure project root is in Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import and run Streamlit dashboard
import app.dashboard  # This will execute the Streamlit UI
