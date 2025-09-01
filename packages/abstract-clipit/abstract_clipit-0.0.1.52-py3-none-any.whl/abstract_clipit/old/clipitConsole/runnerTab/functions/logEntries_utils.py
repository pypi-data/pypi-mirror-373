from ...imports import *

def append_log(self, text):
    cursor = self.log_view.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    self.log_view.setTextCursor(cursor)
    self.log_view.insertPlainText(text)

def set_last_output(self, text: str):
    self.last_output = text or ""
    self.apply_log_filter()

def show_error_entries(self, entries):
    self.errors_list.clear()
    self.append_log(f"[dbg] show_error_entries entries={len(entries)} widget_id={id(self.errors_list)}\n")
    if self.cb_try_alt_ext.isChecked():
        entries = [(resolve_alt_ext(p, self.path_in.text().strip()), ln, col) for (p, ln, col) in entries]
    if not entries:
        self.append_log("\n✅ No matching errors.\n")
        return
    self.append_log("\nErrors found:\n")
    for path, line, col in entries:
        info = f"{path}:{line}:{col or 1}"
        self.append_log(info + "\n")
        self.errors_list.addItem(QListWidgetItem(info))

def show_warning_entries(self, entries):
    self.warnings_list.clear()
    if self.cb_try_alt_ext.isChecked():
        entries = [(resolve_alt_ext(p, self.path_in.text().strip()), ln, col) for (p, ln, col) in entries]
    if not entries:
        self.append_log("\nℹ️ No warnings.\n")
        return
    self.append_log("\nWarnings found:\n")
    for path, line, col in entries:
        info = f"{path}:{line}:{col or 1}"
        self.append_log(info + "\n")
        self.warnings_list.addItem(QListWidgetItem(info))

def apply_log_filter(self):
    if self.rb_err.isChecked():
        self._replace_log(self.last_errors_only or "(no errors)")
    elif self.rb_wrn.isChecked():
        self._replace_log(self.last_warnings_only or "(no warnings)")
    else:
        self._replace_log(self.last_output or "")
