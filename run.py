"""Root entrypoint to run the Secure Data Sanitization & Recovery System."""

import sys
from pathlib import Path

# Ensure root directory is in python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app

if __name__ == "__main__":
    print("==================================================================")
    print("  AEGIS FORENSICS: SECURE SANITIZATION & FILE RECOVERY SYSTEM     ")
    print("  Server URL: http://127.0.0.1:5000                               ")
    print("==================================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
