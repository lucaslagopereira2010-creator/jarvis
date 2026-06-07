@echo off
REM ============================================================
REM  Instalador de JARVIS Clap para Windows
REM  Crea un entorno virtual e instala todas las dependencias.
REM ============================================================
cd /d "%~dp0"

echo.
echo [1/4] Creando entorno virtual (.venv)...
python -m venv .venv
if errorlevel 1 (
    echo.
    echo ERROR: No se encontro Python. Instala Python 3 desde python.org
    echo y marca la casilla "Add Python to PATH".
    pause
    exit /b 1
)

echo [2/4] Activando entorno virtual...
call .venv\Scripts\activate.bat

echo [3/4] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [4/4] Preparando el archivo .env...
if not exist .env copy .env.example .env

echo.
echo ============================================================
echo  Listo. Ahora ejecuta run_jarvis.bat para arrancar JARVIS,
echo  o start_background.vbs para que corra en segundo plano.
echo ============================================================
pause
