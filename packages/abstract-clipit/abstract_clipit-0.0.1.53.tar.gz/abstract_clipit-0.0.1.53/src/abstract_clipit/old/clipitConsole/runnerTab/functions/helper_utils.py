from ..imports import *
import os

# ── helpers ──────────────────────────────────────────────────────────────
def _replace_log(self, text: str):
    try:
        self.log_view.clear()
        self.log_view.insertPlainText(text)
    except Exception as e:
        print(f"{e}")

def _parse_item(self, info: str):
    try:
        parts = info.rsplit(":", 2)
        if len(parts) == 3:
            path, line, col = parts[0], parts[1], parts[2]
        else:
            path, line, col = parts[0], parts[1], "1"
        return path, int(line), int(col)
    except Exception as e:
        print(f"{e}")

def _extract_errors_for_file(self, combined_text: str, abs_path: str, project_root: str) -> str:
    try:
        text = combined_text or ""
        if not text:
            return ""
        try:
            rel = os.path.relpath(abs_path, project_root) if (project_root and abs_path.startswith(project_root)) else os.path.basename(abs_path)
        except Exception:
            rel = os.path.basename(abs_path)
        rel_alt = rel.replace("\\", "/")
        abs_alt = abs_path.replace("\\", "/")
        base = os.path.basename(abs_alt)
        lines = text.splitlines()
        blocks = []
        for i, ln in enumerate(lines):
            if (abs_alt in ln) or (rel_alt in ln) or (("src/" + base) in ln):
                start = max(0, i - 3)
                end = min(len(lines), i + 6)
                block = "\n".join(lines[start:end])
                blocks.append(f"\n— context @ log line {i+1} —\n{block}\n")
        return "\n".join(blocks).strip()
    except Exception as e:
        print(f"{e}")

def create_radio_group(self, labels, default_index=0, slot=None):
    group = QButtonGroup(self)
    buttons = []
    for i, label in enumerate(labels):
        rb = QRadioButton(label)
        if i == default_index:
            rb.setChecked(True)
        group.addButton(rb)
        buttons.append(rb)
        if slot:
            rb.toggled.connect(slot)
    return group, buttons

_PREFERRED_EXT_ORDER = [".tsx",".ts",".jsx",".js",".mjs",".cjs",".tsx",".ts",".jsx",".js",".css",".scss",".less"]
def resolve_alt_ext(path: str, project_root: str) -> str:
    """
    If 'path' doesn't exist, try swapping extensions using a common React stack order.
    Also try replacing absolute project-root prefix with relative 'src/' and vice-versa.
    """
    try_paths = [path]
    base, ext = os.path.splitext(path)
    for e in _PREFERRED_EXT_ORDER:
        try_paths.append(base + e)

    # also try joining with project_root, and under src/
    if project_root and not path.startswith(project_root):
        rel = path.lstrip("./")
        try_paths.extend([
            os.path.join(project_root, rel),
            os.path.join(project_root, "src", os.path.basename(base)) + ext,
        ])
        for e in _PREFERRED_EXT_ORDER:
            try_paths.append(os.path.join(project_root, "src", os.path.basename(base)) + e)

    for candidate in try_paths:
        if os.path.isfile(candidate):
            return candidate
    return path  # fallback
