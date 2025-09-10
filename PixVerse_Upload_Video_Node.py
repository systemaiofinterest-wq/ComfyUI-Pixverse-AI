# PixVerseUploadVideoNode.py

import os
import requests
import uuid
import time
import oss2
import cv2
from urllib.parse import unquote
import json
import tempfile  # ✅ Importado
from pixverse_ai.plogin import *

# === Configuración de rutas temporales ===
temp_dir = tempfile.gettempdir()


# === NODO DE COMFYUI ===
class PixVerseUploadVideoNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Ruta del video local (de otro nodo)"
                }),
                "jwt_token": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "JWT Token del login"
                }),
                "upload": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Subir",
                    "label_off": "No subir"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("media_path", "uploaded_final_url", "last_frame_url", "duration")
    FUNCTION = "upload_video"
    CATEGORY = "PixVerse"

    def upload_video(self, video, jwt_token, upload):
        if not upload:
            return ("❌ Subida no activada.", "", "", 0)
        if not jwt_token:
            return ("❌ JWT Token no proporcionado.", "", "", 0)
        if not video or not os.path.exists(video):
            return ("❌ Archivo de video no encontrado.", "", "", 0)

        video_path = video
        duration = obtener_segundos_video(video_path)
        if not duration:
            return ("❌ No se pudo obtener la duración del video.", "", "", 0)

        print(f"🎥 Video detectado: {video_path} | Duración: {duration}s")

        # Verificar créditos
        creditos = obtener_credit_package(jwt_token)
        if creditos < 20:
            return (f"❌ Créditos insuficientes: {creditos}/20", "", "", 0)

        print(f"✅ Créditos disponibles: {creditos}")

        # Obtener token de subida
        token_data = get_upload_token(jwt_token)
        if not token_data:
            return ("❌ Error al obtener token de subida.", "", "", 0)

        # Subir a OSS
        media_path, _ = upload_video_to_oss(video_path, token_data)
        if not media_path:
            return ("❌ Error al subir a OSS.", "", "", 0)

        # Confirmar en PixVerse
        uploaded_final_url = confirm_upload_on_pixverse_video(media_path, jwt_token)
        if not uploaded_final_url:
            return ("❌ Error al confirmar en PixVerse.", "", "", 0)

        # Obtener último fotograma
        last_frame_url = get_last_frame(jwt_token, media_path, duration)
        if not last_frame_url:
            print("⚠️ No se pudo obtener el último fotograma.")

        print(f"🎉 Video subido exitosamente: {uploaded_final_url}")
        return (media_path, uploaded_final_url, last_frame_url or "", duration)

# --- Registro del nodo ---
NODE_CLASS_MAPPINGS = {
    "PixVerseUploadVideoNode": PixVerseUploadVideoNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PixVerseUploadVideoNode": "📤 PixVerse Upload Video"
}

# ✅ Requerido por ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']