from langsmith import traceable
import json, os, asyncio
from app.nodes.prompts import ANALYST_PROMPT
from app.utils import logger
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
from app.config import serper, openai_llm, gemini_llm
load_dotenv()

# openai_llm = ChatOpenAI(model="gpt-4o-mini")
# gemini_llm = GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
# serper = GoogleSerperAPIWrapper()


@traceable(run_type="chain", name="Junior Analyst Node")
async def junior_analyst_one(state):
    search_terms = state.get("search_terms", [])
    if not search_terms:
        logger.error("No search terms found. Skipping junior analyst.")
        state["junior_analyst_one_report"] = "No terms to research."
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
            prompt = ANALYST_PROMPT.format(topics=", ".join(search_terms), results=json.dumps(all_results, indent=2))

            resp = await openai_llm.ainvoke(prompt)
            # resp = await gemini_llm.ainvoke(prompt) # FOR TESTING
            final_report = resp.content if hasattr(resp, "content") else str(resp)
            state["junior_analyst_one_report"] = final_report
            state["messages"].append(AIMessage(content=final_report))

            return {"junior_analyst_one_report": final_report, "messages": state["messages"]}
            
    except Exception as e:
        logger.error(f"Error in junior analyst one node: {e}")
        state["junior_analyst_one_report"] = "Error generating report."
        return state