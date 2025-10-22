@echo off
echo =====================================
echo AutoClicker Pro - Instalacao
echo =====================================
echo.

echo Instalando dependencias...
pip install -r requirements.txt

if %errorlevel% == 0 (
    echo.
    echo =====================================
    echo Instalacao concluida com sucesso!
    echo =====================================
    echo.
    echo Execute: python gui.py
    echo.
) else (
    echo.
    echo =====================================
    echo Erro na instalacao!
    echo =====================================
    echo.
)

pause
