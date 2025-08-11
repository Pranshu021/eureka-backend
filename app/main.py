# app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import graph
from langchain_core.messages import HumanMessage
import asyncio
import os, tempfile

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://eureka-frontend-azure.vercel.app",
    "https://www.eurekasearch.in",
    "https://eurekasearch.in"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("SECRET_API_KEY")

class QueryRequest(BaseModel):
    query: str

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await call_next(request)

@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)

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
