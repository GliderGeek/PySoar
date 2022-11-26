import subprocess
import os
import sys
import json
import requests

import wx

from analysis import AnalysisThread
from settingsClass import Settings

settings = Settings()


DOWNLOAD_EVENT_ID = wx.NewId()
ANALYSIS_EVENT_ID = wx.NewId()
FINISH_EVENT_ID = wx.NewId()


def url_format_correct(url_string):

    if 'soaringspot.com' in url_string:
        daily_results = _is_daily_soaringspot_url(url_string)
    elif 'strepla.de' in url_string:
        daily_results = _is_daily_strepla_url(url_string)
    else:
        return False, 'Wrong URL: Use SoaringSpot or Strepla URL'

    if not daily_results:
        return False, 'Wrong URL: no daily results'
    else:
        return True, 'URL correct'


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

        # Set up event handlers for any worker thread results
        self.Connect(-1, -1, DOWNLOAD_EVENT_ID, self.on_download_event)
        self.Connect(-1, -1, ANALYSIS_EVENT_ID, self.on_analysis_event)
        self.Connect(-1, -1, FINISH_EVENT_ID, self.on_finish_event)

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

    def on_download_event(self, event):
        event_data = event.data
        print(event_data)
        self.download_status.SetLabel(event_data)

    def on_analysis_event(self, event):
        event_data = event.data
        print(event_data)
        self.analyse_status.SetLabel(event_data)

    def on_finish_event(self, event):
        (success, message) = event.data
        print('finish event:', success)
        if success:
            self.status.SetLabel('Success')
            self.open_spreadsheet.Enable()
            self.start_analysis.Enable()
        else:
            self.status.SetLabel(message)
            self.start_analysis.Enable()

    def on_press(self, event):
        self.open_spreadsheet.Disable()
        self.start_analysis.Disable()
        self.download_status.SetLabel('')
        self.analyse_status.SetLabel('')

        url = self.url_input.GetValue()

        url_correct, failure_reason = url_format_correct(url)
        if url_correct:
            source = get_url_source(url)
            analysis = AnalysisThread(self, DOWNLOAD_EVENT_ID, ANALYSIS_EVENT_ID, FINISH_EVENT_ID, url, source)
            analysis.start()
        else:
            self.status.SetLabel(failure_reason)


def get_latest_version():
    github_user = "GliderGeek"
    github_repo = "PySoar"
    url_latest_version = f"https://api.github.com/repos/{github_user}/{github_repo}/releases"

    r = requests.get(url_latest_version)
    releases = json.loads(r.text)

    # get latest using sorting
    # latest seems to not be serialized in response
    for release in releases:
        if release['draft'] or release['prerelease']:
            continue  # skip drafts and prereleases
        else:
            latest_version = release['tag_name']
            break

    return latest_version


def start_gui(current_version, latest_version):
    app = wx.App()
    MyFrame(current_version, latest_version)
    app.MainLoop()


if __name__ == '__main__':

    current_version = settings.version
    try:
        latest_version = get_latest_version()
    except Exception:
        latest_version = ''

    if len(sys.argv) == 1:
        start_gui(current_version, latest_version)
    else:
        print('not implemented')  # TODO

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
