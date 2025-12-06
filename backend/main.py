import uvicorn
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tts import router as tts_router
from dotenv import load_dotenv

# Load .env from root directory (parent of backend)
root_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=root_dir / ".env")
# Also try loading from backend directory
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
