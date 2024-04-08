@echo off
@title Scratch2Fusion
setlocal enabledelayedexpansion

REM Runs the Scratch2Fusion.py script in the same folder
python "%~dp0/Scratch2Fusion.py" %*
