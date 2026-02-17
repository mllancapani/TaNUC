import asyncio
import websockets
import json
import cv2
import base64
import serial


# --------------------------------------------------------------
# UTILIDADES
# --------------------------------------------------------------
def encode_frame_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')


def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------
# CLIENTE PRINCIPAL
# --------------------------------------------------------------
async def handle_server_messages(websocket, arduino, max_turns, max_v_turns):
    """Listen for incoming messages from server and handle signals."""
    current_turn = 0
    current_v_turn = 0
    try:
        async for message in websocket:
            print(message)
            try:
                json_message = json.loads(message)
                action = json_message.get("action")

                if action == "signal":
                    direction = json_message["parameters"]["signal"]

                    if arduino is not None:
                        if direction == "left":
                            if current_turn <= -max_turns:
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "max_error"
                                    }
                                }))
                                continue
                            try:
                                arduino.write(b'L')
                                print("[CLIENT] Sent LEFT to Arduino")
                                current_turn -= 1
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "ok"
                                    }
                                }))
                            except Exception:
                                print("[CLIENT] Failed to send LEFT signal to Arduino")
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "error"
                                    }
                                }))
                        elif direction == "right":
                            if current_turn >= max_turns:
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "max_error"
                                    }
                                }))
                                continue
                            try:
                                arduino.write(b'R')
                                print("[CLIENT] Sent RIGHT to Arduino")
                                current_turn += 1
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "ok"
                                    }
                                }))
                            except Exception:
                                print("[CLIENT] Failed to send RIGHT signal to Arduino")
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "error"
                                    }
                                }))
                        elif direction == "up":
                            if current_v_turn <= -max_v_turns:
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "max_error"
                                    }
                                }))
                                continue
                            try:
                                arduino.write(b'U')
                                print("[CLIENT] Sent UP to Arduino")
                                current_v_turn -= 1
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "ok"
                                    }
                                }))
                            except Exception:
                                print("[CLIENT] Failed to send UP signal to Arduino")
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "error"
                                    }
                                }))
                        elif direction == "down":
                            if current_v_turn >= max_v_turns:
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "max_error"
                                    }
                                }))
                                continue
                            try:
                                arduino.write(b'D')
                                print("[CLIENT] Sent DOWN to Arduino")
                                current_v_turn += 1
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "ok"
                                    }
                                }))
                            except Exception:
                                print("[CLIENT] Failed to send RIGHT signal to Arduino")
                                await websocket.send(json.dumps({
                                    "action": "aknowledgement",
                                    "parameters": {
                                        "status": "error"
                                    }
                                }))

            except Exception as e:
                print(f"[CLIENT] Error parsing server message: {e}")
    except websockets.ConnectionClosed:
        print("[CLIENT] Server connection closed.")


async def send_frames(websocket, client_id, camera_index):
    """Capture frames from camera and send them to the server."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("[CLIENT] Cannot open webcam")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[CLIENT] Failed to grab frame")
                break

            b64_frame = encode_frame_to_base64(frame)
            await websocket.send(json.dumps({
                "action": "frame",
                "client_id": client_id,
                "image_base64": b64_frame
            }))

            await asyncio.sleep(1)  # 1 FPS
    finally:
        cap.release()


async def send_video_to_server(
        websocket_url,
        client_id,
        weights_source,
        focal_length=18,
        height=100,
        max_turns=2,
        max_v_turns=1,
        camera_index=0,
        arduino=None
):
    try:
        async with websockets.connect(websocket_url) as websocket:
            # 1. Enviar mensaje inicial
            await websocket.send(json.dumps({
                "action": "start_streaming",
                "client_id": client_id,
                "weights_source": weights_source,
                "focal_length": focal_length,
                "height": height
            }))
            print("[CLIENT] Sent start_streaming")

            # 2. Esperar confirmación
            response = await websocket.recv()
            print(f"[CLIENT] Server response: {response}")

            # 3. Lanzar tareas en paralelo: enviar frames y escuchar servidor
            await asyncio.gather(
                send_frames(websocket, client_id, camera_index),
                handle_server_messages(websocket, arduino, max_turns, max_v_turns)
            )

    except Exception as e:
        print(f"[CLIENT] Connection error or fatal error: {e}")


# --------------------------------------------------------------
# MAIN
# --------------------------------------------------------------
if __name__ == "__main__":
    config = load_config("config.json")

    port = config["arduino_port"]

    try:
        arduino = serial.Serial(port, 9600, timeout=1)
        print("[CLIENT] Arduino connected")
    except Exception as e:
        print(f"[CLIENT] No Arduino connected: {e}")
        arduino = None

    asyncio.run(send_video_to_server(
        config["websocket_url"],
        config["client_id"],
        config["weights_source"],
        config["focal_length"],
        config["height"],
        config["max_turns"],
        config["max_v_turns"],
        camera_index=0,
        arduino=arduino
    ))
