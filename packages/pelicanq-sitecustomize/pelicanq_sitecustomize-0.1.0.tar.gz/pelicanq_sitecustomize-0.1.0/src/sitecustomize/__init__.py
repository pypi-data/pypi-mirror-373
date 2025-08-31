import sys
from pathlib import Path

dir = Path(__file__).parent.parent

while dir.name != ".venv":
    dir = dir.parent
dir = dir.parent

sys.path.append(str(dir))
