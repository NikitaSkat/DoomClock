@echo off
echo Building DOOM Clock Screensaver...
echo.

:: Создаем папку для билда если её нет
if not exist "build" mkdir "build"

:: Компилируем в exe
python -m PyInstaller --onefile --windowed --name="Doom Clock" --add-data="doom2016left.ttf;." --distpath="build" --workpath="build\temp" --specpath="build" doom_clock.py

echo.
echo Renaming to SCR file...
:: Переименовываем exe в scr
ren "build\Doom Clock.exe" "Doom Clock.scr"

echo.
echo Copying additional files...
:: Копируем шрифт и readme
copy "doom2016left.ttf" "build\" >nul 2>&1
copy "README.txt" "build\" >nul 2>&1
copy "install.bat" "build\" >nul 2>&1

echo.
echo Build complete!
echo Files in 'build' folder:
echo - Doom Clock.scr
echo - doom2016left.ttf
echo - README.txt
echo - install.bat
echo.
echo Ready for distribution!
pause