# clipit/__init__.py

import os
import sys
import threading
import webbrowser

from PyQt5 import QtCore, QtWidgets

from .clipit import gui_main, gui_web
from .clipit.client import client_main
from .clipit.clipit_flask import abstract_clip_app
from abstract_utilities import *

# ── ENVIRONMENT: force Qt into software OpenGL ─────────────────────────────────

# Disable hardware GLX/EGL:
os.environ["QT_XCB_GL_INTEGRATION"] = "none"
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseSoftwareOpenGL)

def get_args(*args):
    args = args or tuple(make_list(sys.argv or ()))
    return args
def get_arg(args,i=0,lower=False,integer=False,default = None):
    args = get_args(*args)
    args_length = len(args)
    arg = args[i] if args_length > i else default
    if arg and lower:
        typ = type(arg)
        nu_arg = arg
        try:
            nu_arg = str(arg).lower()
        except:
            pass
        
        try:
            nu_arg = typ(nu_arg)
        except:
            pass
        arg = nu_arg
    if arg and integer:
        arg = int(arg) if arg and is_number(arg) else default
    return arg
# ── FLASK LAUNCHER ───────────────────────────────────────────────────────────────

def run_flask(port: int | None = None) -> None:
    """
    Start the Flask app on `port` (defaults to 7823), then open the browser.
    """
    port = port or 7823
    app = abstract_clip_app()
    url = f"http://127.0.0.1:{port}/drop-n-copy.html"

    print(f"→ Opening browser to: {url}")
    # Slight delay so Flask has time to bind before opening the browser:
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(debug=True, port=port)


# ── MODE DISPATCHER ──────────────────────────────────────────────────────────────

def initialize_clipit(choice: str = "display", *, port: int | None = None, url: str | None = None) -> None:
    """
    Dispatch based on `choice`:
      - "display": run the PyQt GUI (`gui_main`)
      - "web":     run the PyQt web‐view GUI (`gui_web(url)`)
      - "client":  run the CLI client (`client_main`)
      - "script":  (not implemented)
      - "flask":   launch the Flask + browser (`run_flask(port)`)
    """
    choice = choice.lower()
    if choice == "display":
        gui_main()

    elif choice == "web":
        if not url:
            print_or_log("When choice=='web', you must pass a `url` argument.")
        gui_web(url)

    elif choice == "client":
        client_main()

    elif choice == "script":
        print("Running in script mode (not implemented).")

    elif choice == "flask":
        run_flask(port=port)

    else:
        raise ValueError(f"Unknown mode: {choice!r}")


# ── ENTRY POINT ─────────────────────────────────────────────────────────────────

def clipit_main(*argv: str) -> None:
    """
    Parse sys.argv and call initialize_clipit appropriately.

    Usage patterns:
      $ python -m clipit               →   display mode
      $ python -m clipit display       →   display mode
      $ python -m clipit web  http://… →   web mode
      $ python -m clipit flask 7823    →   flask mode
      $ python -m clipit client        →   client mode
    """
    
    choice = get_arg(args=argv,i=0,lower=True,default="display")
    if choice in ["web","flask"]:
        if choice == "web":
            url = get_arg(args=argv,i=1)
            
            # Expect: python -m clipit web <url>
            initialize_clipit("web", url=url)
        elif choice == "flask":
            # Expect: python -m clipit flask <port
            port = get_arg(args=argv,i=1,integer=True,default=7823)
            initialize_clipit("flask", port=port)
    # argv[0] is the module name (e.g. "-m clipit"); so look at argv[1], argv[2]
    else:
        # No mode specified → default to "display"
        initialize_clipit("display")
        return



def run_clipit(*args):
    args = get_args(*args)
    clipit_main(*args)
