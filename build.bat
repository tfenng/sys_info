@echo off
setlocal

uv sync --group build
if errorlevel 1 exit /b %errorlevel%

uv run pyinstaller --onefile --name sys-info main.py
if errorlevel 1 exit /b %errorlevel%

echo Build complete: dist\sys-info.exe
endlocal
