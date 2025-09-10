# File: comfyui/custom_nodes/pixverse_login_node.py

import requests
import uuid
import time
from pixverse_ai.plogin import *

class PixVerseLogin:
    def __init__(self):
        self.cached_token = ""
        self.cached_credit = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "username": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Correo electrónico para iniciar sesión en PixVerse"
                }),
                "password": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "password": True,
                    "tooltip": "Contraseña de la cuenta PixVerse"
                }),
                "refresh_token": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Actualizar Token",
                    "label_off": "Usar Caché",
                    "tooltip": "Activa para refrescar el token. Desactiva para usar el último token sin hacer login."
                })
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("token", "credit")
    FUNCTION = "login"
    CATEGORY = "PixVerse"

    def login(self, username, password, refresh_token):
        if not refresh_token:
            print("[PixVerse] 🔴 Modo caché: no se realizará login. Usando token guardado.")
            return (self.cached_token, self.cached_credit)

        print("[PixVerse] ✅ Actualización de token activada. Iniciando sesión...")

        if not username or not password:
            print("[PixVerse] ❌ Usuario o contraseña vacíos. No se puede hacer login.")
            return (self.cached_token, self.cached_credit)

        token = iniciar_sesion(username, password)
        if token:
            credit = obtener_credit_package(token)
            print(f"[PixVerse] ✅ Login exitoso. Créditos: {credit}")
            self.cached_token = token
            self.cached_credit = credit
            return (token, credit)
        else:
            print("[PixVerse] ⚠️  Error al iniciar sesión. Manteniendo token anterior si existe.")
            return (self.cached_token, self.cached_credit)
    