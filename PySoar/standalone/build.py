import sys
import os
import platform
import shutil
sys.path.append('../')
from settingsClass import Settings
from Tkinter import Label, Tk, Button, Entry, W, E
import subprocess

settings = Settings()
version = settings.version
correct_version2 = "jadie"

root = Tk()

def correct_version():
	print 'Build process continues with version %s' % version
	
	if platform.system() == 'Darwin':
		subprocess.call(["pyinstaller", "--onefile", "--windowed", "../main_pysoar.py"])
		directory = 'mac'
		if not os.path.exists(directory):
			os.makedirs(directory)
		else:
			if os.path.exists('mac/PySoar_Mac.app'):
				shutil.rmtree('mac/PySoar_Mac.app')
				
		shutil.move("dist/main_pysoar.app", "mac/PySoar_mac.app")
		
	elif platform.system() == 'Windows':
		subprocess.call(["pyinstaller", "-F", "--noconsole", "../main_pysoar.py"])
		directory = 'windows64'
		if not os.path.exists(directory):
			os.makedirs(directory)
		else:
			if os.path.exists('windows64/PySoar_windows64.exe'):
				os.remove('windows64/PySoar_windows64.exe')
		shutil.move("dist\main_pysoar.exe", "windows64\PySoar_windows64.exe")
		
	elif platform.system() == "Linux":
		subprocess.call(["pyinstaller", "-F", "../main_pysoar.py"])
		directory = 'linux'
		if not os.path.exists(directory):
			os.makedirs(directory)
		else:
			if os.path.exists('linux/PySoar_linux'):
				os.remove('linux/PySoar_linux')
		shutil.move("dist/main_pysoar", "linux/PySoar_linux")
		
	shutil.rmtree('build')
	shutil.rmtree('dist')
	os.remove("main_pysoar.spec")	
	
	root.quit()
	    
def incorrect_version():
	print 'Build process is cancelled because of incorrect version number'
	root.quit()

version_title = Label(root, text='PySoar %s' %version, font=("Helvetica", 30))
question = Label(root, text="Is this the correct version number?", font=("Helvetica", 12))
stop = Button(root, command=incorrect_version, text='no')
go_on = Button(root, command=correct_version, text='yes')

version_title.grid(row=0, column=0, columnspan=2)
question.grid(row=1, column=0, columnspan=2)
stop.grid(row=2, column=0, sticky=E)
go_on.grid(row=2, column=1, sticky=W)

root.mainloop()
