from tkinter import Label, Tk, Button, Entry, W, E

import subprocess

import os

from PySoar.analysis import run
from functools import partial
from PySoar.settingsClass import Settings
import sys

settings = Settings()


def url_format_correct(url_string):
    if 'soaringspot.com' not in url_string and 'strepla.de' not in url_string:
        return 'Use SoaringSpot or Strepla URL'
    elif url_string[-5::] != 'daily' and url_string[33:41] != 'scoreDay':
        return 'URL does not give daily results'
    else:
        return 'URL correct'


def go_bugform(url_entry, event):
    import webbrowser

    form_url = settings.debug_form_url
    versionID = settings.pysoar_version_formID
    urlID = settings.competition_url_formID
    pysoar_version = settings.version

    comp_url = url_entry.get()

    complete_url = '%s?entry.%s=%s&entry.%s=%s' % (form_url, versionID, pysoar_version, urlID, comp_url)
    webbrowser.open(complete_url)


def open_analysis_file():

    if sys.platform.startswith("darwin"):
        subprocess.call(["open", settings.file_name])
    elif sys.platform.startswith('linux'):
        subprocess.call(["xdg-open", settings.file_name])
    elif sys.platform.startswith('win32'):
        os.startfile(settings.file_name)


def get_url_source(url):
    if 'soaringspot.com' in url:
        return 'cuc'
    elif 'strepla.de' in url:
        return 'scs'
    else:
        raise ValueError('Unknown source')


def start_gui():

    root = Tk()
    root.resizable(0, 0)

    def url_check(event):
        checked_url = url_format_correct(url_entry.get())
        if checked_url == 'URL correct':
            url_status.configure(text=checked_url, foreground='green')
            url_status.update()
            start_analysis()
        else:
            url_status.configure(text=checked_url, foreground='red')
            url_status.update()

    def start_analysis():

        url = url_entry.get()
        source = get_url_source(url)
        run(url, source, url_status, download_progress_label, analysis_progress_label)

        analysis_done = Button(root, text='Excel produced', command=open_analysis_file)
        analysis_done.grid(row=6, column=0, pady=5)
        print("Analysis complete, excel produced")

    title = Label(root, text=' PySoar', font=("Helvetica", 30))
    url_accompanying_text = Label(root, text='Give Soaringspot/scoringStrepla URL:')
    url_entry = Entry(root, width=60)
    url_confirmation = Button(root, text='ok')
    url_confirmation.bind('<Button-1>', url_check)
    url_status = Label(root, text='', foreground='red')
    download_progress_label = Label(root, text='Downloaded: ')
    analysis_progress_label = Label(root, text='Analyzed: ')
    report_problem = Button(root, text='Report problem')
    report_problem.bind('<Button-1>', partial(go_bugform, url_entry))
    root.bind('<Return>', url_check)
    version = Label(root, text='v %s' % settings.version)

    title.grid(row=0, column=0)
    url_accompanying_text.grid(row=1, column=0, sticky=W)
    url_entry.grid(row=2, column=0)
    url_confirmation.grid(row=2, column=1)
    url_status.grid(row=3, column=0)
    download_progress_label.grid(row=4, column=0, pady=5)
    analysis_progress_label.grid(row=5, column=0, pady=5)
    report_problem.grid(row=7, column=0, sticky=W)
    version.grid(row=7, column=1, sticky=E)

    root.mainloop()


def print_help():
    print('There are two options for running PySoar from the commandline:\n'
          '1. `python main_python` for GUI\n'
          '2. `python main_pysoar [url]` - where [url] is the daily competition url')


if len(sys.argv) == 1:
    start_gui()
elif len(sys.argv) == 2:
    if sys.argv[1] == '--help':
        print_help()
    else:
        url = sys.argv[1]
        if url_format_correct(url) == 'URL correct':
            source = get_url_source(url)
            run(url, source)
else:
    print_help()

#############################  LICENSE  #####################################

#   PySoar - Automating gliding competition analysis
#   Copyright (C) 2016  Matthijs Beekman
# 
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
# 
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
