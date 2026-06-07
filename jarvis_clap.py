#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Clap - Asistente tipo JARVIS de Iron Man activado por aplausos.

Escucha el microfono de forma CONTINUA, en segundo plano. Cuando detecta
un APLAUSO hace tres cosas EN ORDEN:

  1. Reproduce una voz masculina, grave y en espanol (estilo JARVIS) que dice:
     "Hola Lucas, bienvenido a casa, te espera un gran dia".
  2. Abre en Chrome una URL de Gemini.
  3. Abre en Chrome un video de YouTube.

Tecnologias (segun lo pedido):
  - sounddevice -> escucha del microfono y deteccion del aplauso
  - edge-tts / ElevenLabs (ver tts.py) -> generacion de la voz
  - miniaudio   -> reproduccion del audio

Pensado para Windows. Para ejecutarlo en segundo plano sin ventana usa
"start_background.vbs" (ver README.md).
"""

import os
import sys
import time
import queue
import threading
import webbrowser

import numpy as np
import sounddevice as sd
import miniaudio

from tts import generar_saludo, RUTA_AUDIO

# ---------------------------------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------------------------------
SALUDO = "Hola Lucas, bienvenido a casa, te espera un gran dia"

URL_GEMINI = "https://gemini.google.com/share/d2dfbce3971b"
URL_YOUTUBE = "https://youtu.be/Mm3Um3-kkpM?si=ZHmPi8yc2vw_tLy9"

# Sensibilidad del aplauso (0.0 - 1.0). Sube el valor si JARVIS se dispara
# solo; bajalo si no te detecta el aplauso. 0.30 es un buen punto de partida.
UMBRAL_APLAUSO = float(os.getenv("UMBRAL_APLAUSO", "0.30"))

# Segundos de pausa tras cada reaccion antes de volver a escuchar aplausos.
ENFRIAMIENTO = float(os.getenv("ENFRIAMIENTO", "3.0"))

FRECUENCIA = 44100   # Hz (calidad de muestreo del microfono)
CANALES = 1
TAM_BLOQUE = 2048    # muestras por bloque (~46 ms)

# ---------------------------------------------------------------------------
# Estado interno de la deteccion
# ---------------------------------------------------------------------------
_eventos = queue.Queue()        # aplausos pendientes de atender
_ocupado = threading.Event()    # activo mientras JARVIS esta reaccionando
_ultimo_disparo = 0.0           # momento del ultimo aplauso aceptado


def _callback(indata, frames, time_info, status):
    """Se ejecuta automaticamente por cada bloque de audio del microfono."""
    global _ultimo_disparo
    # Mientras JARVIS reacciona (suena su propia voz) ignoramos el microfono
    # para no auto-dispararnos.
    if _ocupado.is_set():
        return

    pico = float(np.max(np.abs(indata)))   # amplitud maxima del bloque
    ahora = time.monotonic()

    # Un aplauso es un pico de sonido breve y fuerte.
    if pico >= UMBRAL_APLAUSO and (ahora - _ultimo_disparo) >= ENFRIAMIENTO:
        _ultimo_disparo = ahora
        _eventos.put(pico)


def reproducir(ruta):
    """Reproduce un MP3 de principio a fin con miniaudio (bloqueante)."""
    info = miniaudio.decode_file(ruta)
    duracion = info.num_frames / info.sample_rate

    flujo = miniaudio.stream_file(
        ruta,
        output_format=miniaudio.SampleFormat.SIGNED16,
        nchannels=2,
        sample_rate=44100,
    )
    dispositivo = miniaudio.PlaybackDevice(
        output_format=miniaudio.SampleFormat.SIGNED16,
        nchannels=2,
        sample_rate=44100,
    )
    dispositivo.start(flujo)
    # Esperamos a que termine de sonar (+ un pequeno margen).
    time.sleep(duracion + 0.6)
    dispositivo.close()


def _buscar_chrome():
    """Devuelve un navegador Chrome registrable, o None si no se encuentra."""
    posibles = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for ruta in posibles:
        if os.path.exists(ruta):
            try:
                return webbrowser.get(f'"{ruta}" %s')
            except Exception:
                return None
    return None


def abrir_en_chrome(url):
    """Abre una URL en Chrome; si no encuentra Chrome usa el navegador por defecto."""
    navegador = _buscar_chrome()
    try:
        if navegador is not None:
            navegador.open(url)
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"[!] No se pudo abrir {url}: {e}")
        webbrowser.open(url)


def reaccionar():
    """La secuencia JARVIS: 1) voz  2) Gemini en Chrome  3) YouTube en Chrome."""
    global _ultimo_disparo
    _ocupado.set()
    try:
        print("[JARVIS] Aplauso detectado. Reaccionando...")

        # 1) La voz
        if os.path.exists(RUTA_AUDIO):
            reproducir(RUTA_AUDIO)
        else:
            print("[!] No hay audio del saludo. Revisa edge-tts / ElevenLabs.")

        # 2) Gemini en Chrome
        abrir_en_chrome(URL_GEMINI)
        time.sleep(0.8)

        # 3) YouTube en Chrome
        abrir_en_chrome(URL_YOUTUBE)
    finally:
        # Margen para que se vacie el buffer del microfono tras la voz.
        time.sleep(0.5)
        _ultimo_disparo = time.monotonic()
        # Descarta aplausos espurios acumulados durante la reaccion.
        while not _eventos.empty():
            try:
                _eventos.get_nowait()
            except queue.Empty:
                break
        _ocupado.clear()
        print("[JARVIS] Escuchando de nuevo...\n")


def main():
    print("=" * 60)
    print(" JARVIS Clap  -  escuchando el microfono")
    print("=" * 60)

    # Genera (o reutiliza) el audio del saludo ANTES de empezar a escuchar,
    # para que la reaccion al aplauso sea instantanea.
    print("[JARVIS] Preparando la voz...")
    try:
        generar_saludo(SALUDO)
        print(f"[JARVIS] Voz lista: {RUTA_AUDIO}")
    except Exception as e:
        print(f"[!] No se pudo generar la voz: {e}")
        print("    Revisa tu conexion o tu API key. Sigo escuchando igual.")

    print(f"[JARVIS] Umbral de aplauso: {UMBRAL_APLAUSO} "
          f"(ajustable con la variable UMBRAL_APLAUSO)")
    print("[JARVIS] Aplaude para activar.  Pulsa Ctrl+C para salir.\n")

    try:
        with sd.InputStream(
            channels=CANALES,
            samplerate=FRECUENCIA,
            blocksize=TAM_BLOQUE,
            dtype="float32",
            callback=_callback,
        ):
            # Bucle principal: espera aplausos y los atiende uno a uno.
            while True:
                try:
                    _eventos.get(timeout=0.5)
                except queue.Empty:
                    continue
                reaccionar()
    except KeyboardInterrupt:
        print("\n[JARVIS] Hasta luego, Lucas.")
    except Exception as e:
        print(f"[!] Error con el microfono: {e}")
        print("    Comprueba que tienes un microfono conectado y permitido.")
        sys.exit(1)


if __name__ == "__main__":
    main()
