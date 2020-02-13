import subprocess
import os
import sys
import json
import requests
from threading import Thread

import wx

from analysis import run
from settingsClass import Settings

settings = Settings()


def url_format_correct(url_string, status_handle):

    if 'soaringspot.com' in url_string:
        daily_results = _is_daily_soaringspot_url(url_string)
    elif 'strepla.de' in url_string:
        daily_results = _is_daily_strepla_url(url_string)
    else:
        status_handle('Wrong URL: Use SoaringSpot or Strepla URL')
        return False

    if not daily_results:
        status_handle('Wrong URL: no daily results')
        return False
    else:
        status_handle('URL correct')
        return True


def _is_daily_strepla_url(strepla_url):
    """e.g. https://www.strepla.de/scs/public/scoreDay.aspx?cID=472&className=Std&dateScoring=20180427"""
    score_day = strepla_url.split('/')[5]
    return score_day.startswith('scoreDay')


def _is_daily_soaringspot_url(soaringspot_url):
    """e.g. https://www.soaringspot.com/en/sallandse-tweedaagse-2014/results/club/task-1-on-2014-06-21/daily"""
    results = soaringspot_url.split('/')[-1]
    return results == 'daily'


def get_url_source(url):
    if 'soaringspot.com' in url:
        return 'cuc'
    elif 'strepla.de' in url:
        return 'scs'
    else:
        raise ValueError('Unknown source')


class MyFrame(wx.Frame):
    def __init__(self, current_version, latest_version):
        super().__init__(parent=None, title='PySoar: %s' % current_version)
        panel = wx.Panel(self)

        complete_sizer = wx.BoxSizer(wx.VERTICAL)

        if latest_version and latest_version.lstrip('v') != current_version:
            version_status = wx.StaticText(panel, label="Latest version: %s" % latest_version)
            version_status.SetForegroundColour((255, 0, 0))
            complete_sizer.Add(version_status, 0, wx.CENTER)

        my_sizer = wx.BoxSizer(wx.VERTICAL)

        text = wx.StaticText(panel, label="Fill in URL:")
        my_sizer.Add(text, 0, wx.ALL, 5)
        self.url_input = wx.TextCtrl(panel)
        my_sizer.Add(self.url_input, 0, wx.ALL | wx.EXPAND, 5)

        self.status = wx.StaticText(panel, label="")
        my_sizer.Add(self.status)

        self.download_status = wx.StaticText(panel, label="")
        my_sizer.Add(self.download_status)

        self.analyse_status = wx.StaticText(panel, label="")
        my_sizer.Add(self.analyse_status)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.start_analysis = wx.Button(panel, label='Start analysis')
        self.start_analysis.Bind(wx.EVT_BUTTON, self.on_press)
        buttons_sizer.Add(self.start_analysis, 0, wx.EXPAND)

        self.open_spreadsheet = wx.Button(panel, label="Open")
        self.open_spreadsheet.Disable()
        self.open_spreadsheet.Bind(wx.EVT_BUTTON, self.open_analysis_file)
        buttons_sizer.Add(self.open_spreadsheet)

        bug_report = wx.Button(panel, label='Report problem')
        bug_report.Bind(wx.EVT_BUTTON, self.go_bugform)
        buttons_sizer.Add(bug_report)

        complete_sizer.Add(my_sizer, 0, wx.ALL | wx.EXPAND, 5)
        complete_sizer.Add(buttons_sizer, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(complete_sizer)
        self.Show()

    def go_bugform(self, event):
        import webbrowser

        form_url = settings.debug_form_url
        versionID = settings.pysoar_version_formID
        urlID = settings.competition_url_formID
        pysoar_version = settings.version

        comp_url = self.url_input.GetValue()

        complete_url = '%s?entry.%s=%s&entry.%s=%s' % (form_url, versionID, pysoar_version, urlID, comp_url)
        webbrowser.open(complete_url)

    def open_analysis_file(self, event):
        if sys.platform.startswith("darwin"):
            subprocess.call(["open", settings.file_name])
        elif sys.platform.startswith('linux'):
            subprocess.call(["xdg-open", settings.file_name])
        elif sys.platform.startswith('win32'):
            os.startfile(settings.file_name)

    def set_download_status(self, new, total=None):
        if total is not None:
            download_str = 'Downloaded: %s/%s' % (new, total)
        else:
            download_str = 'Downloaded: %s' % new
        print(download_str)
        self.download_status.SetLabel(download_str)

    def set_analyse_status(self, new, total=None):
        if total is not None:
            analysis_str = 'Analyzed: %s/%s' % (new, total)
        else:
            analysis_str = 'Analyzed: %s' % new
        print(analysis_str)
        self.analyse_status.SetLabel(analysis_str)

    def update_status(self, message):
        self.status.SetLabel(message)
        wx.Yield()

    def after_successful_run(self):
        self.update_status("Analysis is complete.")
        self.open_spreadsheet.Enable()
        self.start_analysis.Enable()

    def after_unsuccessful_run(self, msg):
        self.update_status(msg)
        self.start_analysis.Enable()

    def on_press(self, event):
        self.open_spreadsheet.Disable()
        self.start_analysis.Disable()
        self.download_status.SetLabel('')
        self.analyse_status.SetLabel('')

        url = self.url_input.GetValue()
        if url_format_correct(url, self.update_status):
            args = (url, get_url_source(url), self.set_download_status, self.set_analyse_status,
                    self.after_successful_run, self.after_unsuccessful_run)
            x = Thread(target=run, args=args)
            x.start()


def get_latest_version():
    github_user = "GliderGeek"
    github_repo = "PySoar"
    url_latest_version = "https://api.github.com/repos/%s/%s/releases" % (github_user, github_repo)

    r = requests.get(url_latest_version)
    parsed_json = json.loads(r.text)

    latest_version = parsed_json[0]['tag_name']
    return latest_version


def start_gui(current_version, latest_version):
    app = wx.App()
    MyFrame(current_version, latest_version)
    app.MainLoop()


def run_commandline_program(sys_argv, current_version, latest_version):

    def print_help():
        print('There are two options for running PySoar from the commandline:\n'
              '1. `python main_python` for GUI\n'
              '2. `python main_pysoar [url]` - where [url] is the daily competition url')

    def status_handle(message):
        print(message)

    def download_handle(new, total=None):
        if total is not None:
            analysis_str = 'Downloaded: %s/%s' % (new, total)
        else:
            analysis_str = 'Downloaded: %s' % new
        print(analysis_str)

    def on_success():
        print('Analysis complete')

    def on_failure(msg):
        print('Error: %s' % msg)

    def analysis_handle(new, total=None):
        if total is not None:
            analysis_str = 'Analyzed: %s/%s' % (new, total)
        else:
            analysis_str = 'Analyzed: %s' % new
        print(analysis_str)

    if latest_version and latest_version.lstrip('v') != current_version:
        print('Latest version is %s! Current: %s' % (latest_version, current_version))

    if len(sys_argv) == 2:
        if sys_argv[1] == '--help':
            print_help()
        else:
            url = sys_argv[1]
            if url_format_correct(url, status_handle):
                source = get_url_source(url)
                run(url,
                    source,
                    download_progress=download_handle,
                    analysis_progress=analysis_handle,
                    on_success=on_success,
                    on_failure=on_failure)
    else:
        print_help()


if __name__ == '__main__':

    current_version = settings.version
    try:
        latest_version = get_latest_version()
    except Exception:
        latest_version = ''

    if len(sys.argv) == 1:
        start_gui(current_version, latest_version)
    else:
        run_commandline_program(sys.argv, current_version, latest_version)

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
