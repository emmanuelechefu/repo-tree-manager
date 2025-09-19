# Repo Manager and Display

A simple Python utility to **generate a repo tree** and **open files in VS Code** from your project folder.  
Think of it as a lightweight, interactive helper for inspecting and navigating your repo.

---

## Features
- Interactive menu with:
  - `h` → Help / how to use
  - `1` → Generate repo tree (with depth control)
  - `2` → Open one or more files in VS Code
  - `q` → Quit
- Saves the repo structure to `<root-folder> repo.txt`
- Automatically opens the generated `repo.txt` in your default editor
- Lets you choose to save or delete the file afterward
- Handles symlinks safely (does not follow them)
- Displays `[permission denied]` for restricted directories
- Cross-platform (Linux, macOS, Windows)

---

## Requirements
- Python **3.7+**
- [Visual Studio Code](https://code.visualstudio.com/) (for option `2`)
  - Make sure the `code` command is available in your terminal  
    (run **“Shell Command: Install 'code' command in PATH”** from VS Code command palette on macOS, or ensure it's added on Windows/Linux).

---

## Installation
Clone or copy the script into your repo root:

```bash
git clone <your-repo-url>
cd <your-repo>
