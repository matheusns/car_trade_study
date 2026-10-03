#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

app = Path(__file__).with_name("app.py")
cmd = [
    sys.executable, "-m", "streamlit", "run", str(app),
    "--server.address", "127.0.0.1",
    "--server.port", "8501",
]
raise SystemExit(subprocess.call(cmd))
