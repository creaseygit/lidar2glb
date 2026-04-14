@echo off
echo Building LiDAR2GLB...
cd /d "%~dp0\.."
pyinstaller build\lidar2glb.spec --noconfirm
echo.
echo Build complete. Output: dist\lidar2glb.exe
pause
