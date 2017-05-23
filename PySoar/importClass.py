import os
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
import urllib
from settingsClass import Settings
import time
from importClass_scs import set_source, load_scs, convert_task_scs

settings = Settings()


class SoaringSpotImport(object):

    def __init__(self, url, download_progress):
        self.url_page = ""
        self.competition = ""
        self.plane_class = ""
        self.date = ""
        self.igc_directory = ""

        self.flights_downloaded = 0

        self.baseUrl = "http://www.soaringspot.com"
        self.file_urls = []
        self.file_names = []
        self.rankings = []
        
        self.strepla = False
        set_source(self,url)

        if (self.strepla):
            load_scs(self,url)
        else:
            self.load(url)

        self.download_flights(download_progress)

    def download_flights(self, download_progress):
        for index in range(len(self.file_urls)):
            while not os.path.exists(self.igc_directory + "/" + self.file_names[index]):
                self.download_flight(index)
                if (self.strepla):
                    convert_task_scs(self,index)
                time.sleep(0.1)
            self.flights_downloaded += 1
            if download_progress is not None:
                download_progress.configure(text='Downloaded: %s/%s' % (self.flights_downloaded, len(self.file_names)))
                download_progress.update()

    def download_flight(self, index):
        url_location = self.file_urls[index]
        save_location = self.igc_directory + self.file_names[index]
        urllib.URLopener().retrieve(url_location, save_location)

    def load(self, url_input):

        self.url_page = url_input

        self.competition = self.url_page.split('/')[4]
        self.plane_class = self.url_page.split('/')[6]
        date_us = self.url_page.split('/')[7][-10::]
        self.date = date_us[-2::] + '-' + date_us[5:7] + '-' + date_us[0:4]

        # Get entire html site
        mech = Browser()
        mech.set_handle_robots(False)
        page = mech.open(self.url_page)
        html = page.read()
        soup = BeautifulSoup(html)
        table = soup.find("table")

        # Get file URLs, rankings and file names
        for row in table.findAll('tr')[1:]:
            if row.findAll('td')[0].text != "DNS" and\
               row.findAll('td')[0].text != "DNF" and\
                row.findAll('td')[0].text != "HC":
                self.rankings.append(int(row.findAll('td')[0].text[0:-1]))
                for link in row.findAll('a'):
                    if link.get('href').startswith("http://"):
                        self.file_urls.append(link.get('href'))
                    elif link.get('href').split('/')[2] == "download-contest-flight":
                        self.file_urls.append(self.baseUrl + link.get('href'))
                    self.file_names.append(link.text + '.igc')

        print "Analyzing " + self.competition + ", " + self.plane_class + " class " + self.date

        self.igc_directory = settings.current_dir + '/bin/' + self.competition + '/' + self.plane_class + '/' + self.date + '/'

        if not os.path.exists(self.igc_directory):
            os.makedirs(self.igc_directory)

        # if not os.path.exists(settings.current_dir + '/debug_logs'):
        #     os.makedirs(settings.current_dir + '/debug_logs')

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
