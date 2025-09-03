@echo off
REM cd ..
setlocal enableextensions
for /f "tokens=*" %%a in (
'python -c "import wiliot_testers as _; print(_.__file__)"'
) do (
set pyPath=%%a\..
)
cd %pyPath%\association_tester\utils
python continuous_scan.py --host "169.254.245.24" --port 8888 --run_name "test" --time_per_loc 1.0 --asset_str 0000200000
pause