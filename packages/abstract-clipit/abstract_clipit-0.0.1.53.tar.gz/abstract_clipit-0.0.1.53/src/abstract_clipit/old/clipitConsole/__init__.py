from .clipitConsole import clipitConsole
from .imports import QApplication,install_global_traps
import traceback,sys
def startClipitConsole():
    try:
        install_global_traps()  # ← add this
        app = QApplication(sys.argv)
        win = clipitConsole()
        win.show()
        return app.exec()
    except Exception:
        print(traceback.format_exc())
        return 1

