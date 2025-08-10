from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    search_terms: List[str]
    junior_analyst_one_report: str
    junior_analyst_two_report: str
    senior_analyst_report: str
    final_doc_path: str