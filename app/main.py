import asyncio
import uuid
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
# WebRTC Connection imports from Pipecat
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection, IceServer

# Import the runner function from bot.py
from app.bot import run_bot


from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Nova Real Estate AI Voice Agent")

# Allow CORS so WebRTC connection requests pass smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route to serve your index.html showcase page
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "frontend", "index.html")
    
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail=f"Frontend file not found at {html_path}")
        
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


# The frontend is plain HTML/CSS/JS (no bundler), loaded as relative paths
# from index.html (e.g. "style.css", "app.js"). Serve each file explicitly
# so the browser can fetch them from the same origin as "/".
_FRONTEND_ASSETS = {
    "/style.css": ("style.css", "text/css"),
    "/app.js": ("app.js", "application/javascript"),
    "/config.js": ("config.js", "application/javascript"),
}

for _route, (_filename, _media_type) in _FRONTEND_ASSETS.items():

    def _make_handler(filename: str, media_type: str):
        async def _serve_asset():
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, "frontend", filename)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"{filename} not found")
            return FileResponse(file_path, media_type=media_type)

        return _serve_asset

    app.get(_route, include_in_schema=False)(_make_handler(_filename, _media_type))


@app.post("/connect")
async def connect(request: Request):
    try:
        body = await request.json()
        
        # 1. Instantiate SmallWebRTC Connection
        conn = SmallWebRTCConnection()
        
        # 2. Launch Pipecat Bot Task in background
        asyncio.create_task(run_bot(transport_or_webrtc_conn=conn))
        
        # 3. ✅ FIX: Call initialize() with sdp and type instead of handle_offer()
        answer = await conn.initialize(sdp=body["sdp"], type=body["type"])
        
        # Return answer dictionary to frontend
        return JSONResponse(answer)
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
        
@app.post("/offer")
async def handle_webrtc_offer(request: Request, background_tasks: BackgroundTasks):
    """
    Handles WebRTC SDP offer from client, initializes SmallWebRTCConnection,
    generates SDP answer, and spawns the Pipecat voice pipeline in the background.
    """
    try:
        body = await request.json()
        sdp = body.get("sdp")
        sdp_type = body.get("type", "offer")

        if not sdp:
            raise HTTPException(status_code=400, detail="Missing SDP offer payload.")

        # Generate a unique session ID for DB context and tracking
        session_id = str(uuid.uuid4())
        logger.info(f"Received WebRTC SDP offer for new session: {session_id}")

        # 1. Setup WebRTC ICE Servers (STUN/TURN)
        ice_servers = [
            IceServer(urls=["stun:stun.l.google.com:19302"])
        ]

        # 2. Create and initialize WebRTC connection
        webrtc_connection = SmallWebRTCConnection(ice_servers=ice_servers)
        await webrtc_connection.initialize(sdp=sdp, type=sdp_type)

        # 3. Get SDP Answer to send back to the client
        answer = webrtc_connection.get_answer()

        # 4. Spawn Pipecat bot task in the background
        background_tasks.add_task(
            run_bot,
            transport_or_webrtc_conn=webrtc_connection,
            session_id=session_id,
        )

        return answer

    except Exception as e:
        logger.error(f"Error handling WebRTC offer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"WebRTC handshake failed: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting Real Estate Voice Agent FastAPI server on http://0.0.0.0:7860")
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860, reload=True)