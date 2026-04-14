from langgraph.graph import StateGraph, END
from typing import TypedDict

from state import IndustryState
from modules.module1.main import module_1_extraction
from modules.module2.main import module_2_cad
from modules.module3.main import module_3_video
from modules.module4.main import module_4_sourcing
from modules.module8.main import module_8_ml
from modules.module9.main import module_9_catalog


def build_graph():
    graph = StateGraph(IndustryState)

    graph.add_node("m1", module_1_extraction)
    graph.add_node("m2", module_2_cad)
    graph.add_node("m3", module_3_video)
    graph.add_node("m4", module_4_sourcing)
    graph.add_node("m8", module_8_ml)
    graph.add_node("m9", module_9_catalog)

    # linear flow
    graph.set_entry_point("m1")
    graph.add_edge("m1", "m2")
    graph.add_edge("m2", "m3")
    graph.add_edge("m3", "m4")
    graph.add_edge("m4", "m8")
    graph.add_edge("m8", "m9")
    graph.add_edge("m9", END)

    return graph.compile()
