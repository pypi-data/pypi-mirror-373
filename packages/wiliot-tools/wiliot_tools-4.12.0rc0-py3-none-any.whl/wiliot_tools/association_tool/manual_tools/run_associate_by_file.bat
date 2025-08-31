@echo off
REM cd ..
setlocal enableextensions
for /f "tokens=*" %%a in (
'python -c "import wiliot_tools as _; print(_.__file__)"'
) do (
set pyPath=%%a\..
)
cd %pyPath%\association_tool\manual_tools
python associate_by_file.py
pause