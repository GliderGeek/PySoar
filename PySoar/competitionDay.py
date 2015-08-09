import easygui
from generalFunctions import correct_format, hhmmss2ss


class CompetitionDay(object):

    def __init__(self):
        self.flights = {}
        self.file_paths = {}
        self.task = []
        self.task_rules = []

    def ask_start_opening(self):
        no_input = True
        while no_input:
            st_time_string=easygui.enterbox(
                msg='Start gate opening not found in igc files. Enter startime (hh:mm:ss): ',
                title=' ',
                default='',
                strip=True)
            if correct_format(st_time_string):
                print "you entered ", st_time_string,'. Programm is running...'
                no_input = False
                self.start_opening = hhmmss2ss(st_time_string, self.utc_to_local)

    def obtain_task_info(self):

        self.no_tps=int(self.task[0][22:24])
        self.tp_line=[]
        self.tp_radius=[]

        for turnpoint in self.task_rules:
            self.tp_line.append(True) if 'Line=1' in turnpoint.split(',') else  self.tp_line.append(False)
            for item in turnpoint.split(','):
                if item.startswith('R1'):
                    self.tp_radius.append(int(item[3:-1]))


if __name__ == '__main__':
    from main import run
    run()
