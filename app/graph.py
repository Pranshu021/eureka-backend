from langgraph.graph import StateGraph, END
from app.state import State
from app.nodes.research_assistant import research_assistant
from app.nodes.junior_analyst_one import junior_analyst_one
from app.nodes.junior_analyst_two import junior_analyst_two
from app.nodes.senior_analyst import senior_analyst

graph_builder = StateGraph(State)
graph_builder.set_entry_point("research_assistant")

graph_builder.add_node("research_assistant", research_assistant)
graph_builder.add_node("junior_analyst_one", junior_analyst_one)
graph_builder.add_node("junior_analyst_two", junior_analyst_two)
graph_builder.add_node("senior_analyst", senior_analyst)

graph_builder.add_edge("research_assistant", "junior_analyst_one")
graph_builder.add_edge("research_assistant", "junior_analyst_two")
graph_builder.add_edge("junior_analyst_one", "senior_analyst")
graph_builder.add_edge("junior_analyst_two", "senior_analyst")
graph_builder.add_edge("senior_analyst", END)

graph = graph_builder.compile()
