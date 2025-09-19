#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess

TITLE = "REPO MANAGER AND DISPLAY"

def prompt_yes_no(prompt="(y/n): "):
    try:
        ans = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(1)
    return ans in ("y", "yes")

def input_line(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(1)

# ---------- Tree building ----------
def list_entries(path):
    try:
        with os.scandir(path) as it:
            entries = [(e.name, e.is_dir(follow_symlinks=False), e.is_symlink(), e.path) for e in it]
    except PermissionError:
        return [("[permission denied]", False, False, None)]
    entries.sort(key=lambda x: (0 if x[1] else 1, x[0].lower()))
    return entries

def build_tree_lines(root_path, max_depth=None):
    root_name = os.path.basename(os.path.abspath(root_path))
    lines = [f"{root_name}/"]

    def recurse(path, prefix_parts, depth):
        if max_depth is not None and depth >= max_depth:
            return
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
                next_prefix = ("    " if is_last else "│   ")
                recurse(full_path, prefix_parts + [next_prefix], depth + 1)

    recurse(root_path, [], 0)
    return lines

def write_output(lines, root_path):
    root_name = os.path.basename(os.path.abspath(root_path))
    outfile = f"{root_name} repo.txt"
    with open(outfile, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return outfile

# ---------- File opening ----------
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
    code_cmd = shutil.which("code") or shutil.which("code.cmd") or shutil.which("code.exe")
    if not code_cmd:
        print("VS Code command 'code' not found on PATH. Install VS Code or add 'code' to PATH.")
        return
    existing = [p for p in paths if os.path.exists(p)]
    missing = [p for p in paths if not os.path.exists(p)]
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

# ---------- UI ----------
def show_menu():
    print("\n" + "=" * 48)
    print(f"{TITLE}")
    print("=" * 48)
    print("How to use (h)")
    print("generate repo tree (1)")
    print("open file in repo (2)")
    print("Quit (q)")

def show_help():
    help_text = f"""
{TITLE} — Help

- Press '1' to generate a repo tree of the current folder.
  • You will be asked for a depth:
      - Leave blank for unlimited depth
      - Or enter a number (e.g., 2) to limit nesting
  • The tree is saved to "<root folder> repo.txt" and opened automatically.
  • Then you’ll be asked "Save txt? (y/n)":
      - y  -> keep the file
      - n  -> delete the file

- Press '2' to open one or more files in VS Code:
  • Enter relative or absolute paths
  • Separate multiple paths with commas
  • Missing/invalid paths are ignored

- Press 'h' to see this help again.
- Press 'q' to quit.

Notes:
- Symlinks are indicated and not followed to avoid cycles.
- Permission-restricted directories are displayed as [permission denied].
"""
    print(help_text.strip())

def parse_depth(s):
    s = s.strip()
    if s == "":
        return None
    try:
        n = int(s)
        if n < 0:
            raise ValueError
        return n
    except ValueError:
        print("Invalid depth. Using unlimited.")
        return None

def action_generate_tree():
    depth_str = input_line("Enter depth (blank for unlimited): ")
    max_depth = parse_depth(depth_str)

    root_path = os.getcwd()
    try:
        lines = build_tree_lines(root_path, max_depth=max_depth)
        outfile = write_output(lines, root_path)
    except Exception as e:
        print(f"Error while generating or writing tree: {e}", file=sys.stderr)
        return

    print(f'Done! Wrote repo tree to "{outfile}". Opening...')
    open_with_default_app(outfile)

    if not prompt_yes_no("Save txt? (y/n): "):
        try:
            os.remove(outfile)
            print("File deleted.")
        except Exception as e:
            print(f"Could not delete file: {e}")
    else:
        print("File saved.")

def action_open_files_vscode():
    raw = input_line('Enter file path(s) like "apps/server/prisma/seed.ts" (comma-separated): ').strip()
    if not raw:
        print("No paths provided.")
        return
    parts = [p.strip().strip('"').strip("'") for p in raw.split(",")]
    root_path = os.getcwd()
    norm_paths = [
        os.path.normpath(os.path.join(root_path, p)) if not os.path.isabs(p) else os.path.normpath(p)
        for p in parts if p
    ]
    open_in_vscode(norm_paths)

def main():
    while True:
        show_menu()
        choice = input_line("> ").strip().lower()
        if choice == "q":
            print("Goodbye!")
            break
        elif choice == "h":
            show_help()
        elif choice == "1":
            action_generate_tree()
        elif choice == "2":
            action_open_files_vscode()
        else:
            print("Unknown option. Choose h, 1, 2, or q.")

if __name__ == "__main__":
    main()
