@echo off
title Publicar Radar de Innovacion en GitHub
cd /d "%~dp0"
set REPO=juanpradomts-dev/radar-innovacion
echo.
echo   1/4  Creando el repo publico %REPO% y subiendo el codigo...
gh repo create %REPO% --public --description "Radar de Innovacion: tendencias que cambian el mundo, se actualiza solo cada 3 h" --homepage "https://juanpradomts-dev.github.io/radar-innovacion/" --source . --push
if errorlevel 1 goto soloPush
goto pages

:soloPush
echo   [!] No se pudo crear. Si el repo ya existe, se intenta solo el push.
git push -u origin main

:pages
echo.
echo   2/4  Activando GitHub Pages - publicado por GitHub Actions...
gh api -X POST repos/%REPO%/pages -f build_type=workflow >nul 2>&1
gh api -X PUT repos/%REPO%/pages -f build_type=workflow >nul 2>&1
echo.
echo   3/4  Clave gratuita de OpenAlex - opcional, mejora la medicion de investigacion.
echo        Como crearla: https://help.openalex.org/api/authentication/ . Pegala y Enter, o solo Enter para omitir:
set KEY=
set /p KEY=        Clave: 
if "%KEY%"=="" goto lanzar
gh secret set OPENALEX_API_KEY -R %REPO% -b "%KEY%"
set KEY=

:lanzar
echo.
echo   4/4  Lanzando la primera actualizacion...
gh workflow run actualizar.yml -R %REPO%
echo.
echo   Actualizando el acceso directo del escritorio para que abra la pagina publicada...
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set ESCRITORIO=%%D
> "%ESCRITORIO%\Radar de Innovacion.url" echo [InternetShortcut]
>> "%ESCRITORIO%\Radar de Innovacion.url" echo URL=https://juanpradomts-dev.github.io/radar-innovacion/
echo.
echo   Listo. En unos 5 minutos queda en:
echo   https://juanpradomts-dev.github.io/radar-innovacion/
echo.
pause
