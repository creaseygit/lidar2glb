@echo off
echo Building LiDAR2Mesh...
cd /d "%~dp0\.."
pyinstaller build\lidar2mesh.spec --noconfirm
echo.
echo Build complete. Output: dist\lidar2mesh.exe
pause
