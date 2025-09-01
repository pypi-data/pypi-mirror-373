from .imports import *
from .initFuncs import initFuncs
from ..FileSystemTree import FileSystemTree
from ..FileDropArea import FileDropArea
class clipitConsole(QtWidgets.QWidget):
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

        createButton(self,
                        layout=toolbar,
                        connect={"callbacks":self._toggle_logs,"signals":"toggled"},
                        text="Toggle Logs",
                        attr_name='toggle_logs_action',
                        setCheckable=True
                               )
        createButton(self,
                     layout=toolbar,
                     connect={"callbacks":self._toggle_view,"signals":"toggled"},
                     text="Toggle View",
                     attr_name='toggle_view_action',
                     setCheckable=True
                     )

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

clipitConsole = initFuncs(clipitConsole)
