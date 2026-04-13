from langgraph.graph import StateGraph, END
from typing import TypedDict

from state import IndustryState
from modules.module1.main import module_1_extraction
from modules.module8.main import module_8_ml
from modules.module9.main import module_9_catalog


def build_graph():
    graph = StateGraph(IndustryState)

    graph.add_node("m1", module_1_extraction)
    graph.add_node("m8", module_8_ml)
    graph.add_node("m9", module_9_catalog)

    # linear flow
    graph.set_entry_point("m1")
    graph.add_edge("m1", "m8")
    graph.add_edge("m8", "m9")
    graph.add_edge("m9", END)

    return graph.compile()