@echo off
cd /d "%~dp0"
echo === SUBCONTROL — compilando ejecutable ===
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --noconsole --clean --name SubControl ^
  --hidden-import pymavlink.dialects.v20.ardupilotmega subcontrol.py
copy /y "dist\SubControl.exe" "SubControl.exe" >nul
echo.
echo Listo: SubControl.exe (en la carpeta del proyecto) y dist\SubControl.exe
pause
