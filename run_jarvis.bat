@echo off
REM Arranca JARVIS Clap mostrando la consola (util para ver mensajes/ajustar).
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
python jarvis_clap.py
pause
