#pibble voice

import os
import requests
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()

# Load env variables
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

class TTSRequest(BaseModel):
    text: str

@router.post("/tts")
def tts(req: TTSRequest):
    # Check if API key and voice ID are set
    if not ELEVEN_API_KEY or not VOICE_ID:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="ElevenLabs API key or Voice ID not configured. Please check your .env file."
        )
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": req.text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.8
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        return Response(
            content=response.content,
            media_type="audio/mpeg"
        )
    except requests.exceptions.RequestException as e:
        from fastapi import HTTPException
        error_msg = f"ElevenLabs API error: {str(e)}"
        if hasattr(e.response, 'text'):
            error_msg += f" - {e.response.text}"
        raise HTTPException(status_code=500, detail=error_msg)
