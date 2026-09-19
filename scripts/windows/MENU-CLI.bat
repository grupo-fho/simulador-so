@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
if not exist "SimuladorCLI.exe" goto incompleto
if not exist "Testar.exe" goto incompleto
if not exist "runtime\lib\modules" goto incompleto

:menu
cls
echo SIMULADOR DE SISTEMAS OPERACIONAIS
echo.
echo 1 - Demonstracao: FCFS, Round Robin e prioridades
echo 2 - Demonstracao do sistema de arquivos
echo 3 - Executar testes automatizados
echo 4 - Abrir resultados
echo 5 - Ajuda da linha de comando
echo 0 - Sair
echo.
choice /c 123450 /n /m "Escolha uma opcao: "
if errorlevel 255 goto falha
if errorlevel 6 goto sair
if errorlevel 5 goto ajuda
if errorlevel 4 goto resultados
if errorlevel 3 goto testes
if errorlevel 2 goto arquivos
if errorlevel 1 goto demonstracao
goto sair

:demonstracao
call :novaPasta
if errorlevel 1 goto falha
SimuladorCLI.exe --carga cargas\mista.txt --politica FCFS --saida "%saida%\FCFS"
if errorlevel 1 goto falha
SimuladorCLI.exe --carga cargas\mista.txt --politica RR --quantum 3 --saida "%saida%\RR"
if errorlevel 1 goto falha
SimuladorCLI.exe --carga cargas\mista.txt --politica PRIORIDADE --saida "%saida%\PRIORIDADE"
if errorlevel 1 goto falha
echo.
echo Demonstracao concluida. Logs e metricas: %saida%
start "" "%cd%\%saida%"
pause
goto menu

:arquivos
call :novaPasta
if errorlevel 1 goto falha
SimuladorCLI.exe --carga cargas\arquivos.txt --saida "%saida%\arquivos"
if errorlevel 1 goto falha
echo.
type "%saida%\arquivos\eventos.log"
pause
goto menu

:testes
Testar.exe
if errorlevel 1 goto falha
pause
goto menu

:resultados
if not exist resultados mkdir resultados
if not exist resultados goto falha
start "" "%cd%\resultados"
goto menu

:ajuda
SimuladorCLI.exe --ajuda
pause
goto menu

:novaPasta
set "saida=resultados\execucao-%RANDOM%-%RANDOM%"
if exist "%saida%" goto novaPasta
mkdir "%saida%"
if errorlevel 1 exit /b 1
exit /b 0

:falha
echo.
echo A operacao falhou. Confira a mensagem acima.
echo Extraia a pasta completa em um local gravavel, como Downloads.
pause
goto menu

:incompleto
echo Pacote incompleto. Extraia TODO o ZIP antes de abrir INICIAR.bat.
echo Nao mova o executavel sozinho para outra pasta.
pause
popd
exit /b 1

:sair
popd
endlocal
exit /b 0
