import os
import sys

# Ensure project root is importable when running tests via VS Code tasks
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
