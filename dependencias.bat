@echo off
title SUBCONTROL - Gestor de dependencias
cd /d "%~dp0"

:MENU
cls
echo ==================================================
echo    SUBCONTROL - GESTOR DE DEPENDENCIAS
echo ==================================================
echo.
echo    1. INSTALAR todos los requerimientos
echo    2. DESINSTALAR todos los requerimientos
echo    3. VER estado de los paquetes
echo    4. Salir
echo.
set /p op="Elegi una opcion (1-4): "

if "%op%"=="1" goto INSTALAR
if "%op%"=="2" goto DESINSTALAR
if "%op%"=="3" goto VER
if "%op%"=="4" exit /b
goto MENU

:INSTALAR
echo.
echo === Instalando: opencv, numpy, pillow, pymavlink, pygame,
echo     pyinstaller, trimesh, scipy ===
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel%==0 (
    echo.
    echo [OK] Instalacion completa. Ya podes compilar con build.bat
    echo      o correr la app con:  python subcontrol.py
) else (
    echo.
    echo [AVISO] Hubo un error. Revisa el mensaje de arriba.
)
echo.
pause
goto MENU

:DESINSTALAR
echo.
echo === Desinstalando los paquetes de SUBCONTROL ===
echo.
echo AVISO: esto quita los siguientes paquetes de Python:
echo    opencv-python-headless, numpy, Pillow, pymavlink,
echo    pygame, pyinstaller, trimesh, scipy
echo Si otro proyecto tuyo usa numpy o scipy, dejalos instalados
echo (elegi N y desinstala solo los demas cuando pip pregunte).
echo.
set /p ok="Confirmar desinstalacion (S/N): "
if /i not "%ok%"=="S" goto MENU
python -m pip uninstall -y opencv-python-headless numpy Pillow pymavlink pygame pyinstaller trimesh scipy
echo.
echo [OK] Desinstalacion completa. La app deja de funcionar hasta
echo      que vuelvas a INSTALAR (opcion 1). El .exe compilado no
echo      necesita estos paquetes: sigue funcionando igual.
echo.
pause
goto MENU

:VER
echo.
echo === Estado de los paquetes ===
python -m pip show opencv-python-headless numpy Pillow pymavlink pygame pyinstaller trimesh scipy 2>nul | findstr /C:"Name" /C:"Version" /C:"WARNING"
echo.
echo (Si un paquete no aparece en la lista, no esta instalado)
pause
goto MENU
