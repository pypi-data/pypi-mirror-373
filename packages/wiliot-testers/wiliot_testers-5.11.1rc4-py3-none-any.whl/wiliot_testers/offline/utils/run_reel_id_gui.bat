@echo off
REM cd ..
setlocal enableextensions
for /f "tokens=*" %%a in (
'python -c "import wiliot_testers as _; print(_.__file__)"'
) do (
set pyPath=%%a\..
)
cd %pyPath%\offline\utils
:loop
python reel_id_gui.py --env prod --owner_id 852213717688
@pause