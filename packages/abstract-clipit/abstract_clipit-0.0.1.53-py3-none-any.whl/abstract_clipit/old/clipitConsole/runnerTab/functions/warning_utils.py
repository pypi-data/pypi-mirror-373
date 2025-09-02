from ..imports import *
import subprocess, traceback, os

def build_warnings_list(self):
    """
    QListWidget pre-wired with:
      • click  -> open + filtered log view
      • dblclick -> open only
    """
    lw = QListWidget()

    def _resolve(path: str) -> str:
        try:
            if self.cb_try_alt_ext.isChecked():
                return resolve_alt_ext(path, self.path_in.text().strip())
        except Exception:
            pass
        return path

    def _open_in_vscode(path: str, line: int, col: int | None):
        subprocess.run(["code", "-g", f"{path}:{line}:{(col or 1)}"], check=False)

    def on_click(item: QListWidgetItem):
        try:
            text = item.text()
            path, line, col = self._parse_item(text)
            path = _resolve(path)
            _open_in_vscode(path, line, col)
            snippet = self._extract_errors_for_file(
                self.last_output, path, self.path_in.text().strip()
            )
            self._replace_log(snippet if snippet else f"(No specific lines found for {path})\n\n{self.last_output}")
        except Exception:
            self.append_log("show_error_for_item error:\n" + traceback.format_exc() + "\n")

    def on_dblclick(item: QListWidgetItem):
        try:
            text = item.text()
            path, line, col = self._parse_item(text)
            path = _resolve(path)
            _open_in_vscode(path, line, col)
        except Exception:
            self.append_log("open_in_editor error:\n" + traceback.format_exc() + "\n")

    lw.itemClicked.connect(on_click)
    lw.itemDoubleClicked.connect(on_dblclick)
    return lw
