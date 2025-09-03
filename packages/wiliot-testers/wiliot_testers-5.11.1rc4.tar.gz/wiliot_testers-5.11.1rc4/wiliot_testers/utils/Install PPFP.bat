@echo off

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller

REM Change the current directory to the script's location
cd /d "%~dp0"

REM Navigate 2 directories up
cd ..\..

REM Execute PyInstaller command
echo Executing Wiliot Exe creating command...
pyinstaller --onefile --windowed --add-data ".\wiliot_testers\docs\wiliot_logo.png;.\docs" .\wiliot_testers\utils\ppfp_tool.py

REM Copy the exe file to the desired location
copy "dist\ppfp_tool.exe" "\utils\ppfp_tool.exe"

REM Pause for a moment to display the final message
timeout /t 5 >nul
exit
