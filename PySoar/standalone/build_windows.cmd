#!/bin/bash
# Runs pyinstaller (make 1 file) for mac executable and move it to correct folder

# to do: change stand-alone boolean from bash?

pyinstaller -F --noconsole ../main_pysoar.py
IF NOT EXIST "windows64" (
	mkdir windows64
)
move dist\main_pysoar.exe windows64\PySoar_windows64.exe
del main_pysoar.spec
del /S /Q dist
del /S /Q build
rmdir /S /Q dist
rmdir /S /Q build
