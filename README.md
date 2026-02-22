# TaNUC  
### Nodo de Captura y Transmisión para Detección de Aves – Patagonia

TaNUC es un software nodo diseñado para capturar imágenes desde una cámara local y enviarlas a un servidor central para su procesamiento y detección de aves en entornos patagónicos.

El sistema está pensado para despliegues en terreno, con monitoreo de recursos y capacidad de integración con hardware externo.

---

## 🌎 Descripción General

TaNUC permite:

- 📸 Captura continua de imágenes en terreno  
- 📡 Envío de frames vía WebSocket al servidor central  
- 🧠 Procesamiento remoto mediante modelos de detección  
- 📊 Monitoreo del estado del nodo (CPU / RAM / GPU)  
- 🔌 Integración opcional con dispositivos físicos (Arduino)

El nodo es ligero y delega el procesamiento pesado al backend, permitiendo escalabilidad mediante múltiples nodos distribuidos.

---

## 🏗️ Arquitectura del Sistema

```text
[Cámara Nodo]
      ↓
   OpenCV
      ↓
Captura Frame
      ↓
WebSocket Client  →  Servidor Central
                         ↓
                 Modelo de Detección
                         ↓
                 Resultados / Acciones
```
---

## ⚙️ Configuración

La configuración del nodo se realiza mediante el archivo `config.json`.

### 🔴 IMPORTANTE

Para conectarse correctamente al servidor, debes modificar la IP en el siguiente parámetro:

```json
"websocket_url": "ws://192.168.1.88:8085"
```

Reemplaza `192.168.1.88` por la IP del servidor donde se ejecuta el backend de detección.

---

## 📄 Ejemplo completo de `config.json`

```json
{
  "websocket_url": "ws://192.168.1.88:8085",
  "client_id": "tanu-1",
  "weights_source": "default",
  "focal_length": 18,
  "height": 100,
  "arduino_port": "COM3",
  "max_turns": 2,
  "max_v_turns": 1
}
```

---

## 🖥️ Requisitos

- Python 3.9+
- Cámara
- Conectividad de red estable
- Arduino (opcional)

---

## 📦 Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Ejecución

```bash
python video_send.py
```

---

## 📚 Dependencias Principales

- websockets
- opencv-python
- psutil
- GPUtil
- pyserial

---

## 👨‍💻 Autor

Moises Iván Llancapani Stormensan 

Proyecto TANU – Monitoreo Ambiental Inteligente

Generado el 2026-01-17
