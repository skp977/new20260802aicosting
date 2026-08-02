import os
import py_compile

root = os.path.dirname(os.path.abspath(__file__))

SKIP_DIRS = {".venv", "venv", "env", "__pycache__", ".git", "node_modules"}

errors = 0
checked = 0

for path, dirs, files in os.walk(root):
    dirs[:] = [
        d for d in dirs
        if d not in SKIP_DIRS
    ]
    for f in files:
        if f.endswith(".py"):
            full = os.path.join(path, f)
            checked += 1
            try:
                py_compile.compile(full, doraise=True)
                print("OK   ", full)
            except Exception as e:
                errors += 1
                print("ERROR", full)
                print(e)
                print("-" * 80)

print(f"\nChecked {checked} files, {errors} error(s)")
