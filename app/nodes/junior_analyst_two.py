import json, os, asyncio
from app.nodes.prompts import ANALYST_PROMPT
from app.utils import logger
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
load_dotenv()
from langsmith import traceable
from app.config import serper, gemini_llm

# gemini_llm = GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
# serper = GoogleSerperAPIWrapper()

@traceable(run_type="chain", name="Junior Analyst Two Node")
async def junior_analyst_two(state):
    search_terms = state.get("search_terms", [])
    if not search_terms:
        state["junior_analyst_two_report"] = "No terms to research."
        return state

    try:
        all_results = {}
        for term in search_terms:
            try:
                result = await asyncio.to_thread(serper.run, term)
                all_results[term] = result
            except Exception as e:
                logger.error(f"Error fetching results for {term}: {e}")
                all_results[term] = "No results"

        prompt = ANALYST_PROMPT.format(
            topics=", ".join(search_terms),
            results=json.dumps(all_results, indent=2)
        )

        resp = await gemini_llm.ainvoke(prompt)
        report = resp.content if hasattr(resp, "content") else str(resp)

        state["junior_analyst_two_report"] = report
        state["messages"].append(AIMessage(content=report))

        return {"junior_analyst_two_report": report, "messages": state["messages"]}

    except Exception as e:
        logger.error(f"Error in junior analyst 2: {e}")
        state["junior_analyst_two_report"] = "Error generating report."
        return state
