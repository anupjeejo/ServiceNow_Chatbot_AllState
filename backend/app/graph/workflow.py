from langgraph.graph import StateGraph, END
from backend.app.agents import (
    parser_agent,
    retrieval_agent,
    workaround_agent,
    summary_agent,
    assignment_agent
)

graph = StateGraph(dict)

graph.add_node("parse", parser_agent.run)
graph.add_node("retrieve", retrieval_agent.run)
graph.add_node("assign", assignment_agent.run)
graph.add_node("workaround", workaround_agent.run)
graph.add_node("summary", summary_agent.run)

graph.set_entry_point("parse")
graph.add_edge("parse", "retrieve")
graph.add_edge("retrieve", "assign")
graph.add_edge("assign", "workaround")
graph.add_edge("workaround", "summary")
graph.add_edge("summary", END)

workflow = graph.compile()
