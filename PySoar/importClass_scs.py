import os
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
import urllib
from settingsClass import Settings
import time


settings = Settings()

class ScoringStreplaImport(object):

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

        self.set_source(url)

        if (self.strepla):
            self.load_scs(url)
        else:
            self.load(url)
            
        self.download_flights(download_progress)

    def set_source(self,url):
        if ( 'strepla' in url):
            self.strepla = True
            self.baseUrl = "http://www.strepla.de/scs/Public/"
            self.plane = []
    
    def download_flights(self, download_progress):

        for index in range(len(self.file_urls)):
            while not os.path.exists(self.igc_directory + "/" + self.file_names[index]):
                self.download_flight(index)
                if (self.strepla):
                    self.convert_task_scs(index)
                time.sleep(0.1)
                self.flights_downloaded += 1
            time.sleep(0.1)
            self.flights_downloaded += 1
            if download_progress is not None:
                download_progress.configure(text='Downloaded: %s/%s' % (self.flights_downloaded, len(self.file_names)))
                download_progress.update()

    def download_flight(self, index):
        url_location = self.file_urls[index]
        save_location = self.igc_directory + self.file_names[index]
        urllib.URLopener().retrieve(url_location, save_location)        
        
    def convert_task_scs(self,index):
        save_location = self.igc_directory + self.file_names[index]

        #open file
        f = open(save_location, "U") 
        full_file = f.readlines()
        f.close()

        tp_in=[]
        tp_seeyou=[]
        tp_sector=[]
        aat_sector_radius=[]
        aat_sector_angle=[]
        aat_time=[]
        start_time=[]
        base="LCU::C0000000N00000000E"
        
        # Get all task points and further task information
        for line in full_file:
            if line.startswith('LSCSDCID'):
                tp_seeyou.append("LCU::HPCIDCOMPETITIONID:"+str((line.split(':')[1]))[0:-1])
            if line.startswith('LSCSDName'):
                name=((line.split(':')[1])[0:-1]).split(',')
                tp_seeyou.append("LCU::HPPLTPILOT:"+name[1]+" "+name[0])
            if line.startswith('LSCSC'):
                tp_in.append(line)
            if line.startswith('LSCSRSLINE'):
                sl_width=str((int((line.split(':'))[1]))/2)
            if line.startswith('LSCSRFCYLINDER'):
                fc_radius=str((int((line.split(':'))[1])))
            if line.startswith('LSCSA0'):
                aat_sector_radius.append((line.split(':'))[1])
                if int(((line.split(':'))[3])[0:-1]) == 0:
                    aat_sector_angle.append(360)
                else:
                    aat_sector_angle.append( ((line.split(':'))[3])[0:-1] )  
            if line.startswith('LSCSDTime window'):
                aat_time.append((line.split(':'))[1]+":"+((line.split(':'))[2])[0:-1]+":00")
            if line.startswith('LSCSDGate open'):
                start_time.append((line.split(':'))[1]+":"+((line.split(':'))[2])[0:-1]+":00")

        # Check if task is AAT        
        aat=False
        if (len(aat_sector_radius)) > 1:
            aat=True

        # Write points into SeeYou readable format        
        i=-1
        for point in tp_in:
            if i == -1:
                tp_seeyou.append('LCU::HPGTYGLIDERTYPE:'+self.plane[index])
                tp_seeyou.append('LCU::HPTZNTIMEZONE:2')
                tp_seeyou.append('LCU::C'+time.strftime("%d%m%y%H%M%S")+'000000000000')
                tp_seeyou.append(base)
                tp_sector.append("LSEEYOU OZ=-1,Style=2,R1="+sl_width+"m,A1=180,Line=1")
            if i > -1 and i != (len(tp_in)-2):
                if aat:
                    tp_sector.append("LSEEYOU OZ="+str(i)+",Style=1,R1="+aat_sector_radius[i]+"m,A1="+str(int(aat_sector_angle[i])/2))    
                else:
                    tp_sector.append("LSEEYOU OZ="+str(i)+",Style=1,R1=10000m,A1=45,R2=500m,A2=180")
            elif  i == (len(tp_in)-2):
                tp_sector.append("LSEEYOU OZ="+str(i)+",Style=3,R1="+fc_radius+"m,A1=180,Reduce=1")       
            tp_split  = point.split(':')
            tp_seeyou.append("LCU::C"+ ((tp_split[2])[1:] + (tp_split[2])[0]) + (((tp_split[3])[1:-1])+(tp_split[3])[0]) +tp_split[1] )
            i=i+1

        # append sector definitions
        tp_seeyou.append(base)
        tp_seeyou.extend(tp_sector)

        # add task information
        if aat:
            tp_seeyou.append('LSEEYOU TSK,NoStart='+start_time[0]+',TaskTime='+aat_time[0]+',WpDis=False')
        else:
            tp_seeyou.append('LSEEYOU TSK,NoStart='+start_time[0])

        f = open(save_location,'a') 
        for item in tp_seeyou:
            f.write("%s\n" % item)
        f.close()    
        
    def load_scs(self, url_input):

        self.url_page = url_input
        print(self.url_page)

        # Get entire html site
        mech = Browser()
        mech.set_handle_robots(False)
        page = mech.open(self.url_page)
        html = page.read()
        soup = BeautifulSoup(html)

        # get competition, class and date
        self.competition = soup.find('div', id="public_contest_info").find('span',id="ctl00_lblCompName").text
        self.plane_class=soup.find('div', { "class" : "h3a" }).find('span',id="ctl00_Content_lblCompClass").text
        self.date=soup.find('div', { "class" : "h3a" }).find('span',id="ctl00_Content_lblDate").text[0:10]        

        # Get file URLs, rankings and file names
        table = soup.find("table")
        num_comp=len(table.findAll('tr'))
        for i in range(num_comp-1):
            comp=table.findAll('tr')[i+1]
            self.rankings.append(int(comp.findAll('span')[0].text))
            self.file_urls.append(self.baseUrl + comp.findAll('a')[0].get('href'))
            self.file_names.append((comp.findAll('span')[1].text) + '.igc')
            self.plane.append((comp.findAll('span')[3].text))


        base_path="/home/jan/Schreibtisch/PySoar/test_download/"    
        self.igc_directory = base_path +  self.competition + '/' + self.plane_class + '/' + self.date + '/'

        if not os.path.exists(self.igc_directory):
            os.makedirs(self.igc_directory)
        
        #print(self.file_urls.append)    
        print "Analyzing " + self.competition + ", " + self.plane_class + " class " + self.date


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
