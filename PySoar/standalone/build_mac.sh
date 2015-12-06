#!/bin/bash
# Runs pyinstaller (make 1 file) for mac executable and move it to correct folder
# to do: change stand-alone boolean from bash?

pyinstaller -F ../main_pysoar.py

if [ ! -d "mac" ]; then
	mkdir mac
fi

mv dist/main_pysoar mac/PySoar_mac
rm -rf build
rm -rf dist
rm main_pysoar.spec
