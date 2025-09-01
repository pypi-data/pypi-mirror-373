# ─── Third-party ──────────────────────────────────────────────────────────────
from .imports import *
from abstract_utilities import *
from abstract_paths import *
logger = get_logFile('clipit_logs')
def copy_to_clipboard(text=None):
    clipboard.copy(text)

def log_it(self, message: str):
    """Append a line to the shared log widget, with timestamp."""
    timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
    logger.info(f"[{timestamp}] {message}")
    self.log_widget.append(f"[{timestamp}] {message}")
    
def _log(self, m: str):
    """Helper to write to both QTextEdit and Python logger."""
    logger.debug(m)
    log_it(self, m)

def _clear_layout(layout: QtWidgets.QLayout):
    """Recursively delete all widgets in a layout (Qt-safe)."""
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().setParent(None)      # detach
            item.widget().deleteLater()        # mark for deletion
        elif item.layout():
            _clear_layout(item.layout())
def unlist(obj):
    if obj and isinstance(obj, list):
        obj = obj[0]
    return obj
def get_all_dir_pieces(file_paths: List[str]) -> List[str]:
    """Extract unique directory components, excluding root-like components."""
    all_pieces = set()
    for file_path in file_paths:
        path = Path(file_path)
        for parent in path.parents:
            name = parent.name
            if name:
                all_pieces.add(name)
    return sorted(list(all_pieces))
def is_string_in_dir(path,strings):
    dirname =  path
    if os.path.isfile(path):
        dirname = os.path.dirname(path)
    pieces = [pa for pa in dirname.split('/') if pa and pa in strings]
    logger.info(f"pieces = {pieces}\nstrings == {strings}")
    if pieces:
        return True
    return False
def is_in_exts(path,exts,visible_dirs):
    logger.info(f"path = {path}\nexts == {exts}")
    if is_string_in_dir(path,visible_dirs):
        return True
    if os.path.isdir(path):
        return True
    ext = os.path.splitext(path)[1].lower()
    if ext in exts:
        return True
    return 

def split_clipit_sections(clipit_sections):
    return clipit_sections.split('――――――――――――――――――')
def get_clipit_sections_lines(clipit_sections):
    clipit_sections = split_clipit_sections(clipit_sections)
    return [section.split('\n') for secion in clipit_sections if section]
def get_all_clipit_file_paths_and_sections(clipit_sections):
    clipit_sections_lines = get_clipit_sections_lines(clipit_sections)
    sections=[]
    for j,lines in enumerate(clipit_sections_lines):
        for i,line in enumerate(lines):
            line = eatAll(line,[' ','\n','\t','"',"'"])
            if line.startswith('==='):
                file_path = eatAll(line,[' ','\n','\t','='])
                file_paths.append(file_path)
                content = '\n'.join(lines[i+1:])
                content = eatAll(content,[' ','\n','\t','"',"'"])
                sections.append({"file_path":file_path,"section":content})
    return sections
def save_from_clipit_section(section):
    file_path = section.get("file_path")
    content = section.get("section")
    write_to_file(contents = content,file_path=file_path)
def save_clipit_sections(sections):
    for section in sections:
        save_from_clipit_section(section)
def get_save_clipit_sections(clipit_sections):
    sections = get_all_clipit_file_paths_and_sections(clipit_sections)
    save_clipit_sections(sections)
def get_allowed_clipit_sections(
    clipit_sections,                        
    allowed_exts: Optional[Set[str]] = False,
    unallowed_exts: Optional[Set[str]] = False,
    exclude_types: Optional[Set[str]] = False,
    exclude_dirs: Optional[List[str]] = False,
    exclude_patterns: Optional[List[str]] = False
    ):
    CFG = derive_file_defaults(
            allowed_exts = allowed_exts,
            unallowed_exts = unallowed_exts,
            exclude_types = exclude_types,
            exclude_dirs = exclude_dirs,
            exclude_patterns = exclude_patterns,
            add = add
        )
    
    
    is_allowed = make_allowed_predicate(GFC)
    sections = get_all_clipit_file_paths_and_sections(clipit_sections)
    file_paths = [item.get('file_path') for item in sections]
    allowed_paths = get_allowed_files(file_paths,allowed=is_allowed)
    sections = [item for item in sections if item and item.get('file_path') in allowed_paths]
    return sections
def get_save_allowed_clipit_sections(
    clipit_sections,                        
    allowed_exts: Optional[Set[str]] = False,
    unallowed_exts: Optional[Set[str]] = False,
    exclude_types: Optional[Set[str]] = False,
    exclude_dirs: Optional[List[str]] = False,
    exclude_patterns: Optional[List[str]] = False
    ):
    sections = get_allowed_clipit_sections(
            clipit_sections,                        
            allowed_exts=allowed_exts,
            unallowed_exts=unallowed_exts,
            exclude_types=exclude_types,
            exclude_dirs=exclude_dirs,
            exclude_patterns=exclude_patterns
        )
    save_clipit_sections(sections)
    
def get_text_view(combined_text_lines,view_toggle):
    parts = []
    for path, info in self.combined_text_lines.items():
        if not info.get('visible', True):
            continue
        lines = info['text']
        if view_toggle != 'print':
            lines = [lines[0], repr(lines[1]), lines[-1]]
        seg = "\n".join(lines)
        parts.append(seg)
    final = "\n\n".join(parts)
    return final
