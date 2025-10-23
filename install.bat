@echo off
echo Installing DOOM Clock Screensaver...
echo.

:: Копируем скринсейвер в системную папку
copy "Doom Clock.scr" "%SystemRoot%\System32\" >nul 2>&1
copy "doom2016left.ttf" "%SystemRoot%\Fonts\" >nul 2>&1

echo.
echo Installation complete!
echo.
echo To enable after lock screen:
echo 1. Right-click on desktop -> Personalize -> Screensaver
echo 2. Select "DOOM Clock" from the list
echo 3. Check "On resume, display logon screen"
echo 4. Set wait time and click "Apply"
echo.
pause

:: Открываем настройки заставки
rundll32.exe desk.cpl,InstallScreenSaver "%SystemRoot%\System32\Doom Clock.scr"