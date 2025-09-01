from pathlib import Path
from .detector import detect_language
from .plugins import get_builder
import networkx as nx


def build_graph(project_path: str) -> nx.DiGraph:
    lang = detect_language(project_path)
    builder = get_builder(lang)
    return builder.build_graph(Path(project_path))
