from fastapi import FastAPI
from app.database import init_db
from app.routers import health, codebase, search, chat
app = FastAPI(
    title="Smart Codebase & Tech Stack Knowledge Assistant",
    description="Local, open-source RAG assistant for developer codebases.",
    version="0.1.0",
)

init_db()

app.include_router(health.router, tags=["health"])
app.include_router(codebase.router, tags=["codebase"])
app.include_router(search.router, tags=["search"])
app.include_router(chat.router, tags=["chat"])
@app.get("/")
def root():
    return {"message": "Codebase Assistant API is running. See /docs for the interactive API explorer."}
