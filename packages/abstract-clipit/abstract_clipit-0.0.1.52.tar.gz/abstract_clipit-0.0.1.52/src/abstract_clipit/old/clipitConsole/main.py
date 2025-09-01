#!/usr/bin/env python3
# main.py

import os
#os.environ["QT_XCB_GL_INTEGRATION"] = "none"
from .imports import *
#QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseSoftwareOpenGL)
from .clipitConsole import clipitConsole
from .FileDropArea  import FileDropArea
from .FileSystemTree import FileSystemTree
from .JSBridge import JSBridge
from .imports import *
import sys

def gui_main():
    clipitConsole(
        FileDropArea=FileDropArea,
        FileSystemTree=FileSystemTree
        )

def gui_web(target_url=None):
    from .JSBridge import JSBridge
    app = QtWidgets.QApplication(sys.argv)

    # Pass the URL into the constructor of your widget
    window = DragDropWithWebBrowser(
        FileDropArea=FileDropArea,
        FileSystemTree=FileSystemTree,
        JSBridge=JSBridge,
        url=target_url,                 # new parameter
    )
    window.show()
    sys.exit(app.exec_())


