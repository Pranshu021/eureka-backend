# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import graph
from langchain_core.messages import HumanMessage
import asyncio
import os, tempfile

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/generate-report")
async def generate_report(request: QueryRequest):
    try:
        query = request.query
        print("Query: ", query)
        state = {"messages": [HumanMessage(content=query)]}
        result = await graph.ainvoke(state)
        final_report = result.get("senior_analyst_report", "")
        file_path = result.get("final_doc_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="File generation failed. File path not returned")
        
        return {
            "query": query,
            "report": final_report,
            "download_url": f"/download/{os.path.basename(file_path)}"
            }

    except Exception as e:
        print("Error - ", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(tempfile.gettempdir(), filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/msword"
    )
