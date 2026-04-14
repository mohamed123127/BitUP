from langgraph.graph import StateGraph, END
from typing import TypedDict

from state import IndustryState
from modules.module1.main import module_1_extraction
from modules.module8.main import module_8_ml
from modules.module9.main import module_9_catalog
from modules.module6.main import module_6_tco
from modules.module7.main import module_7_business_plan

def build_graph():
    graph = StateGraph(IndustryState)

    graph.add_node("m1", module_1_extraction)
    graph.add_node("m6", module_6_tco)
    graph.add_node("m7", module_7_business_plan)
    graph.add_node("m8", module_8_ml)
    graph.add_node("m9", module_9_catalog)
 

    # linear flow
    graph.set_entry_point("m1")
    graph.add_edge("m1", "m6")
    graph.add_edge("m6", "m7")
    graph.add_edge("m7", "m8")
    graph.add_edge("m8", "m9")
    graph.add_edge("m9", END)

    return graph.compile()