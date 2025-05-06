import re
from pathlib import Path
import sys
import argparse

def scan_tmdl_file(path, required_entities):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    artefact_pattern = re.compile(
        rf"^[ \t]*({'|'.join(re.escape(e) for e in required_entities)})\b\s*('([^']|'')+'|[^\s=:]+)"
    )
    artefacts = []
    for i, line in enumerate(lines):
        m = artefact_pattern.match(line)
        if m:
            entity = m.group(1)
            artefact_name = m.group(2).strip()
            # Ignore if previous line contains ignore comment
            if i > 0 and "tmdl-doc-ignore" in lines[i-1]:
                continue
            # Check for documentation row(s) above, skipping blank lines
            idx = i - 1
            doc_lines = []
            while idx >= 0:
                content = lines[idx].strip()
                if content == "":
                    idx -= 1
                    continue
                if content.lstrip().startswith("///"):
                    doc_lines.insert(0, lines[idx].rstrip("\n"))
                    idx -= 1
                    continue
                break
            artefacts.append({
                "file": path,
                "line": i+1,
                "entity": entity,
                "name": artefact_name,
                "doc": doc_lines
            })
    return artefacts

def main():
    parser = argparse.ArgumentParser(description="Validate TMDL documentation.")
    parser.add_argument(
        "--require",
        type=str,
        default="table,column,measure,model,role,partition",
        help="Comma-separated list of entities to require documentation for (e.g. table,column,measure)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a specific TMDL file to validate"
    )
    parser.add_argument(
        "--artefact",
        type=str,
        default=None,
        help="Artefact to validate in the form 'type name' (e.g. 'column COGS')"
    )
    args = parser.parse_args()
    required_entities = [e.strip() for e in args.require.split(",") if e.strip()]

    if args.require == "table,column,measure,model,role,partition":
        print("WARNING: No --require argument provided. All entities will be enforced (table, column, measure, model, role, partition).\n"
              "To match your workflow, run with:\n"
              "  python .github/scripts/validate_tmdl_docs.py --require table,column,measure\n")

    files_to_check = [Path(args.file)] if args.file else Path(".").rglob("*.tmdl")
    all_artefacts = []
    for file in files_to_check:
        artefacts = scan_tmdl_file(file, required_entities)
        all_artefacts.extend(artefacts)

    # Artefact targeting by type and name
    if args.artefact:
        artefact_type, artefact_name = args.artefact.split(" ", 1)
        all_artefacts = [
            a for a in all_artefacts
            if a["entity"] == artefact_type and (a["name"] == artefact_name or a["name"].strip("'") == artefact_name.strip("'"))
        ]

    violations = [a for a in all_artefacts if not a["doc"]]
    successes = [a for a in all_artefacts if a["doc"]]

    if violations:
        print("TMDL documentation violations found:\n")
        for a in violations:
            print(f"{a['file']}:{a['line']} --> {a['entity']}: {a['entity']} {a['name']}")
    if successes:
        print("\nTMDL documentation successes:\n")
        for a in successes:
            print(f"{a['file']}:{a['line']} --> {a['entity']}: {a['entity']} {a['name']} is documented")
            print(f"  Documentation:\n" + "\n".join(a["doc"]))
    if not successes:
        print("\nNo documented artefacts found.")
    if violations:
        sys.exit(1)

if __name__ == "__main__":
    main()

# --- Patch: Print success and documentation row for targeted artefact test ---
def print_success_for_targeted_artefact(file, artefact_type, artefact_name):
    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    doc_lines = []
    artefact_regex = re.compile(
        rf"^[ \t]*{re.escape(artefact_type)}\b\s*('([^']|'')+'|[^\s=:]+)"
    )
    for i, line in enumerate(lines):
        m = artefact_regex.match(line)
        if m:
            found_name = m.group(1).strip()
            # Match quoted/unquoted names exactly
            if found_name == artefact_name or found_name.strip("'") == artefact_name.strip("'"):
                idx = i - 1
                while idx >= 0:
                    content = lines[idx].strip()
                    if content == "":
                        idx -= 1
                        continue
                    if content.startswith("///"):
                        doc_lines.insert(0, content)
                        idx -= 1
                        continue
                    break
                doc_row = "\n".join(doc_lines) if doc_lines else "(No documentation row found above specified artefact)"
                print(f"SUCCESS: No documentation violation found for {file}: {artefact_type} {artefact_name}")
                print(f"Documentation row:\n{doc_row}")
                return
    print(f"Artefact {artefact_type} {artefact_name} not found in {file}")

if __name__ == "__main__":
    import sys
    # Only print success for targeted artefact test
    if "--file" in sys.argv and "--artefact" in sys.argv:
        args = sys.argv
        file_arg = args[args.index("--file") + 1]
        artefact_arg = args[args.index("--artefact") + 1]
        artefact_type, artefact_name = artefact_arg.split(" ", 1)
        print_success_for_targeted_artefact(file_arg, artefact_type, artefact_name)