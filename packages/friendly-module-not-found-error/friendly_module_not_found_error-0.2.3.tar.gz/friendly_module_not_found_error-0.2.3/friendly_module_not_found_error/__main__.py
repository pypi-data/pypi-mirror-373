import sys
import os
import subprocess


def main():
    os.chdir(f"{os.path.dirname(__file__)}/test")
    result = subprocess.run(
        [sys.executable, "test.py"],
        text=True,
        capture_output=True
    )
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
if __name__ == "__main__":
    main()

    
