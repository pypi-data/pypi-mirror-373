from ..imports import *
def on_file_save_sections(self):
    combined_text_lines = self.combined_text_lines
    view_toggle = self.view_toggle
    text_view = get_text_view(
        combined_text_lines= combined_text_lines,
        view_toggle = view_toggle
        )
    save_clipit_sections(text_view)
def on_file_get_sections(self):
    combined_text_lines = self.combined_text_lines
    view_toggle = self.view_toggle
    text_view = get_text_view(
        combined_text_lines= combined_text_lines,
        view_toggle = view_toggle
        )
    return get_all_clipit_file_paths(text_view)
def populate_python_view(self) -> None:
    try:
        self.python_file_list.clear()
        all_paths = [info['path'] for info in self.python_files]
        filtered_set = set(self.filter_paths(self._last_raw_paths))
        for p in all_paths:
            item = QtWidgets.QListWidgetItem(os.path.basename(p))
            item.setData(QtCore.Qt.UserRole, p)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked if p in filtered_set else QtCore.Qt.Unchecked)
            self.python_file_list.addItem(item)
        self.python_file_list.setVisible(bool(all_paths))
    except Exception as e:
        print(f"{e}")
def _populate_list_view(self) -> None:
    try:
        self.function_list.clear()
        if self.functions:
            for func in self.functions:
                itm = QtWidgets.QListWidgetItem(f"{func['name']} ({func['file']})")
                itm.setFlags(itm.flags() | QtCore.Qt.ItemIsUserCheckable)
                itm.setCheckState(QtCore.Qt.Unchecked)
                self.function_list.addItem(itm)
            self.function_list.setVisible(True)
        else:
            self.function_list.setVisible(False)
        self.populate_python_view()
    except Exception as e:
        print(f"{e}")

def _populate_text_view(self) -> None:
    try:
        if not self.combined_text_lines:
            self.text_view.clear()
            self.text_view.setVisible(False)
            return
        parts = []
        for path, info in self.combined_text_lines.items():
            if not info.get('visible', True):
                continue
            lines = info['text']
            if self.view_toggle != 'print':
                lines = [lines[0], repr(lines[1]), lines[-1]]
            seg = "\n".join(lines)
            parts.append(seg)
        final = "\n\n".join(parts)
        self.text_view.setPlainText(final)
        self.text_view.setVisible(bool(final))
        copy_to_clipboard(final)
    except Exception as e:
        print(f"{e}")

def _toggle_populate_text_view(self, view_toggle=None) -> None:
    try:
        if view_toggle:
            self.view_toggle = view_toggle
        self._populate_text_view()
    except Exception as e:
        print(f"{e}")
