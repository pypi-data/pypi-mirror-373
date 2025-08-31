from ..imports import *
from .utils import *
def analyze_file(p: Path) -> Dict:
    code = strip_comments(read_file(p))
    decl_k = decl_kinds(code)
    exports: Set[str] = set()
    imports: List[Dict] = []
    reexports: List[Dict] = []
    export_kinds: Dict[str, str] = {}

    # After your existing loops in analyze_file(...)
    for m in RE_EXPORT_FN_DECL.finditer(code):
        export_kinds[m.group(1)] = 'function'
    for m in RE_EXPORT_CONST_FN.finditer(code):
        export_kinds[m.group(1)] = 'function'
    for m in RE_EXPORT_DEFAULT_NAMED.finditer(code):
        exports.add(m.group(1))
    if RE_EXPORT_DEFAULT_ANON.search(code):
        exports.add("<default>")

    for m in RE_EXPORT_NAMED_LOCAL.finditer(code):
        for piece in m.group(1).split(","):
            nm = piece.strip().split(" as ")[-1].strip()
            if nm:
                exports.add(nm)

    for m in RE_REEXPORT.finditer(code):
        spec = m.group("spec")
        if is_local_spec(spec):
            reexports.append({"spec": spec, "named": [s.strip().split(" as ")[0] for s in m.group("names").split(",") if s.strip()] or ["<reexport>"]})

    for m in RE_IMPORT.finditer(code):
        spec = m.group("spec")
        clause = m.group("clause")
        if is_local_spec(spec):
            imports.append({"spec": spec, "named": parse_import_clause(clause)})

    for m in RE_SIDE_EFFECT_IMPORT.finditer(code):
        spec = m.group("spec")
        if is_local_spec(spec):
            imports.append({"spec": spec, "named": ["<side-effect>"]})

    # For things you explicitly matched as functions/const funcs, etc.,
    # we already added names to `exports`. Pull kinds from decl_k if known.
    for name in list(exports):
        kind = decl_k.get(name, None)
        if kind:
            export_kinds[name] = kind

    # Named local re-exports (export { foo, bar as baz })
    # You already collect names via RE_EXPORT_NAMED_LOCAL; make sure those
    # names get a kind if we can find a local decl:
    for m in RE_EXPORT_NAMED_LOCAL.finditer(code):
        for piece in m.group(1).split(','):
            nm = piece.strip().split(" as ")[-1].strip()
            if nm:
                exports.add(nm)
                if nm in decl_k:
                    export_kinds[nm] = decl_k[nm]

    # Return with both the original 'exports' AND new 'export_kinds'
    return {
        "file": str(p),
        "exports": sorted(exports),
        "imports": imports,
        "reexports": reexports,
        "export_kinds": export_kinds  # <-- NEW
    }
def build_graph_reachable(entry: Path, src_root: Path) -> Dict:
    visited: Set[Path] = set()
    nodes: Dict[str, Dict] = {}
    edges: List[Dict] = {}

    def dfs(fp: Path):
        if fp in visited:
            return
        visited.add(fp)
        info = analyze_file(fp)
        nodes[str(fp)] = {"exports": info["exports"],
                          "kinds":   info.get("export_kinds", {})}


        # resolve and traverse imports & reexports
        for block in (info["reexports"], info["imports"]):
            for item in block:
                base = (fp.parent / item["spec"]).resolve()
                resolved = resolve_with_ext(base)
                if resolved:
                    edges.setdefault(str(fp), []).append({
                        "to": str(resolved),
                        "named": item["named"],
                    })
                    dfs(resolved)

    dfs(entry.resolve())

    # flatten edges
    flat_edges = []
    for frm, lst in edges.items():
        for e in lst:
            flat_edges.append({"from": frm, "to": e["to"], "named": e["named"]})

    return {"entry": str(entry.resolve()), "nodes": nodes, "edges": flat_edges}


def build_graph_all(src_root: Path, cfg=None, is_allowed=None) -> Dict:
    cfg = cfg or REACT_DEFAULT_CFG
    roots = make_list(src_root)
    files = collect_filepaths(roots, cfg)
    is_allowed = is_allowed or REACT_ALLOWED

    analyses: Dict[str, Dict] = {}
    for f in files:
        try:
            info = analyze_file(Path(f))
            analyses[str(Path(f))] = info
        except Exception as e:
            print(f"[analyze_file] failed on {f}: {e}")

    # <-- moved out of the for-loop
    nodes: Dict[str, Dict] = {
        f: {"exports": analyses[f]["exports"],
            "kinds":   analyses[f].get("export_kinds", {})}
        for f in analyses.keys()
    }
    edges: List[Dict] = []

    for f, info in analyses.items():
        fp = Path(f)
        for block in (info["reexports"], info["imports"]):
            for item in block:
                base = (fp.parent / item["spec"]).resolve()
                resolved = resolve_with_ext(base, is_allowed=is_allowed)
                if resolved:
                    edges.append({"from": f, "to": str(resolved), "named": item["named"]})
                else:
                    edges.append({"from": f, "to": item["spec"], "named": item["named"], "unresolved": True})

    return {"entry": None, "nodes": nodes, "edges": edges}

def to_dot(graph: Dict, src_root: Path) -> str:
    def rel(p: str) -> str:
        try:
            return str(Path(p).resolve().relative_to(src_root.resolve()))
        except Exception:
            return p  # for unresolved specs

    def q(s: str) -> str:
        return json.dumps(s)

    lines = ["digraph G {", "  rankdir=LR;", "  node [shape=box, fontsize=10];"]
    for p, data in graph["nodes"].items():
        rp = rel(p)
        ex = data.get("exports") or []
        extra = f"\\nexports: {', '.join(ex)}" if ex else ""
        lines.append(f"  {q(rp)} [label={q(rp + extra)}];")
    for e in graph["edges"]:
        frm = rel(e["from"])
        to = rel(e["to"])
        label = ", ".join((e.get("named") or [])[:4])
        if (e.get("named") and len(e["named"]) > 4):
            label += ", …"
        style = " [style=dashed]" if e.get("unresolved") else ""
        lines.append(f"  {q(frm)} -> {q(to)} [label={q(label)}]{style};")
    lines.append("}")
    return "\n".join(lines)
