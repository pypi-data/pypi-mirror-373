# For jeteve_omniorb/wrapper.py
from pathlib import Path
import os
import subprocess
import sys


def run_binary(binary_name):
    binary_path = Path(__file__).parent / "bin" / binary_name

    if not binary_path.exists():
        print(f"Binary {binary_name} not found at {binary_path}")
        sys.exit(1)

    os.chmod(binary_path, 0o755)

    return subprocess.call([str(binary_path)] + sys.argv[1:])


def run_omnicpp():
    return run_binary("omnicpp")

def run_omniNames():
    return run_binary("omniNames")

if __name__ == "__main__":
    sys.exit(run_omnicpp())
