import os
import sys
from pathlib import Path

FUNCTIONS = Path(__file__).resolve().parents[1]
for sub in ("", "processor"):
    sys.path.insert(0, str(FUNCTIONS / sub) if sub else str(FUNCTIONS))

os.environ.setdefault("AWS_DEFAULT_REGION", "eu-north-1")
os.environ.setdefault("AWS_REGION", "eu-north-1")
