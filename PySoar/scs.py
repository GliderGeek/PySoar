import os
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
from settingsClass import Settings
from daily_results_page import DailyResultsPage

settings = Settings()

class StreplaDaily(DailyResultsPage):

    def __init__(self, url):
        DailyResultsPage.__init__(self, url)

        self.baseUrl = "http://www.strepla.de/scs/Public/"
        
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

        # get competition, class and date
        self.competition = soup.find('div', id="public_contest_info").find('span',id="ctl00_lblCompName").text
        self.plane_class=soup.find('div', { "class" : "h3a" }).find('span',id="ctl00_Content_lblCompClass").text
        self.date=soup.find('div', { "class" : "h3a" }).find('span',id="ctl00_Content_lblDate").text[0:10]    

        # Get file URLs, rankings and file names
        table = soup.find("table")
        num_comp=len(table.findAll('tr'))
        for i in range(num_comp-1):
            comp=table.findAll('tr')[i+1]
            if ((comp.findAll('span')[0].text) != 'dnf'):
                self.rankings.append(int(comp.findAll('span')[0].text))
                self.file_urls.append(self.baseUrl + comp.findAll('a')[0].get('href'))
                self.file_names.append((comp.findAll('span')[1].text) + '.igc')
                self.plane.append((comp.findAll('span')[3].text))
            

        print "Analyzing %s, %s %s" % (self.competition, self.plane_class, self.date)   
