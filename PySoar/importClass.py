import os
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
import urllib
from settingsClass import Settings

settings = Settings()


class SoaringSpotImport(object):

    def __init__(self):
        # combine parameters in dictionary?
        self.url_page = ""
        self.competition = ""
        self.plane_class = ""
        self.date = ""
        self.igc_directory = ""

        self.flights_downloaded = 0
        self.flights_analyzed = 0

        self.competition_day_exists = False

        self.baseUrl = "http://www.soaringspot.com"
        self.file_urls = []
        self.file_names = []
        self.rankings = []

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
        self.competition_day_exists = os.path.exists(self.igc_directory)

        if not os.path.exists(settings.current_dir + '/debug_logs'):
            os.makedirs(settings.current_dir + '/debug_logs')

    def save(self, settings):
        file_name = settings.current_dir + "/debug_logs/importClassDebug.txt"
        text_file = open(file_name, "w")

        text_file.write("rankings\t file_names\t file_urls\t \n")
        for ii in range(len(self.file_urls)):
            text_file.write(str(self.rankings[ii])+'\t')
            text_file.write(str(self.file_names[ii]) + '\t')
            text_file.write(str(self.file_urls[ii]) + '\n')

        text_file.close()

if __name__ == '__main__':
    from main_pysoar import run
    run()
