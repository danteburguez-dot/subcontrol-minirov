@echo off
cd /d "%~dp0"
echo === SUBCONTROL — compilando ejecutable ===
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --noconsole --clean --name SubControl ^
  --hidden-import pymavlink.dialects.v20.ardupilotmega subcontrol.py
echo.
echo Listo: dist\SubControl.exe
pause
