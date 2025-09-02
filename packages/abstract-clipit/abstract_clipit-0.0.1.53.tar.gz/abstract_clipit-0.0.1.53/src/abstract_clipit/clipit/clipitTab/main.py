from .imports import *
from .initFuncs import initFuncs
from ..FileSystemTree import FileSystemTree
from ..FileDropArea import FileDropArea
class clipitTab(QtWidgets.QWidget):
    """
    Main window: toolbar + splitter:
      • Left: FileSystemTree
      • Right: FileDropArea
      • Bottom: QTextEdit for logs
    """

    def __init__(self,*args,**kwargs):
        super().__init__()

        title = "ClipIt - File Browser + Drag/Drop + Logs"
        size=(950, 600)
        make_main_window(parent=self,
                         title=title,
                         size=size)
        main_layout = get_layout(parent=self)
        
        # 1) Toolbar with “Toggle Logs”
        toolbar = make_toolbar(self)

        btn_logs = QPushButton("Toggle Logs", self)
        btn_logs.setCheckable(True)
        btn_logs.toggled.connect(self._toggle_logs)
        toolbar.addWidget(btn_logs)
        self.toggle_logs_action = btn_logs   # keep the attribute name you use elsewhere

        btn_view = QPushButton("Toggle View", self)
        btn_view.setCheckable(True)
        btn_view.toggled.connect(self._toggle_view)
        toolbar.addWidget(btn_view)
        self.toggle_view_action = btn_view

        
        clipped_save = QPushButton("save_clipped", self)
        clipped_save.setCheckable(True)
        clipped_save.toggled.connect(self.on_file_save_sections)
        toolbar.addWidget(clipped_save)
        self.toggle_save_clipped = clipped_save

        self.view_widget = 'array'
        # 2) Splitter: left = FileSystemTree; right = FileDropArea
        splitter = QtWidgets.QSplitter(
            QtCore.Qt.Orientation.Horizontal,  # was just "QtCore.Orientation"
            self
        )
        # Shared log widget (initially hidden)
        self.log_widget = get_log_widget(style="background:#111; color:#eee; font-family:monospace;")

        # Left pane: FileSystemTree
        self.tree_wrapper = FileSystemTree(log_widget=self.log_widget, parent=self)
        
        # Right pane: FileDropArea
        self.drop_area = FileDropArea(log_widget=self.log_widget,view_widget=self.view_widget, parent=self)

        add_widgets(splitter,
                    {"widget":self.tree_wrapper},
                    {"widget":self.drop_area}
                    )
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        add_widgets(main_layout,
                    {"widget":toolbar,
                     "kwargs":{"stretch":1}},
                    {"widget":splitter},
                    {"widget":self.log_widget}
                    
                    )
        # 3) Bottom: the log console (hidden until toggled)
        
        self.setLayout(main_layout)

        # ─── Hook up tree signals ─────────────────────────────────────────────────
        self.tree_wrapper.tree.doubleClicked.connect(self.on_tree_double_click)
        self.drop_area.function_selected.connect(self.on_function_selected)
        self.drop_area.file_selected.connect(self.on_file_selected)

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
    def _toggle_logs(self, checked: bool):
        """
        Show/hide the log console when the toolbar action is toggled.
        """
        if checked:
            self.log_widget.show()
            self.toggle_logs_action.setText("Hide Logs")
            self._log("Logs shown.")
        else:
            self._log("Logs hidden.")
            self.log_widget.hide()
            self.toggle_logs_action.setText("Show Logs")

    def _toggle_view(self, checked: bool):
        """
        Show/hide the log console when the toolbar action is toggled.
        """
        if checked:
            self.view_widget = 'array'
            self.toggle_view_action.setText("View Print")
            self._log("View Array.")
        else:
            self._log("View Print.")
            self.view_widget = 'print'
            self.toggle_view_action.setText("View Array")
        self.drop_area._toggle_populate_text_view(view_toggle=self.view_widget)
    def on_tree_copy(self, paths: List[str]):
        """
        Called when the “Copy Selected” button is pressed.
        We log how many items, then forward to drop_area.
        """
        self._log(f"Copy Selected triggered on {len(paths)} path(s).")
        self.drop_area.process_files(paths)

    def on_tree_double_click(self, index: QtCore.QModelIndex):
        model = self.tree_wrapper.model
        path = model.filePath(index)
        if path:
            self._log(f"Double-clicked: {path}")
            self.drop_area.process_files([path])

    def on_function_selected(self, function_info: dict):
        """
        Handle function selection: map imports and project reach, then copy to clipboard.
        """
        self._log(f"Function selected: {function_info['name']} from {function_info['file']}")
        self.drop_area.map_function_dependencies(function_info)

    def on_file_selected(self, file_info: dict):
        """
        Handle Python file selection: map import chain, then copy to clipboard.
        """
        self._log(f"Python file selected: {file_info['path']}")
        self.drop_area.map_import_chain(file_info)

    def _log(self, message: str):
        """Write to the shared log widget with a timestamp."""
        log_it(self=self, message=message)


