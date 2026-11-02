@echo off
chcp 65001 >nul
title Instalando o Ditado BR
cd /d "%~dp0"
echo.
echo   Ditado BR - instalacao
echo   ----------------------
echo.

where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo   Python nao encontrado.
    echo   Instale o Python 3.10 ou mais novo em https://www.python.org/downloads/
    echo   e marque "Add python.exe to PATH" na instalacao.
    pause
    exit /b 1
  )
  set PY=python
) else (
  set PY=py -3
)

echo   [1/4] Criando ambiente isolado...
%PY% -m venv .venv || goto erro

echo   [2/4] Instalando dependencias (pode levar alguns minutos)...
.venv\Scripts\python -m pip install -q --upgrade pip
.venv\Scripts\python -m pip install -q -r requirements.txt || goto erro

where nvidia-smi >nul 2>nul
if not errorlevel 1 (
  echo   [3/4] Placa NVIDIA encontrada: instalando aceleracao ^(~800 MB^)...
  .venv\Scripts\python -m pip install -q -r requirements-nvidia.txt || echo   Aviso: aceleracao nao instalada, o Ditado vai usar o processador.
) else (
  echo   [3/4] Sem placa NVIDIA: o Ditado vai usar o processador.
)

echo   [4/4] Criando atalhos...
.venv\Scripts\python -m ditado.atalhos || goto erro

echo.
echo   Pronto! Abrindo o Ditado BR...
echo   O icone fica perto do relogio. Segure o Ctrl DIREITO, fale e solte.
echo   Na primeira vez ele baixa o modelo de voz (1 a 2 minutos).
start "" .venv\Scripts\pythonw.exe -m ditado
timeout /t 8 >nul
exit /b 0

:erro
echo.
echo   Algo deu errado. Copie a mensagem acima e abra uma issue no GitHub.
pause
exit /b 1
