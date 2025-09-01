from ...imports import *
# imports (PyQt6)
from PyQt6.QtCore import QProcess, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QListWidgetItem
import os, shutil, traceback
# ── click handlers ───────────────────────────────────────────────────────
def show_error_for_item(self, item):
    info = item.text()
    try:
        path, line, col = self._parse_item(info)
        if self.cb_try_alt_ext.isChecked():
            path = resolve_alt_ext(path, self.path_in.text().strip())
        os.system(f'code -g "{path}:{line}:{col or 1}"')
        snippet = self._extract_errors_for_file(self.last_output, path, self.path_in.text().strip())
        self._replace_log(snippet if snippet else f"(No specific lines found for {path})\n\n{self.last_output}")
    except Exception:
        self.append_log("show_error_for_item error:\n" + traceback.format_exc() + "\n")

def open_in_editor(self, item: QListWidgetItem):
    try:
        text = item.text()
        path, line, col = self._parse_item(text)
        if self.cb_try_alt_ext.isChecked():
            path = resolve_alt_ext(path, self.path_in.text().strip())
        target = f"{path}:{line}:{col or 1}"

        # prefer VS Code if available (platform-aware)
        candidates = ["code"]
        if os.name == "nt":
            candidates = ["code.cmd", "code.exe", "code"]

        for cmd in candidates:
            if shutil.which(cmd):
                # -g path:line[:col]
                QProcess.startDetached(cmd, ["-g", target])
                return

        # fallback: open the file without line:col via OS handler
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    except Exception:
        self.append_log("open_in_editor error:\n" + traceback.format_exc() + "\n")


def _pick_build_cmd(self, project_dir: str):
    # choose yarn/pnpm/npm by lockfile
    if os.path.exists(os.path.join(project_dir, "yarn.lock")):
        return "yarn", ["build"]
    if os.path.exists(os.path.join(project_dir, "pnpm-lock.yaml")):
        return "pnpm", ["build"]
    return "npm", ["run", "build"]

def _run_build_qprocess(self, project_dir: str):
    # keep GUI responsive
    self.proc = QProcess(self)
    self.proc.setWorkingDirectory(project_dir)
    self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

    tool, args = self._pick_build_cmd(project_dir)

    sh = f'''
        set -e
        if [ -s "$HOME/.nvm/nvm.sh" ]; then . "$HOME/.nvm/nvm.sh"; fi
        if command -v corepack >/dev/null 2>&1; then corepack enable >/dev/null 2>&1 || true; fi
        {tool} --version >/dev/null 2>&1 || true
        {"yarn install --frozen-lockfile &&" if tool=="yarn" else ""}
        {"pnpm install --frozen-lockfile &&" if tool=="pnpm" else ""}
        {"npm ci &&" if tool=="npm" else ""}
        {tool} {" ".join(args)}
    '''.strip()

    # wire output/finish/error (Qt6 signal enums)
    self.proc.readyReadStandardOutput.connect(self._on_build_output)
    self.proc.finished.connect(self._on_build_finished)
    self.proc.errorOccurred.connect(self._on_build_error)

    self.run_btn.setEnabled(False)
    self.append_log(f"[build] cwd={project_dir}\n")

    # clearer in Qt6 than start("bash", ["-lc", ...])
    self.proc.setProgram("bash")
    self.proc.setArguments(["-lc", sh])
    self.proc.start()

def _on_build_output(self):
    try:
        chunk = bytes(self.proc.readAllStandardOutput()).decode("utf-8", "ignore")
        if chunk:
            self.append_log(chunk)
    except Exception:
        self.append_log("readAllStandardOutput error:\n" + traceback.format_exc() + "\n")

def _on_build_finished(self, code: int, status):
    # status is QProcess.ExitStatus, kept generic for simplicity
    self.append_log(f"\n\n[build] exited with code {code}\n")
    self.run_btn.setEnabled(True)

def _on_build_error(self, err):
    # err is QProcess.ProcessError
    self.append_log(f"\n[build] QProcess error: {err}\n")
    self.run_btn.setEnabled(True)
