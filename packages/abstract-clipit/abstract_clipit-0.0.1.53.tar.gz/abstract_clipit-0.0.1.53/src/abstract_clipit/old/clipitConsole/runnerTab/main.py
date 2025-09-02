from abstract_gui.QT6 import QWidget, QVBoxLayout, QHBoxLayout, QLabel, getListBox, getRow
from .initFuncs import initFuncs

class runnerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initializeInit()

        root = QVBoxLayout(self)     # root layout ON self
        # (don’t bother with an intermediate 'page' unless you really need it)

        top = QHBoxLayout()
        top.addWidget(QLabel("User:")); top.addWidget(self.user_in, 2)
        top.addWidget(QLabel("Path:")); top.addWidget(self.path_in, 3)
        top.addWidget(self.run_btn); top.addWidget(self.rerun_btn); top.addWidget(self.clear_btn)
        root.addLayout(top)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Log Output:")); filter_row.addStretch(1)
        filter_row.addWidget(self.rb_all); filter_row.addWidget(self.rb_err); filter_row.addWidget(self.rb_wrn)
        filter_row.addWidget(self.cb_try_alt_ext)
        root.addLayout(filter_row)

        root.addWidget(self.log_view, 3)

        left  = getListBox((self.errors_list,   "Errors (file:line:col):", 1))
        right = getListBox((self.warnings_list, "Warnings (file:line:col):", 1))
        root.addLayout(getRow(left, right), 2)


runnerTab = initFuncs(runnerTab)
