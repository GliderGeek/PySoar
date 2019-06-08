# PySoar
[![Build Status](https://travis-ci.org/GliderGeek/PySoar.svg?branch=master)](https://travis-ci.org/GliderGeek/PySoar)

PySoar automates the analysis of glider competitions. It starts with a Soaring Spot URL and delivers a spreadsheet as output.

A screenshot of the program:

[![PySoar screenshot](https://github.com/glidergeek/pysoar/raw/master/images/pysoar_screenshot_thumbnail.jpg)](https://github.com/glidergeek/pysoar/raw/master/images/pysoar_screenshot.png)

An example analysis is provided for [this](http://www.soaringspot.com/en/sallandse-tweedaagse-2014/results/club/task-1-on-2014-06-21/daily) competition day:

[![Example pysoar analysis](https://github.com/glidergeek/pysoar/raw/master/images/excel_logo.jpg)](https://github.com/glidergeek/pysoar/raw/master/example_analysis.xls)


## Stand alone versions
Stand alone versions for Windows, Mac and Linux are available under [releases](https://github.com/GliderGeek/PySoar/releases).

Apart from Excel/Open Office for viewing the spreadsheet, no extra software is needed.

## Limitations
The following limitations are (currently) in place:

- no restart after 1st turnpoint
- no penalties for missing turnpoints -> outlanding
- no multiple start points


## Development
For development, the following steps need to be taken:

1. Install python requirements

```
pip install -r requirements.txt
```

## Building an executable
This chapter explains how to create a pysoar executable

Note: it is important to use the system python3.6
- running inside virtualenv causes wxpython issues
- running python3.7 causes PyInstaller issues

### Patch pygeodesy

There is currently a problem with the pygeodesy library and pyinstaller for which pygeodesy needs to be cloned locally, patched and installed instead of taking the version from pypi.

To patch `pygeodesy`:
- clone repo locally
- change `_ismodule` callable in `pygeodesy/__init__.py`. Replace its content with a single `pass` statement.

For more info: https://github.com/mrJean1/PyGeodesy/issues/31

### Mac OS

- inside pygeodesy patched repo: `pip3.6 install .`
- inside PySoar folder: `pip3.6 install -r requirements.txt` 
- `PYGEODESY_PATH=$(python3.6 -c "import pygeodesy; print(pygeodesy.__path__[0])")`
- `pyinstaller --windowed --paths=$PYGEODESY_PATH main_pysoar.py`

### Windows
- inside pygeodesy patched repo: `pip install .`
- inside PySoar folder: `pip install -r requirements.txt`
- `python3.6 -c "import pygeodesy; print(pygeodesy.__path__[0])"`
- `pyinstaller --windowed --onefile --paths=[INSERT_RESULT_PREVIOUS_LINE_HERE] main_pysoar.py`

## License

	PySoar - Automating gliding competition analysis	Copyright (C) 2016  Matthijs Beekman

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>


You can find the full license text in the [LICENSE](LICENSE) file.
