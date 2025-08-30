from ..imports import *
# utils.py
##def decl_kinds(code: str) -> Dict[str, str]:
##    """
##    Return {name: kind} where kind in {'function','class','const','let','var'}.
##    """
##    kinds: Dict[str, str] = {}
##
##    # function Foo() {}
##    for m in RE_FN_DECL.finditer(code):
##        kinds[m.group(1)] = 'function'
##
##    # class Foo {}
##    for m in RE_CLASS_DECL.finditer(code):
##        kinds[m.group(1)] = 'class'
##
##    # --- NEW: function/class expressions assigned to variables ----------------
##    RE_VAR_FN = re.compile(
##        r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*'
##        r'(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)'
##    )
##    RE_VAR_CLASS = re.compile(
##        r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*class\b'
##    )
##
##    for m in RE_VAR_FN.finditer(code):
##        kinds[m.group(1)] = 'function'
##
##    for m in RE_VAR_CLASS.finditer(code):
##        kinds[m.group(1)] = 'class'
##
##    # const/let/var a = 1, b = 2, c;
##    # Only mark as variable if not already upgraded to function/class above.
##    for m in RE_VAR_BLOCK.finditer(code):
##        k = m.group('kind')  # const|let|var
##        lst = m.group('list')
##        for piece in lst.split(','):
##            name = piece.strip().split('=')[0].strip()
##            if name and re.match(r'^[A-Za-z_$][\w$]*$', name):
##                kinds.setdefault(name, k)
##
##    return kinds
# in utils/utils.py (decl_kinds)
def decl_kinds(code: str) -> Dict[str, str]:
    kinds = {}
    for m in RE_FN_DECL.finditer(code):
        kinds[m.group(1)] = 'function'
    for m in RE_CLASS_DECL.finditer(code):
        kinds[m.group(1)] = 'class'

    # NEW: treat const/let/var assigned to a function/arrow as 'function'
    for m in RE_VAR_ASSIGNED_FN.finditer(code):
        kinds[m.group(1)] = 'function'

    # Finally, plain var blocks (won't overwrite any 'function' set above)
    for m in RE_VAR_BLOCK.finditer(code):
        k = m.group('kind')
        lst = m.group('list')
        for piece in lst.split(','):
            name = piece.strip().split('=')[0].strip()
            if name and re.match(r'^[A-Za-z_$][\w$]*$', name):
                kinds.setdefault(name, k)

    return kinds
def read_file(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    
def strip_comments(src: str) -> str:
    src = RE_BLOCK_COMMENT.sub('', src)
    src = RE_LINE_COMMENT.sub('', src)
    return src

    
def is_local_spec(spec: str) -> bool:
    return spec.startswith("./") or spec.startswith("../") or spec.startswith("/")
 
def find_entry(src_root: Path, entries: List[str]) -> Path:
    for base in entries:
        for ext in EXTS:
            p = src_root / f"{base}{ext}"
            if p.is_file():
                return p
    for ext in EXTS:
        p = src_root / f"index{ext}"
        if p.is_file():
            return p
    raise FileNotFoundError(f"No entry found. Tried {entries} with extensions {EXTS} under {src_root}")

# 3) resolve_with_ext that uses the same allowed predicate
def resolve_with_ext(base: Path, is_allowed=None) -> Optional[Path]:
    is_allowed = is_allowed or REACT_ALLOWED
    candidates: list[Path] = []
    if base.is_file():
        candidates.append(base)
    for ext in EXTS:
        candidates.append(base.with_suffix(ext))
    if base.is_dir():
        for ext in EXTS:
            candidates.append(base / f"index{ext}")
    for p in candidates:
        if p.is_file() and (is_allowed(p) if is_allowed else True):
            return p
    return None



def parse_import_clause(clause: str) -> List[str]:
    names: List[str] = []
    if "* as" in clause or clause.strip().startswith("*"):
        names.append("*")
        return names
    m_def = RE_DEFAULT_IMPORT.match(clause)
    if m_def:
        names.append("<default>")
    m_named = RE_NAMED_BINDINGS.search(clause)
    if m_named:
        raw = m_named.group("named")
        for piece in raw.split(","):
            piece = piece.strip()
            if not piece:
                continue
            name = piece.split(" as ")[0].strip()
            if name:
                names.append(name)
    return names or ["<side-effect>"]
