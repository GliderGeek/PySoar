import os
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
from settingsClass import Settings
from daily_results_page import DailyResultsPage

settings = Settings()


class SoaringSpotDaily(DailyResultsPage):

    def __init__(self, url):
        DailyResultsPage.__init__(self, url)

        self.baseUrl = "http://www.soaringspot.com"

        self.competition, self.plane_class, self.date = self._get_competition_info(self.url)

        self.load_website()
        self.set_igc_directory(os.path.join(settings.current_dir, 'bin'), self.competition, self.plane_class, self.date)

    def load_website(self):

        # Get entire html site
        mech = Browser()
        mech.set_handle_robots(False)

        page = mech.open(self.url)
        html = page.read()
        soup = BeautifulSoup(html)
        table = soup.find("table")

        # Get file URLs, rankings and file names
        for row in table.findAll('tr')[1:]:
            if row.findAll('td')[0].text not in ["DNS", "DNF", "HC"]:
                self.rankings.append(int(row.findAll('td')[0].text[0:-1]))
                for link in row.findAll('a'):
                    if link.get('href').startswith("http://"):
                        self.file_urls.append(link.get('href'))
                    elif link.get('href').split('/')[2] == "download-contest-flight":
                        self.file_urls.append(self.baseUrl + link.get('href'))
                    self.file_names.append(link.text + '.igc')

        print "Analyzing %s, %s %s" % (self.competition, self.plane_class, self.date)

    @staticmethod
    def _get_competition_info(url):

        print(url)

        if url.startswith('https://') or url.startswith('http://'):
            _, _, _, _, competition, _, plane_class, date_description, _ = url.split('/')
        else:
            _, _, competition, _, plane_class, date_description, _ = url.split('/')

        date_us = date_description[-10::]
        date = date_us[-2::] + '-' + date_us[5:7] + '-' + date_us[0:4]

        return competition, plane_class, date
