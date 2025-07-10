@echo off
setlocal

:: Set root folder
set "ROOT_DIR=%~dp0"

:: Set output file path
set "OUTPUT=%ROOT_DIR%directory_tree.txt"

:: Generate directory tree and save to file
echo Generating directory tree for: %ROOT_DIR%
tree "%ROOT_DIR%" /F /A > "%OUTPUT%"

echo Done! Output saved to: %OUTPUT%"
pause
