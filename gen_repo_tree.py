#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess

def prompt_yes_no(prompt="(y/n): "):
    try:
        ans = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(1)
    return ans in ("y", "yes")

def list_entries(path):
    try:
        with os.scandir(path) as it:
            entries = [(e.name, e.is_dir(follow_symlinks=False), e.is_symlink(), e.path) for e in it]
    except PermissionError:
        return [("[permission denied]", False, False, None)]
    # Directories first, then files; case-insensitive sort
    entries.sort(key=lambda x: (0 if x[1] else 1, x[0].lower()))
    return entries

def build_tree_lines(root_path):
    root_name = os.path.basename(os.path.abspath(root_path))
    lines = [f"{root_name}/"]

    def recurse(path, prefix_parts):
        entries = list_entries(path)
        count = len(entries)
        for idx, (name, is_dir, is_link, full_path) in enumerate(entries):
            is_last = (idx == count - 1)
            connector = "└── " if is_last else "├── "
            prefix = "".join(prefix_parts) + connector

            display_name = name
            if is_dir and name != "[permission denied]":
                display_name += "/"
            if is_link:
                display_name += " -> (symlink)"

            lines.append(prefix + display_name)

            if is_dir and full_path is not None and name != "[permission denied]":
                recurse(full_path, prefix_parts + [("    " if is_last else "│   ")])

    recurse(root_path, [])
    return lines

def write_output(lines, root_path):
    root_name = os.path.basename(os.path.abspath(root_path))
    outfile = f"{root_name} repo.txt"
    with open(outfile, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return outfile

def open_with_default_app(filepath):
    try:
        if sys.platform.startswith("darwin"):  # macOS
            subprocess.run(["open", filepath], check=False)
        elif os.name == "nt":  # Windows
            os.startfile(filepath)  # type: ignore
        else:  # Linux and others
            subprocess.run(["xdg-open", filepath], check=False)
    except Exception as e:
        print(f"Could not open file automatically: {e}")

def open_in_vscode(paths):
    # Find VS Code CLI
    code_cmd = shutil.which("code") or shutil.which("code.cmd") or shutil.which("code.exe")
    if not code_cmd:
        print("VS Code command 'code' not found on PATH. Skipping VS Code open.")
        return

    # Filter to existing paths
    existing = [p for p in paths if os.path.exists(p)]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        for m in missing:
            print(f"Ignored (not found): {m}")

    if not existing:
        print("No valid paths to open in VS Code.")
        return

    try:
        subprocess.run([code_cmd, *existing], check=False)
        print("Opened in VS Code:", ", ".join(existing))
    except Exception as e:
        print(f"Could not open in VS Code: {e}")

def main():
    if not prompt_yes_no("Generate tree? (y/n): "):
        print("Okay, not generating a tree.")
        return

    root_path = os.getcwd()
    try:
        lines = build_tree_lines(root_path)
        outfile = write_output(lines, root_path)
    except Exception as e:
        print(f"Error while generating or writing tree: {e}", file=sys.stderr)
        sys.exit(1)

    print(f'Done! Wrote repo tree to "{outfile}". Opening file...')
    open_with_default_app(outfile)

    # Ask about opening files in VS Code
    if prompt_yes_no("open files? (vscode) y/n: "):
        try:
            raw = input('enter the file path and file(s) like "apps/server/prisma/seed.ts" (comma-separated): ').strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSkipped opening files.")
            raw = ""

        if raw:
            # Split by comma, strip whitespace and quotes, resolve relative to current directory
            parts = [p.strip().strip('"').strip("'") for p in raw.split(",")]
            norm_paths = [os.path.normpath(os.path.join(root_path, p)) if not os.path.isabs(p) else os.path.normpath(p)
                          for p in parts if p]
            open_in_vscode(norm_paths)
        else:
            print("No paths provided. Skipping VS Code open.")

    # Finally, ask to save or delete the txt
    if not prompt_yes_no("Save repo tree txt file? (y/n): "):
        try:
            os.remove(outfile)
            print("File deleted.")
        except Exception as e:
            print(f"Could not delete file: {e}")
    else:
        print("File saved.")

if __name__ == "__main__":
    main()
