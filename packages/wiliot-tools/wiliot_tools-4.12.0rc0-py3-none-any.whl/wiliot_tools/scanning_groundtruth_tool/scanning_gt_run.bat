@echo off
REM cd ..
setlocal enableextensions
for /f "tokens=*" %%a in (
'python -c "import wiliot_tools as _; print(_.__file__)"'
) do (
set pyPath=%%a\..
)
cd %pyPath%\scanning_groundtruth_tool
:loop
python scanning_gt.py
IF "%ERRORLEVEL%"=="1" goto loop
echo %ERRORLEVEL%
pause