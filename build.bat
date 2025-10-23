@echo off
echo Building Doom Clock Screensaver...
python -m PyInstaller --onefile --windowed --name="Doom Clock" --add-data="doom2016left.ttf;." doom_clock.py

echo.
echo Build complete!
echo Now rename "dist\Doom Clock.exe" to "Doom Clock.scr"
echo.
pause