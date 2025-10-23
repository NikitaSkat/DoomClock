@echo off
echo Building Doom Clock Screensaver...
python -m PyInstaller --onefile --windowed --name="DoomClock" --add-data="doom2016left.ttf;." doom_clock.py

echo Creating proper SCR file...
ren "dist\DoomClock.exe" "Doom Clock.scr"

echo Copying font...
copy "doom2016left.ttf" "." >nul

echo.
echo Build complete!
echo Test: Double-click "Doom Clock.scr"
echo Install: Right-click "Doom Clock.scr" -> "Install"
echo.
pause