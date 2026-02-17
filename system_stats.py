import asyncio
import websockets
import json
import psutil
import GPUtil
import time


def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def send_system_stats_once(websocket_url, client_id):
    try:
        async with websockets.connect(websocket_url) as websocket:
            print("[CLIENT] Connected to WebSocket for system stats")

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            ram_percent = memory.percent

            # Disk usage (root partition)
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # GPU usage (first GPU if available)
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_load = gpus[0].load * 100  # %
                gpu_mem_percent = (gpus[0].memoryUsed / gpus[0].memoryTotal) * 100
            else:
                gpu_load = None
                gpu_mem_percent = None

            # Create JSON payload
            stats_data = {
                "action": "system_stats",
                "client_id": client_id,
                "data": {
                    "cpu_usage_percent": cpu_percent,
                    "gpu_usage_percent": gpu_load,
                    "gpu_memory_percent": gpu_mem_percent,
                    "ram_usage_percent": ram_percent,
                    "disk_usage_percent": disk_percent,
                    "timestamp": time.time()
                }
            }

            await websocket.send(json.dumps(stats_data))
            print(f"[CLIENT] Sent stats: {stats_data}")

    except Exception as e:
        print(f"[CLIENT] Connection error: {e}")

if __name__ == "__main__":
    config = load_config("config.json")

    asyncio.run(send_system_stats_once(
        config["websocket_url"],
        config["client_id"]
    ))

