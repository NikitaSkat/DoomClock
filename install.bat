@echo off
echo Installing Doom Clock Screensaver...
echo.

:: Копируем файлы в папку Windows для скринсейверов
xcopy "Doom Clock.scr" "%SystemRoot%\System32\" /Y
xcopy "doom2016left.ttf" "%SystemRoot%\Fonts\" /Y

echo.
echo Installation complete!
echo Opening screensaver settings...
timeout /t 3 /nobreak >nul
rundll32.exe desk.cpl,InstallScreenSaver "%SystemRoot%\System32\Doom Clock.scr"