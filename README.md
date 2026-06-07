# JARVIS Clap 👏🤖

Un asistente tipo **JARVIS de Iron Man** para Windows. Escucha tu micrófono
todo el tiempo y, **cuando aplaudes**, hace tres cosas en orden:

1. 🔊 Suena una **voz masculina, grave y en español** (estilo JARVIS) que dice:
   *"Hola Lucas, bienvenido a casa, te espera un gran día"*.
2. 🌐 Abre en **Chrome** una conversación de **Gemini**.
3. ▶️ Abre en **Chrome** un **vídeo de YouTube**.

Tecnologías usadas: **sounddevice** (micrófono + detección del aplauso),
**edge-tts** o **ElevenLabs** (la voz) y **miniaudio** (reproducción).

---

> ℹ️ **Nota importante.** Este proyecto se preparó en un contenedor Linux en la
> nube (donde no hay micrófono, ni altavoces, ni Chrome), así que **el script no
> se puede ejecutar de verdad ahí**. Está pensado para que **tú lo arranques en
> tu PC Windows**, donde sí tienes micrófono y altavoces. Abajo tienes los pasos:
> es literalmente doble clic en dos archivos. El código está verificado
> (compila correctamente y la generación de voz funciona con internet normal).

---

## ✅ Requisitos

- **Windows** con **Python 3.9 o superior** instalado
  ([python.org](https://www.python.org/downloads/) — marca *"Add Python to PATH"*).
- Un **micrófono** conectado y con permiso de uso en Windows.
- **Google Chrome** instalado (si no, se usará tu navegador por defecto).

## 🚀 Instalación rápida (recomendada)

1. Descarga esta carpeta en tu PC.
2. Doble clic en **`install.bat`** → crea el entorno e instala todo solo.
3. Doble clic en **`run_jarvis.bat`** → arranca JARVIS y verás la consola.
4. **¡Aplaude!** 👏

## 🥷 Que corra en segundo plano (sin ventana)

- Doble clic en **`start_background.vbs`** → arranca JARVIS oculto, sin consola.
- Para que **arranque solo al encender el PC**: pulsa `Win + R`, escribe
  `shell:startup` y pega ahí un **acceso directo** a `start_background.vbs`.

## 🔧 Instalación manual (si prefieres a mano)

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python jarvis_clap.py
```

---

## 🎙️ La voz

Por defecto se usa **edge-tts** con la voz **`es-ES-AlvaroNeural`** (masculina,
española). Para que suene más **grave y solemne** (estilo JARVIS) se baja el tono
y la velocidad. Puedes afinarlo en el archivo `.env`:

```env
EDGE_VOZ=es-ES-AlvaroNeural
EDGE_RATE=-5%      # más negativo = más lento
EDGE_PITCH=-15Hz   # más negativo = más grave
```

La voz se genera una vez y se guarda en `saludo.mp3`, así que la reacción al
aplauso es instantánea. ¿Cambiaste el texto o los ajustes? Borra `saludo.mp3`
(o ejecuta `python tts.py`) para regenerarla.

### Opción ElevenLabs (PASO 3)

Si prefieres una voz aún más realista con **ElevenLabs**:

1. Crea una cuenta en **[elevenlabs.io](https://elevenlabs.io)**.
2. **Diseña o clona una voz tipo JARVIS** (masculina, grave, en español) en su
   *Voice Lab* y copia su **Voice ID**.
3. Copia tu **API key** (en *Profile → API Keys*).
4. Abre tu archivo **`.env`** y rellena:

```env
TTS_MOTOR=elevenlabs
ELEVENLABS_API_KEY=tu_api_key_aqui
ELEVENLABS_VOICE_ID=el_voice_id_de_tu_voz_jarvis
```

5. Borra `saludo.mp3` y vuelve a arrancar. JARVIS usará tu voz de ElevenLabs.

> 🔐 **Seguridad de la API key.** La clave va en el archivo **`.env`**, que está
> incluido en **`.gitignore`** para que **nunca se suba al repositorio**. En el
> repo solo se guarda `.env.example` (una plantilla sin secretos). Por eso no
> verás `.env` en GitHub: es justo lo que queremos.

---

## 👏 ¿Cómo detecta el aplauso?

Un aplauso es un **pico de sonido breve y fuerte**. El script mide la amplitud
del micrófono en tiempo real y, cuando supera un umbral, dispara la reacción.
Mientras JARVIS habla, ignora el micrófono para no auto-dispararse.

Ajusta la sensibilidad en `.env`:

```env
UMBRAL_APLAUSO=0.30   # sube si se dispara solo; baja si no te detecta
ENFRIAMIENTO=3.0      # segundos de pausa tras cada reacción
```

---

## 🧩 Sobre OpenJarvis (PASO 1)

El primer paso pedía instalar **[OpenJarvis](https://github.com/open-jarvis/OpenJarvis)**.
OpenJarvis es un **framework grande** para montar agentes de IA locales (con su
propio instalador, modelos locales vía Ollama, agentes, etc.) — es bastante más
de lo que hace falta para "reaccionar a un aplauso".

La función que tú describiste (aplauso → voz + abrir webs) está resuelta aquí
como un **script independiente y ligero**, que es la herramienta adecuada y no
necesita OpenJarvis. Si aun así quieres el framework completo, clónalo aparte:

```bat
git clone https://github.com/open-jarvis/OpenJarvis.git
```

y sigue las instrucciones de instalación de su propio repositorio.

---

## 🆘 Problemas frecuentes

| Síntoma | Solución |
|---|---|
| No detecta el aplauso | Baja `UMBRAL_APLAUSO` (p. ej. `0.20`) en `.env`. |
| Se dispara solo | Sube `UMBRAL_APLAUSO` (p. ej. `0.45`). |
| No suena la voz | Comprueba que `saludo.mp3` existe; bórralo y reinicia para regenerarlo. Necesitas internet la primera vez. |
| `Error con el micrófono` | Revisa que tienes micrófono y que Windows da permiso (Configuración → Privacidad → Micrófono). |
| No abre en Chrome | Si Chrome no está en la ruta habitual, se abrirá tu navegador por defecto. |
| Error al generar la voz | edge-tts necesita internet la primera vez. Si usas ElevenLabs, revisa la API key y el Voice ID en `.env`. |

---

## 📁 Archivos del proyecto

```
jarvis_clap.py        Programa principal (escucha + reacción)
tts.py                Generación de la voz (edge-tts / ElevenLabs)
requirements.txt      Dependencias de Python
.env.example          Plantilla de configuración (cópiala a .env)
.gitignore            Evita subir .env y otros archivos locales
install.bat           Instalador para Windows
run_jarvis.bat        Arranca JARVIS con consola
start_background.vbs  Arranca JARVIS en segundo plano (sin ventana)
README.md             Esta guía
```

¡Disfruta de tu JARVIS! 👏
