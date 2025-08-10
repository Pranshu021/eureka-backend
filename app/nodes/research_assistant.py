import json, os
from langchain_core.messages import HumanMessage
from app.nodes.prompts import RESEARCH_ASSISTANT_PROMPT
from app.utils import logger
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
from langsmith import traceable
from dotenv import load_dotenv
from app.config import gemini_llm
load_dotenv()

class ResearchTerms(BaseModel):
    search_terms: list[str]

parser = PydanticOutputParser(pydantic_object=ResearchTerms)

@traceable(run_type="chain", name="Research Assistant Node")
async def research_assistant(state):
    query = None
    # Extract last human message

    print("State: ", state)
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            query = msg.content
            break

    if not query:
        raise ValueError("No user query found in state['messages'].")
    prompt = RESEARCH_ASSISTANT_PROMPT.format(query=query, format_instructions=parser.get_format_instructions())
    response = await gemini_llm.ainvoke(prompt)
    response_text = response.content if hasattr(response, "content") else str(response)
    
    try:
        parsed = parser.parse(response_text)
        # logging.info(f"Validated Search Terms: {parsed.search_terms}")
        state["search_terms"] = parsed.search_terms
    except Exception as e:
        logging.error(f"Parsing failed: {e}")
        state["search_terms"] = []

    return state