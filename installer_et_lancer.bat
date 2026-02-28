@echo off
chcp 65001 >nul

:: Astuce : si lance par double-clic (pas d'argument), se relance dans cmd /k
:: pour que la fenetre reste toujours ouverte meme en cas d'erreur
if "%~1"=="" (
    cmd /k ""%~f0" run"
    exit /b
)

setlocal EnableDelayedExpansion
title DComite - Installation et Lancement

echo ============================================
echo   DComite - Installation et Lancement
echo ============================================
echo.

:: ---- Detecter la commande Python disponible ----
set PYTHON_CMD=

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :python_found
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

:: ---- Python non trouve : le telecharger ----
echo [1/4] Python non installe. Telechargement en cours...
echo.

set PYTHON_URL=https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe
set PYTHON_INSTALLER=%TEMP%\python_installer.exe

powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'; Write-Host 'Telechargement OK' }"
if %errorlevel% neq 0 (
    echo.
    echo  ERREUR : Impossible de telecharger Python.
    echo  Installez Python manuellement depuis https://www.python.org/downloads/
    echo  puis relancez ce fichier.
    goto :fin_erreur
)

echo  Installation de Python (quelques minutes)...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
if %errorlevel% neq 0 (
    echo  ERREUR : L'installation de Python a echoue.
    goto :fin_erreur
)
del "%PYTHON_INSTALLER%" >nul 2>&1

echo.
echo  Python installe avec succes.
echo  Veuillez FERMER cette fenetre et RELANCER installer_et_lancer.bat
echo  pour que le PATH soit pris en compte.
goto :fin_ok

:python_found
echo [1/4] Python detecte :
%PYTHON_CMD% --version
echo.

:: ---- 2. Verifier pip ----
echo [2/4] Verification de pip...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Installation de pip...
    %PYTHON_CMD% -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo  ERREUR : Impossible d'installer pip.
        goto :fin_erreur
    )
)
echo  pip OK.
echo.

:: ---- 3. Installer les dependances ----
echo [3/4] Installation des dependances...
echo  (Flask, ReportLab, OpenPyXL, Pillow)
echo.

%PYTHON_CMD% -m pip install --upgrade pip --quiet
%PYTHON_CMD% -m pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo.
    echo  ERREUR : Installation des dependances echouee.
    echo  Verifiez votre connexion internet.
    goto :fin_erreur
)
echo.
echo  Dependances OK.
echo.

:: ---- 4. Lancer le serveur web ----
echo [4/4] Lancement du serveur web...
echo.
echo  Adresse : http://localhost:5000
echo  Pour arreter : Ctrl+C ou fermer cette fenetre
echo.

start "" /B cmd /C "timeout /t 3 >nul && start http://localhost:5000"

cd /d "%~dp0"
%PYTHON_CMD% web_app.py
if %errorlevel% neq 0 (
    echo.
    echo  ERREUR : Le serveur s'est arrete avec une erreur (code %errorlevel%).
    goto :fin_erreur
)

:fin_ok
echo.
echo  Termine.
goto :eof

:fin_erreur
echo.
echo  !! Une erreur est survenue. Lisez le message ci-dessus. !!
echo.

:eof
echo Appuyez sur une touche pour fermer...
pause >nul
