from Tkinter import Label, Tk, Button, Entry, W, E
from generalFunctions import open_analysis_file, url_format_correct, go_bugform
from analysis import run
from functools import partial
from settingsClass import Settings
import sys

settings = Settings()


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

        run(url_entry.get(), url_status, download_progress, analysis_progress)

        analysis_done = Button(root, text='Excel produced', command=open_analysis_file)
        analysis_done.grid(row=6, column=0, pady=5)
        print "Analysis complete, excel produced"

    title = Label(root, text=' PySoar', font=("Helvetica", 30))
    url_accompanying_text = Label(root, text='Give Soaringspot/scoringStrepla URL:')
    url_entry = Entry(root, width=60)
    url_confirmation = Button(root, text='ok')
    url_confirmation.bind('<Button-1>', url_check)
    url_status = Label(root, text='', foreground='red')
    download_progress = Label(root, text='Downloaded: ')
    analysis_progress = Label(root, text='Analyzed: ')
    report_problem = Button(root, text='Report problem')
    report_problem.bind('<Button-1>', partial(go_bugform, url_entry))
    root.bind('<Return>', url_check)
    version = Label(root, text='v %s' % settings.version)

    title.grid(row=0, column=0)
    url_accompanying_text.grid(row=1, column=0, sticky=W)
    url_entry.grid(row=2, column=0)
    url_confirmation.grid(row=2, column=1)
    url_status.grid(row=3, column=0)
    download_progress.grid(row=4, column=0, pady=5)
    analysis_progress.grid(row=5, column=0, pady=5)
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
        run(sys.argv[1])
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
