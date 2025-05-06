import re
from pathlib import Path
import sys

def validate_tmdl_file(path):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    violations = []
    for i, line in enumerate(lines):
        if re.match(r'^\s*(table|column|measure|model|role|partition)\s', line):
            if i == 0 or not lines[i-1].strip().startswith("///"):
                violations.append((i+1, line.strip()))
    return violations

def main():
    all_violations = []
    for file in Path(".").rglob("*.tmdl"):
        violations = validate_tmdl_file(file)
        if violations:
            all_violations.append((file, violations))

    if all_violations:
        print("TMDL documentation violations found:\n")
        for file, violations in all_violations:
            for lineno, content in violations:
                print(f"{file}:{lineno} --> {content}")
        sys.exit(1)

if __name__ == "__main__":
    main()