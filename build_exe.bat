@echo off
echo.
echo ===================================================
echo   ZigZag Pic - Build Executable
echo ===================================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Building EXE...
pyinstaller --noconsole --onefile --add-data "toss.png;." --add-data "kakao.png;." --name "ZigZagPic_v2.2.4" --version-file "version_info.txt" main.py
echo.
echo Build complete! Check dist/ folder for ZigZagPic.exe
pause
