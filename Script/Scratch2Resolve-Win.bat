@echo off
@title Scratch2Resolve
setlocal enabledelayedexpansion

REM Runs the Scratch2Resolve.py script in the same folder
python "%~dp0/Scratch2Resolve.py" %*
