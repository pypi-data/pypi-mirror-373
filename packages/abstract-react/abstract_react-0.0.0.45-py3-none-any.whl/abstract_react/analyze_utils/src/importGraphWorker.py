# react_analyzer/ImportGraphWorker.py (or wherever you keep it)
from ..imports import *
from .invert_utils import invert_to_function_map, invert_to_variable_map
from .graph_utils import build_graph_all, build_graph_reachable
from .utils import find_entry

class ImportGraphWorker(QThread):
    log   = pyqtSignal(str)
    ready = pyqtSignal(dict, dict, dict)  # graph, func_map, var_map

    def __init__(self, project_root: str, scope: str = "all", entries=None):
        super().__init__()
        self.project_root = project_root
        self.root   = Path(project_root).resolve()
        self.scope  = scope
        self.entries = entries or ["index", "main"]

    def run(self):
        try:
            self.log.emit(f"[map] scanning {self.root} (scope={self.scope})\n")
            graph = self._get_graph()
            func_map = invert_to_function_map(graph)
            var_map  = invert_to_variable_map(graph)
            self.log.emit(
                f"[map] files={len(graph['nodes'])} edges={len(graph['edges'])} "
                f"functions={len(func_map)} vars={len(var_map)}\n"
            )
            self.ready.emit(graph, func_map, var_map)
        except Exception as e:
            self.log.emit(f"[map] error: {e}\n{traceback.format_exc()}\n")
            self.ready.emit({}, {}, {})

    def _get_graph(self):
        if self.scope == "reachable":
            entry = find_entry(self.root, self.entries)
            self.log.emit(f"[map] entry={entry}\n")
            return build_graph_reachable(entry, self.root)
        return build_graph_all(self.root)
