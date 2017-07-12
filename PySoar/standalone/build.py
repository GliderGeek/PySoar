import sys
import os
import platform
import shutil

sys.path.append('../')
from settingsClass import Settings
from Tkinter import Label, Tk, Button, Entry, W, E
import subprocess
from contextlib import contextmanager

settings = Settings()
version = settings.version

manual_location = os.path.join("..", "..", "docs", "manual", "EN")
tex_filename = "PySoar-manual.tex"
pdf_filename = "PySoar-manual.pdf"
main_file = "main_pysoar"

root = Tk()


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def correct_version():
    print 'Build process continues with version %s' % version

    # # create pdf of manual
    # with cd(manual_location):
    #     subprocess.call(["pdflatex", tex_filename])

    if platform.system() == 'Darwin':
        platform_name = "mac"
        source_executable = main_file
        executable = "PySoar_mac.app"

        subprocess.call(["pyinstaller", "--onefile", "--windowed", os.path.join("..", main_file + ".py")])

    elif platform.system() == 'Windows':
        platform_name = "windows"
        source_executable = main_file + ".exe"
        executable = "PySoar_windows.exe"

        subprocess.call(["pyinstaller", "-F", "--noconsole", os.path.join("..", main_file + ".py")])

    elif platform.system() == "Linux":
        platform_name = 'linux'
        source_executable = main_file
        executable = "PySoar_linux"

        subprocess.call(["pyinstaller", "-F", os.path.join("..", main_file + ".py")])

    # create platform folder. if already exists, remove executable
    if not os.path.exists(platform_name):
        os.makedirs(platform_name)
    else:
        if platform.system() == "Darwin":
            if os.path.exists(os.path.join(platform_name, executable + ".app")):
                shutil.rmtree(os.path.join(platform_name, executable + ".app"))
        else:
            if os.path.exists(os.path.join(platform_name, executable)):
                os.remove(os.path.join(platform_name, executable))

    foldername = "%s_v%s" % (platform_name, version)
    os.makedirs(foldername)

    # delete zip file if it exists
    if os.path.exists("%s.zip" % foldername):
        os.remove("%s.zip" % foldername)

    # copy executable to zip folder and platform_folder
    if platform.system() == 'Darwin':
        shutil.copytree(os.path.join("dist", source_executable + ".app"), os.path.join(foldername, executable))
        shutil.move(os.path.join("dist", source_executable + ".app"), os.path.join(platform_name, executable))
    else:  # linux and windows
        shutil.copy(os.path.join("dist", source_executable), os.path.join(foldername, executable))
        shutil.move(os.path.join("dist", source_executable), os.path.join(platform_name, executable))

    # move pdf to zip folder and create zip file
    # shutil.move(os.path.join(manual_location, pdf_filename), os.path.join(foldername, pdf_filename))
    shutil.make_archive(foldername, "zip", foldername)

    # remove unnecessary folders and files
    shutil.rmtree(foldername)
    shutil.rmtree('build')
    shutil.rmtree('dist')
    os.remove("main_pysoar.spec")

    root.quit()


def incorrect_version():
    print 'Build process is cancelled because of incorrect version number'
    root.quit()


version_title = Label(root, text='PySoar %s' % version, font=("Helvetica", 30))
question = Label(root, text="Is this the correct version number?", font=("Helvetica", 12))
stop = Button(root, command=incorrect_version, text='no')
go_on = Button(root, command=correct_version, text='yes')

version_title.grid(row=0, column=0, columnspan=2)
question.grid(row=1, column=0, columnspan=2)
stop.grid(row=2, column=0, sticky=E)
go_on.grid(row=2, column=1, sticky=W)

root.mainloop()

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
