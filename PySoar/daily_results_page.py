import os
import urllib
import urllib2

import time
from BeautifulSoup import BeautifulSoup


class DailyResultsPage:

    def __init__(self, url):

        if url.startswith('http://') or url.startswith('https://'):
            self.url = url
        else:
            self.url = 'http://%s' % url

        # set by set_igc_directory method
        self.igc_directory = None

        # to be filled by load_website method in sub-class
        self.rankings = list()
        self.file_urls = list()
        self.file_names = list()
        self.competition = None
        self.plane_class = None
        self.date = None

        # needed for scoringStrepla as no information of airplane type is available in the IGC files
        self.planes = list()

    def set_igc_directory(self, start_dir, competition_name, plane_class, date):
        self.igc_directory = os.path.join(start_dir, competition_name, plane_class, date)

        # make directory
        if not os.path.exists(self.igc_directory):
            os.makedirs(self.igc_directory) 

    def _get_html_soup(self):
        # fix problem with SSL certificates
        # https://stackoverflow.com/questions/30551400/disable-ssl-certificate-validation-in-mechanize#35960702
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

        # get entire html of page
        html = urllib2.urlopen(self.url).read()

        return BeautifulSoup(html)

    def download_flights(self, download_progress):
        flights_downloaded = 0

        for file_url, file_name in zip(self.file_urls, self.file_names):

            file_path = os.path.join(self.igc_directory, file_name)
            while not os.path.exists(file_path):
                urllib.URLopener().retrieve(file_url, file_path)
                time.sleep(0.1)

            flights_downloaded += 1

            if download_progress is not None:
                download_progress.configure(text='Downloaded: %s/%s' % (flights_downloaded, len(self.file_names)))
                download_progress.update()
