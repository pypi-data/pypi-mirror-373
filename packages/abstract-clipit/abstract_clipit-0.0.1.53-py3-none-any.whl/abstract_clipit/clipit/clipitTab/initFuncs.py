from .imports import *
from .functions import *
def initFuncs(self):
    try:
        for f in (on_file_save_sections, _log, _toggle_logs, _toggle_view, on_file_selected, on_function_selected, on_tree_copy, on_tree_double_click):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
