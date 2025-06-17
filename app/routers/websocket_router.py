import asyncio
import logging
import os
from datetime import datetime

import websockets
from dotenv import load_dotenv
from fastapi import WebSocket, APIRouter


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"

headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "realtime=v1"
}

router = APIRouter(prefix='/ws')


@router.websocket("/openai")
async def chat_via_openai(websocket: WebSocket):
    await websocket.accept()
    async with websockets.connect(
        OPENAI_WS_URL,
        additional_headers=headers
    ) as openai_ws:
        async def forward_client_to_openai():
            try:
                while True:
                    msg = await websocket.receive_bytes()
                    logging.debug(f"received byte data type: {type(msg)}")
                    logging.debug(f"received data: {msg}")

                    if isinstance(msg, bytes):
                        logging.debug("➡️ Forwarding binary audio to OpenAI")
                        await openai_ws.send(msg)
                    elif isinstance(msg, str):
                        logging.debug(f"➡️ Forwarding text to OpenAI: {msg}")
                        await openai_ws.send(msg)
                    else:
                        logging.warning("Unknown client message type")
            except Exception as e:
                logging.error(f"Client->OpenAI error: {e}")
                await openai_ws.close()

        async def forward_openai_to_client():
            try:
                while True:
                    msg = await openai_ws.recv()
                    logging.debug(f"received from OpenAI data type: {type(msg)}")
                    logging.debug(f"received from OpenAI data: {msg}")

                    if isinstance(msg, bytes):
                        logging.debug("⬅️ Forwarding binary from OpenAI to client")
                        await websocket.send_bytes(msg)
                    elif isinstance(msg, str):
                        logging.debug(f"⬅️ Forwarding JSON from OpenAI: {msg}")
                        await websocket.send_text(msg)
                    else:
                        logging.warning("Unknown OpenAI message type")
            except Exception as e:
                logging.error(f"OpenAI->Client error: {e}")
                await websocket.close()

        await asyncio.gather(
            forward_client_to_openai(),
            forward_openai_to_client()
        )


@router.websocket("/text")
async def websocket_text(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")


@router.websocket("/audio")
async def websocket_audio(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    with open(f"audio_{timestamp}.webm", "wb") as audio_file:
        try:
            while True:
                data = await websocket.receive_bytes()
                audio_file.write(data)
        except Exception as e:
            print("Connection closed:", e)


@router.websocket("/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            pcm_bytes = await websocket.receive_bytes()
            await websocket.send_bytes(pcm_bytes)  # Echo back
    except Exception as e:
        print(f"WebSocket closed: {e}")

