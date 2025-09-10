# PixVerse_Extend_Node.py
import os
import requests
import json
import time
import uuid
import random
from pixverse_ai.plogin import *

# === NODO DE COMFYUI ===
class PixVerseExtendNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "Continue the scene with dynamic movement",
                    "multiline": True,
                    "tooltip": "Prompt para extender el video"
                }),
                "model_version": (["v3.5", "v4", "v4.5", "v5"], {"default": "v5"}),
                "duration": ([5, 8], {"default": 5}),
                "quality": (["360p", "540p", "720p", "1080p"], {"default": "360p"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "use_custom_seed": ("BOOLEAN", {"default": False}),  # No usado, pero lo dejamos
                "jwt_token": ("STRING", {"forceInput": True}),
                "media_path": ("STRING", {"forceInput": True}),
                "uploaded_final_url": ("STRING", {"forceInput": True}),
                "last_frame_url": ("STRING", {"forceInput": True}),
                "duration_seconds": ("INT", {"forceInput": True}),
                "extend": ("BOOLEAN", {"default": False, "label_on": "Extender", "label_off": "Detener"})
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("video_path", "video_url", "credit")
    FUNCTION = "extend_video"
    CATEGORY = "PixVerse"
    OUTPUT_NODE = True  # Nodo de salida

    def extend_video(self, prompt, model_version, duration, quality, seed, use_custom_seed,
                     jwt_token, media_path, uploaded_final_url, last_frame_url, duration_seconds, extend):

        if not extend:
            return {"ui": {"text": "Extensión desactivada"}, "result": ("❌ Extensión no activada.", "")}

        if not jwt_token:
            return {"ui": {"text": "Token faltante"}, "result": ("❌ JWT Token no proporcionado.", "")}

        if not media_path or not uploaded_final_url or not last_frame_url:
            return {"ui": {"text": "Datos de video faltantes"}, "result": ("❌ Faltan datos del video subido.", "")}

        # Mapeo de modelos
        model_map = {
            "v3.5": "v3.5",
            "v4": "v4",
            "v4.5": "v4.5",
            "v5": "v5"
        }
        model = model_map[model_version]

        # Validar combinación
        valido, creditos = validar_combinacion(model, duration, quality)
        if not valido:
            msg = f"❌ Combinación no válida: {model} | {duration}s | {quality}"
            return {"ui": {"text": "Error"}, "result": (msg, "")}

        creditos_paquete = obtener_credit_package(jwt_token)
        if creditos > creditos_paquete:
            msg = f"❌ Créditos insuficientes: {creditos_paquete}/{creditos}"
            return {"ui": {"text": "Créditos insuficientes"}, "result": (msg, "")}

        print(f"✅ Créditos suficientes: {creditos_paquete}/{creditos}")

        # Calcular credit_change
        credit_change = min(((duration_seconds + 4) // 5) * 10, 60)

        # Extender video
        print("🚀 Extendiendo video...")
        video_id = extend_pixverse_video(
            token=jwt_token,
            prompt=prompt,
            model=model,
            duration=duration,
            quality=quality,
            seed=seed,
            credit_change=credit_change,
            customer_video_path=media_path,
            customer_video_url=uploaded_final_url,
            customer_video_duration=duration_seconds,
            customer_video_last_frame_url=last_frame_url
        )

        if not video_id or "Créditos agotados" in str(video_id) or "Parámetro inválido" in str(video_id):
            return {"ui": {"text": "Error"}, "result": (f"❌ Error al extender video: {video_id}", "")}

        print(f"🎥 Video extendido iniciado: {video_id}")
        os.environ["VIDEO_ID"] = str(video_id)
        os.environ["PROMPT"] = prompt

        # Polling y descarga
        result = poll_for_specific_video_txt(jwt_token, video_id, prompt)
        if result:
            credit_actualizado = obtener_credit_package(jwt_token)
            print(f"[PixVerse] ✅ Login exitoso. Créditos: {credit_actualizado}")
            video_path, video_url = result
            return {"ui": {"text": f"Listo: {os.path.basename(video_path)}"}, "result": (video_path, video_url, credit_actualizado)}
        else:
            return {"ui": {"text": "Error descarga"}, "result": ("❌ Error al descargar el video extendido.", "", 0)}

