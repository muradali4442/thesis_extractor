# Makes the package importable in tests without installing it.
# Adds the project's `src/` directory to sys.path at test collection time.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
