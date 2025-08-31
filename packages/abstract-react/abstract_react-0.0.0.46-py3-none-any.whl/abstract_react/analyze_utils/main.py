# ---------- import graph analyzer (pure Python) ----------
from .imports import *
from .src import *
def start_analyzer(
    root=None,
    scope="all",
    out=None,
    entries=None,
    dot=None
    ):
    
        
    root = root or os.getcwd()
    src_root = Path(root).resolve()
    entries = entries or []
    if isinstance(entries,str):
        entries = entries.split(",")
    if scope == "reachable":
        entries = [s.strip() for s in entries if s.strip()]
        entry = find_entry(src_root, entries)
        graph = build_graph_reachable(entry, src_root)
    else:
        graph = build_graph_all(src_root)
    out = out or os.path.join(root,'import-graph.json')
    Path(out).write_text(json.dumps(graph, indent=2), encoding="utf-8")
    #print(f"✅ Wrote {out} (scope: {scope})")

    if dot:
        dot_data = to_dot(graph, src_root)
        Path(dot).write_text(dot_data, encoding="utf-8")
        #print(f"✅ Wrote {dot} (Graphviz)")

def react_cmd_start():
    ap = argparse.ArgumentParser(description="Map local imports & exported functions.")
    ap.add_argument("--root", default="src", help="Project source root (default: src)")
    ap.add_argument("--entries", default="index,main", help="Comma list of entry basenames (used when --scope=reachable)")
    ap.add_argument("--scope", choices=["reachable", "all"], default="all", help="reachable|all (default: reachable)")
    ap.add_argument("--out", default="import-graph.json", help="Output JSON file")
    ap.add_argument("--dot", default="graph.dot", help="Optional Graphviz .dot output path")
    args = ap.parse_args()
    root = args.root
    scope = args.scope
    out = args.out
    entries = args.entries
    dot = args.dot
    start_analyzer(
        root=root,
        scope=scope,
        out=out,
        entries=entries,
        dot=dot
    )
