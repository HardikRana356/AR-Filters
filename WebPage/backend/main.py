from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2, base64, json, numpy as np
from ar_engine import process_frame, handle_command

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            if not msg.startswith("{"):
                continue

            data = json.loads(msg)

            if data["type"] == "command":
                handle_command(data)

            elif data["type"] == "frame":
                out = process_frame(
                    cv2.imdecode(
                        np.frombuffer(base64.b64decode(data["data"]), np.uint8),
                        cv2.IMREAD_COLOR
                    )
                )
                if out is None:
                    continue

                _, buf = cv2.imencode(".jpg", out)
                await ws.send_text(base64.b64encode(buf).decode())

    except WebSocketDisconnect:
        pass
