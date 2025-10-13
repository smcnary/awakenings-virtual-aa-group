from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.routes import api_router
from app.core.config import settings

app = FastAPI(
    title="AA Virtual Group API",
    description="API for Awakenings Virtual AA Group",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return JSONResponse(
        content={"message": "AA Virtual Group API", "version": "1.0.0"}
    )

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
