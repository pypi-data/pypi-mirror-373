@echo off
REM cd ..
setlocal enableextensions
for /f "tokens=*" %%a in (
'python -c "import wiliot_testers as _; print(_.__file__)"'
) do (
set pyPath=%%a\..
)
cd %pyPath%\utils
:loop
python convert_log_to_offline.py
IF "%ERRORLEVEL%"=="1" goto loop
echo %ERRORLEVEL%
pause