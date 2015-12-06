#!/bin/bash
# Runs pyinstaller (make 1 file) for linux executable and move it to correct folder

pyinstaller -F ../main_pysoar.py

if [ ! -d "linux" ]; then
	mkdir linux
fi

mv dist/main_pysoar linux/PySoar_linux
rm -rf build
rm -rf dist
rm main_pysoar.spec
