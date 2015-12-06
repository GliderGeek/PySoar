import easygui
from generalFunctions import correct_format, hhmmss2ss, determine_distance, print_array_debug, ss2hhmmss
from settingsClass import Settings

settings = Settings()

class CompetitionDay(object):

    def __init__(self):
        self.flights = []
        self.file_paths = []

        self.task_rules = []
        self.tp_line = []
        self.tp_radius = []

        self.task = []
        self.task_dists = []
        self.tp_names = []

        self.task_date = ""

        self.no_tps = 0
        self.no_legs = 0

        self.aat = False
        self.task_found = False
        self.start_opening = 0

    def ask_start_opening(self):
        # old implementation with easygui asking for opening time. seems to crash. maybe collapse with other easygui?
        ############################################################
        # no_input = True
        # while no_input:
        #     st_time_string = easygui.enterbox(
        #         msg='Start gate opening not found in igc files. Enter startime local time (hh:mm:ss): ',
        #         title=' ',
        #         default='',
        #         strip=True)
        #     if correct_format(st_time_string):
        #         print "you entered ", st_time_string, '. Programm is running...'
        #         no_input = False
        #         self.start_opening = hhmmss2ss(st_time_string, 0)
        ############################################################
        # new default at 09:00:00
        self.start_opening = hhmmss2ss("09:00:00", 0)

    def obtain_task_info(self):

        self.no_tps = int(self.task[0][-4::])
        self.no_legs = self.no_tps + 1

        for turnpoint in self.task_rules:
            if 'Line=1' in turnpoint.split(',') or 'Line=1\r\n' in turnpoint.split(','):
                self.tp_line.append(True)
            else:
                self.tp_line.append(False)
            for item in turnpoint.split(','):
                if item.startswith('R1'):
                    self.tp_radius.append(int(item[3:-1]))

        for tp in range(len(self.task)):
            if 1 < tp <= self.no_tps + 2:
                distance = determine_distance(self.task[tp], self.task[tp+1], 'tsk', 'tsk')
                self.task_dists.append(distance)
            if 1 < tp <= self.no_tps + 3:
                name = self.task[tp][23::]
                self.tp_names.append(name)

        date_raw = self.task[0][6:12]
        self.task_date = date_raw[0:2] + "-" + date_raw[2:4] + "-" + date_raw[4::]

    def save(self):
        file_name = settings.current_dir + "/debug_logs/competitionDayDebug.txt"
        text_file = open(file_name, "w")

        print_array_debug(text_file, "task_rules", self.task_rules)
        print_array_debug(text_file, "tp_line", self.tp_line)
        print_array_debug(text_file, "tp_radius", self.tp_radius)
        print_array_debug(text_file, "task", self.task)
        print_array_debug(text_file, "task_dists", self.task_dists)
        print_array_debug(text_file, "tp_names", self.tp_names)

        text_file.write("task_date: " + self.task_date + "\n\n")

        text_file.write("no_tps: " + str(self.no_tps) + "\n")
        text_file.write("no_legs: " + str(self.no_legs) + "\n\n")

        text_file.write("aat: " + str(self.aat) + "\n")
        text_file.write("task_found: " + str(self.task_found) + "\n")
        text_file.write("start_opening: " + ss2hhmmss(self.start_opening) + "\n\n")

        text_file.close()

if __name__ == '__main__':
    from main_pysoar import run
    run()
