@echo off
setlocal
pushd "%~dp0" || exit /b 1
if not exist "SimuladorSO.exe" (
 echo Extraia TODO o pacote portatil antes de iniciar.
 pause
 popd
 exit /b 1
)
start "" "%~dp0SimuladorSO.exe"
popd
endlocal
