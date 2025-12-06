@echo off
echo ---------------------------------------------
echo STOPPING RUNNING PROCESSES...
echo ---------------------------------------------
taskkill /F /IM AstitvaDrugHouse.exe >nul 2>&1

echo.
echo ---------------------------------------------
echo CLEANING OLD BUILD FILES...
echo ---------------------------------------------
rmdir /s /q build
rmdir /s /q dist

echo.
echo ---------------------------------------------
echo BUILDING APPLICATION...
echo ---------------------------------------------
pyinstaller --clean --noconfirm AstitvaDrugHouse.spec

echo.
echo ---------------------------------------------
echo BUILD COMPLETE! LAUNCHING APP...
echo ---------------------------------------------
cd dist\AstitvaDrugHouse
start AstitvaDrugHouse.exe
