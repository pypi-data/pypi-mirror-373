from ..imports import *
from .graph_utils import *
from .utils import *
from collections import defaultdict
# react_analyzer/utils/invert_utils.py
def invert_to_symbol_map(graph: dict, include_kinds: Optional[Set[str]] = None) -> dict:
    include_kinds = set(include_kinds or [])

    # Build export-kind index per module
    module_kinds: Dict[str, Dict[str, str]] = {
        mod: (data.get('kinds') or {}) for mod, data in graph.get('nodes', {}).items()
    }

    out: Dict[str, Dict[str, Set[str]]] = {}

    # Export side
    for mod, data in graph.get('nodes', {}).items():
        kinds = data.get('kinds', {})  # {name: kind}
        for name, k in kinds.items():
            if include_kinds and k not in include_kinds:
                continue
            out.setdefault(name, {'exported_in': set(), 'imported_in': set()})
            out[name]['exported_in'].add(mod)

    # Import side: keep only names whose DEST module exports them with a matching kind
    for e in graph.get('edges', []):
        dst = e.get('to')  # module path we import from
        dst_kinds = module_kinds.get(dst, {})
        for n in (e.get('named') or []):
            if n in ('*', '<side-effect>', '<default>'):
                continue
            if include_kinds:
                k = dst_kinds.get(n)
                if k not in include_kinds:
                    continue
            out.setdefault(n, {'exported_in': set(), 'imported_in': set()})
            out[n]['imported_in'].add(e['from'])

    # to lists
    return {
        k: {'exported_in': sorted(v['exported_in']),
            'imported_in': sorted(v['imported_in'])}
        for k, v in out.items()
    }

def invert_to_function_map(graph: dict) -> dict:
    # WARNING: this will also pull non-callable consts!
    return invert_to_symbol_map(graph, include_kinds={'function','const','let','var'})


def invert_to_variable_map(graph: dict) -> dict[str, dict[str, list[str]]]:
    """
    Build: {
      varName: {"exported_in": [files...], "imported_in": [files...] }
    }
    """
    out = defaultdict(lambda: {"exported_in": [], "imported_in": []})

    # where variables are defined/exported
    for fp, node in (graph.get("nodes") or {}).items():
        for name, kind in (node.get("kinds") or {}).items():
            if kind in {"const", "let", "var"}:
                out[name]["exported_in"].append(fp)

    # where they are imported (follow edges' named imports)
    for e in (graph.get("edges") or []):
        for nm in (e.get("named") or []):
            if nm in {"<default>", "<side-effect>", "<reexport>"}:
                continue
            # we don't *know* it's a variable here, but if it *is* one it'll be present above
            out[nm]["imported_in"].append(e["from"])

    # de-dup + sort
    for v in out.values():
        v["exported_in"] = sorted(set(v["exported_in"]))
        v["imported_in"] = sorted(set(v["imported_in"]))

    return dict(out)
