# PixVerse_Generate_Node.py

import os
import requests
import json
import time
import uuid
import random
from pixverse_ai.plogin import *

# === NODO DE COMFYUI ===
class PixVerseGenerateNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "upload_data": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Conectar con salida del nodo de subida"
                }),
                "prompt": ("STRING", {
                    "default": "A cat dancing in the rain",
                    "multiline": True,
                    "tooltip": "Describe el video que quieres generar"
                }),
                "quality": (["360p", "540p", "720p", "1080p"], {"default": "360p"}),
                "model_version": (["v3.5", "v4", "v4.5", "v5"], {"default": "v5"}),
                "motion_mode": (["normal"], {"default": "normal"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "seed_select": ("BOOLEAN", {"default": False, "label_on": "Fijo", "label_off": "Aleatorio"}),
                "style_selected": (["Normal", "Anime", "Animación 3D", "Cómic", "Cyberpunk", "Arcilla"], {"default": "Normal"}),
                "camera_selected": ([
                    "Normal",
                    "Horizontal Izquierda", "Horizontal Derecha",
                    "Vertical Arriba", "Vertical Abajo",
                    "Movimiento de Grúa hacia Arriba", "Dolly Zoom",
                    "Acercar", "Alejar",
                    "Zoom Rápido Acercando", "Zoom Rápido Alejando",
                    "Zoom Suave Acercando", "Super Dolly Alejando",
                    "Toma de Rastreo Izquierdo", "Toma de Rastreo Derecho",
                    "Toma de Arco Izquierdo", "Toma de Arco Derecho",
                    "Toma Fija", "Ángulo de Cámara",
                    "Brazo Robótico", "Barrido Rápido"
                ], {"default": "Normal"}),
                "duration": ([5, 8], {"default": 5}),
                "generate": ("BOOLEAN", {"default": False, "label_on": "Generar", "label_off": "Detener"})
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("video_path", "video_url", "credit")
    FUNCTION = "generate_video"
    CATEGORY = "PixVerse"
    OUTPUT_NODE = True

    def generate_video(self, upload_data, prompt, quality, model_version, motion_mode, seed, seed_select, style_selected, camera_selected, duration, generate):
        import json

        # Inicializar créditos
        credit_actualizado = 0

        if not generate:
            print("❌ Generación no activada.")
            return {"ui": {"text": "Detenido"}, "result": ("❌ Generación no activada.", "", 0)}

        # Extraer datos
        try:
            data = json.loads(upload_data)
        except Exception as e:
            print(f"❌ Error: upload_data no es un JSON válido. {e}")
            return {"ui": {"text": "Error JSON"}, "result": ("❌ Error: upload_data no es un JSON válido.", "", 0)}

        if not data.get("success"):
            error_msg = f"❌ Error en subida: {data.get('error', 'Desconocido')}"
            print(error_msg)
            jwt_token = data.get("jwt_token", "")
            credit_actualizado = obtener_credit_package(jwt_token) if jwt_token else 0
            return {"ui": {"text": "Error subida"}, "result": (error_msg, "", credit_actualizado)}

        jwt_token = data.get("jwt_token", "")
        uploaded_final_url = data.get("uploaded_final_url", "")
        media_path = data.get("media_path", "")

        if not all([jwt_token, uploaded_final_url, media_path]):
            print("❌ Datos faltantes en upload_data")
            credit_actualizado = obtener_credit_package(jwt_token) if jwt_token else 0
            return {"ui": {"text": "Faltan datos"}, "result": ("❌ Datos faltantes en upload_data", "", credit_actualizado)}

        # Obtener créditos actuales
        credit_actualizado = obtener_credit_package(jwt_token)
        if not jwt_token:
            return {"ui": {"text": "Sin token"}, "result": ("❌ JWT Token no proporcionado.", "", 0)}

        # Mapeo de modelos
        model_map = {
            "v3.5": "v3.5",
            "v4": "v4",
            "v4.5": "v4.5",
            "v5":"v5"
        }
        model = model_map[model_version]

        # Mapeo de estilos
        style_ids = {
            "Normal": "normal",
            "Anime": "anime",
            "Animación 3D": "3d_animation",
            "Cómic": "comic",
            "Cyberpunk": "cyberpunk",
            "Arcilla": "clay"
        }
        style = style_ids.get(style_selected, "normal")

        # Mapeo de cámaras (✅ Corregido "Izquirda" → "Izquierda")
        camera_ids = {
            "Normal": "normal",
            "Horizontal Izquierda": "horizontal_left",
            "Horizontal Derecha": "horizontal_right",
            "Vertical Arriba": "vertical_up",
            "Vertical Abajo": "vertical_down",
            "Movimiento de Grúa hacia Arriba": "crane_up",
            "Dolly Zoom": "hitchcock",
            "Acercar": "zoom_in",
            "Alejar": "zoom_out",
            "Zoom Rápido Acercando": "quickly_zoom_in",
            "Zoom Rápido Alejando": "quickly_zoom_out",
            "Zoom Suave Acercando": "smooth_zoom_in",
            "Super Dolly Alejando": "super_dolly_out",
            "Toma de Rastreo Izquierdo": "left_follow",
            "Toma de Rastreo Derecho": "right_follow",
            "Toma de Arco Izquierdo": "pan_left",
            "Toma de Arco Derecho": "pan_right",
            "Toma Fija": "fix_bg",
            "Ángulo de Cámara": "camera_rotation",
            "Brazo Robótico": "robo_arm",
            "Barrido Rápido": "whip_pan"
        }
        camera_movement = camera_ids.get(camera_selected, "normal")

        # Validar combinación
        valido, creditos_necesarios = validar_combinacion(model, duration, quality)
        if not valido:
            msg = f"❌ Combinación no válida: {model} | {duration}s | {quality}"
            return {"ui": {"text": "Error"}, "result": (msg, "", credit_actualizado)}

        if creditos_necesarios > credit_actualizado:
            msg = f"❌ Créditos insuficientes: {credit_actualizados}/{creditos_necesarios}"
            return {"ui": {"text": "Créditos insuf."}, "result": (msg, "", credit_actualizado)}

        print(f"✅ Créditos suficientes: {credit_actualizado}/{creditos_necesarios}")

        # 🚀 Generar video
        video_id = generate_video_from_image(
            media_path=media_path,
            media_url=uploaded_final_url,
            prompt=prompt,
            duration=duration,
            quality=quality,
            token=jwt_token,
            model=model,
            credit_change=creditos_necesarios,
            style=style,
            camera_movement=camera_movement,
            seed=seed if seed_select else 0,  # Usa seed solo si está fijo
            motion_mode=motion_mode
        )

        if not video_id or isinstance(video_id, str) and ("Créditos agotados" in video_id or "Parámetro inválido" in video_id):
            print(f"❌ Error al generar video: {video_id}")
            credit_actualizado = obtener_credit_package(jwt_token)
            return {"ui": {"text": "Error gen."}, "result": (f"❌ Error: {video_id}", "", credit_actualizado)}

        print(f"🎥 Video iniciado: {video_id}")
        os.environ["VIDEO_ID"] = str(video_id)

        # ✅ Polling y descarga
        result = poll_for_specific_video(jwt_token, video_id)
        if result:
            video_path, video_url = result
            credit_actualizado = obtener_credit_package(jwt_token)
            return {"ui": {"text": f"Listo: {os.path.basename(video_path)}"}, "result": (video_path, video_url, credit_actualizado)}
        else:
            credit_actualizado = obtener_credit_package(jwt_token)
            return {"ui": {"text": "Error descarga"}, "result": ("❌ Error al descargar el video.", "", credit_actualizado)}


# --- Registro del nodo ---
NODE_CLASS_MAPPINGS = {
    "PixVerseGenerateNode": PixVerseGenerateNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PixVerseGenerateNode": "🎬 PixVerse I2V (con Créditos)"
}

# ✅ Requerido por ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']