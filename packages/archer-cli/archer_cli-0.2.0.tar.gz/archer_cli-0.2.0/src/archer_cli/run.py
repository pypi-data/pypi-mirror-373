# Thin wrapper that imports the existing app's main
# We want to keep current behavior but under package entry point

from pathlib import Path
import sys

# Ensure project root is importable if needed
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import main  # reuse existing main
