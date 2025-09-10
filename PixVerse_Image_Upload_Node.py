# PixVerse_Image_Upload_Node.py

import os
import requests
import uuid
import time
import oss2
from urllib.parse import unquote
from torchvision.transforms import ToPILImage
import tempfile
import json
from pixverse_ai.plogin import *

# === Configuración de rutas temporales ===
temp_dir = tempfile.gettempdir()

# === NODO DE COMFYUI ===
class PixVerseImageUploadNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
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

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("📤 Imagen Subida (para generar video)",)
    FUNCTION = "upload_image"
    CATEGORY = "PixVerse"

    def upload_image(self, image, jwt_token, upload):
        if not upload:
            result = {"success": False, "error": "Subida no activada"}
            return (json.dumps(result),)

        if not jwt_token:
            result = {"success": False, "error": "JWT Token no proporcionado"}
            return (json.dumps(result),)

        # Convertir imagen de ComfyUI a PIL
        try:
            to_pil = ToPILImage()
            temp_path = os.path.join(temp_dir, f"pixverse_upload_{uuid.uuid4().hex}.png")

            if len(image.shape) == 4:
                image = image[0]  # Tomar primer frame

            pil_image = to_pil(image.permute(2, 0, 1).cpu())
            pil_image.save(temp_path, format='PNG')
            print(f"🖼️ Imagen temporal guardada: {temp_path}")
        except Exception as e:
            error = {"success": False, "error": f"Error al procesar imagen: {str(e)}"}
            return (json.dumps(error),)

        # Verificar créditos
        creditos = obtener_credit_package(jwt_token)
        if creditos < 20:
            result = {"success": False, "error": f"Créditos insuficientes: {creditos}/20"}
            return (json.dumps(result),)

        print(f"✅ Créditos disponibles: {creditos}")

        # Obtener token de subida
        token_data = get_upload_token(jwt_token)
        if not token_data:
            result = {"success": False, "error": "Error al obtener token de subida"}
            return (json.dumps(result),)

        # Subir a OSS
        media_path, _ = upload_image_to_oss(temp_path, token_data)
        if not media_path:
            result = {"success": False, "error": "Error al subir a OSS"}
            return (json.dumps(result),)

        # Confirmar en PixVerse
        size = os.path.getsize(temp_path)
        uploaded_final_url = confirm_upload_on_pixverse(
            path=media_path,
            name=os.path.basename(media_path),
            size=size,
            token_header=jwt_token
        )

        # Limpiar archivo temporal
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"⚠️ No se pudo eliminar temporal: {e}")

        if uploaded_final_url:
            result = {
                "success": True,
                "jwt_token": jwt_token,
                "uploaded_final_url": uploaded_final_url,
                "media_path": media_path,
                "duration_seconds": 5,  # Puedes ajustarlo si tienes metadatos
                "last_frame_url": uploaded_final_url,  # Útil para extend
                "error": None
            }
            return (json.dumps(result),)
        else:
            result = {"success": False, "error": "Error al confirmar en PixVerse"}
            return (json.dumps(result),)


# --- Registro del nodo ---
NODE_CLASS_MAPPINGS = {
    "PixVerseImageUploadNode": PixVerseImageUploadNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PixVerseImageUploadNode": "📤 PixVerse Upload Image"
}

# ✅ Requerido por ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']