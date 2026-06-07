#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generacion de la voz de JARVIS.

Dos motores disponibles (se elige con la variable de entorno TTS_MOTOR):
  - "edge"       -> Microsoft edge-tts, voz es-ES-AlvaroNeural (por defecto).
                    Es gratis y NO necesita API key.
  - "elevenlabs" -> ElevenLabs (requiere ELEVENLABS_API_KEY en el archivo .env).

El resultado se guarda en "saludo.mp3" y se reutiliza en los siguientes
arranques para que la reaccion al aplauso sea instantanea.
"""

import os
import asyncio

# Carga las variables del archivo .env (API keys, ajustes de voz, etc.).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv es opcional; si no esta, se usan los valores por defecto.
    pass

# Archivo donde se guarda (cachea) la voz ya generada.
RUTA_AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saludo.mp3")

# Motor por defecto: edge-tts (gratis, sin API key).
TTS_MOTOR = os.getenv("TTS_MOTOR", "edge").strip().lower()

# --- Ajustes de edge-tts --------------------------------------------------
# Voz masculina, espanola y grave. El pitch negativo la hace mas profunda
# y el rate negativo la hace un poco mas lenta y solemne (estilo JARVIS).
EDGE_VOZ = os.getenv("EDGE_VOZ", "es-ES-AlvaroNeural")
EDGE_RATE = os.getenv("EDGE_RATE", "-5%")
EDGE_PITCH = os.getenv("EDGE_PITCH", "-15Hz")

# --- Ajustes de ElevenLabs ------------------------------------------------
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
ELEVEN_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
ELEVEN_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")


def _generar_edge(texto, ruta):
    """Genera la voz con Microsoft edge-tts (online, gratis)."""
    import edge_tts

    async def _run():
        com = edge_tts.Communicate(
            texto,
            voice=EDGE_VOZ,
            rate=EDGE_RATE,
            pitch=EDGE_PITCH,
        )
        await com.save(ruta)

    asyncio.run(_run())


def _generar_elevenlabs(texto, ruta):
    """Genera la voz con ElevenLabs usando la API key del archivo .env."""
    import requests

    if not ELEVEN_API_KEY:
        raise RuntimeError(
            "Falta ELEVENLABS_API_KEY en el archivo .env"
        )
    if not ELEVEN_VOICE_ID:
        raise RuntimeError(
            "Falta ELEVENLABS_VOICE_ID en el archivo .env. "
            "Crea una voz tipo JARVIS en elevenlabs.io y copia su Voice ID."
        )

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": texto,
        "model_id": ELEVEN_MODEL,
        # Ajustes pensados para una voz grave y estable tipo JARVIS.
        "voice_settings": {
            "stability": 0.40,
            "similarity_boost": 0.85,
            "style": 0.30,
            "use_speaker_boost": True,
        },
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    with open(ruta, "wb") as f:
        f.write(r.content)


def generar_saludo(texto, forzar=False):
    """
    Genera el MP3 del saludo si todavia no existe (o si forzar=True).
    Devuelve la ruta del archivo de audio.
    """
    if os.path.exists(RUTA_AUDIO) and not forzar:
        return RUTA_AUDIO

    if TTS_MOTOR == "elevenlabs":
        _generar_elevenlabs(texto, RUTA_AUDIO)
    else:
        _generar_edge(texto, RUTA_AUDIO)
    return RUTA_AUDIO


if __name__ == "__main__":
    # Util para regenerar la voz a mano:  python tts.py
    print(f"Motor de voz: {TTS_MOTOR}")
    ruta = generar_saludo(
        "Hola Lucas, bienvenido a casa, te espera un gran dia",
        forzar=True,
    )
    print(f"Audio generado en: {ruta}")
