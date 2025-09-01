import sys
import shutil
from pathlib import Path

def export_frontend():
    source = Path(__file__).parent / "web" / "frontend"
    target = Path(sys.argv[0])
    if target.exists and target.is_dir:
        shutil.copy(source, target, dirs_exist_ok=True)
    print(sys.argv)

def setup_basic_implementation():
    print(sys.argv)

def setup_boilerplate():
    export_frontend()
    setup_basic_implementation()
    print(sys.argv)