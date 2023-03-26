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

## Building an executable
Executables are built using github actions. See `.github/workflows/main.yml` for the steps taken

## Publishing a new version
- everything merged in development
- add version number in `CHANGES.md` and change version number in `settingsClass.py`
- commit on developent, merge development in master and tag on master
- download zips from pipeline and create release from the tag

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
