@echo off
:: Verifica se está rodando como admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Executando como Administrador...
    python gui.py
) else (
    echo Solicitando privilegios de Administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)
