from generalFunctions import print_array_debug, ss2hhmmss, get_date
from settingsClass import Settings
from aat import AAT
from race_task import RaceTask
import copy
from flightClass import Flight

settings = Settings()


class CompetitionDay(object):

    def __init__(self):
        self.flights = []
        self.file_paths = []

        # following variables are from new task implementation for AAT
        self.task = None
        self.utc_diff = None
        self.date = None

    def read_flights(self, soaring_spot_info):
        for ii in range(len(soaring_spot_info.file_names)):
            file_name = soaring_spot_info.file_names[ii]
            ranking = soaring_spot_info.rankings[ii]
            self.file_paths.append(soaring_spot_info.igc_directory + file_name)
            self.flights.append(Flight(soaring_spot_info.igc_directory, file_name, ranking))
            self.flights[-1].read_igc(soaring_spot_info)

    def load_task_information(self):  # new task implementation for AAT

        # task part
        task_info = None
        for flight in self.flights:
            new_task_info = flight.get_task_information()

            if task_info is None:
                task_info = new_task_info
            else:

                # check whether task dates are the same, because this line is removed
                current_task_date = get_date(task_info['lcu_lines'][0])
                new_task_date = get_date(task_info['lcu_lines'][0])
                if new_task_date != current_task_date:
                    print 'different task date present in igc files'
                    # issue #65

                # temporarily take out first lcu_line (timestamped) for comparison
                temp_task_info = copy.deepcopy(task_info)
                temp_new_task_info = copy.deepcopy(new_task_info)
                del temp_task_info['lcu_lines'][0]
                del temp_new_task_info['lcu_lines'][0]

                if temp_task_info != temp_new_task_info:
                    print 'different task information present in igc files'
                    # issue #65

                    if len(task_info['lcu_lines']) == 0 and len(new_task_info['lcu_lines']) != 0:
                        task_info = new_task_info
                        print 'used new task info because old one did not have full task'  # uncertain if this happens

        if task_info['aat']:
            self.task = AAT(task_info)
        else:
            self.task = RaceTask(task_info)

        # utc difference and date
        self.date = task_info['date']
        self.utc_diff = task_info['utc_diff']

    def save(self):
        file_name = settings.current_dir + "/debug_logs/competitionDayDebug.txt"
        text_file = open(file_name, "w")

        print_array_debug(text_file, "task", self.task.taskpoints)
        print_array_debug(text_file, "task_dists", self.task.distances)

        text_file.write("task_date: " + self.date.strftime('%d-%m-%y') + "\n\n")

        text_file.write("no_tps: " + str(self.task.no_tps) + "\n")
        text_file.write("no_legs: " + str(self.task.no_legs) + "\n\n")

        text_file.write("aat: " + str(self.task.aat) + "\n")
        text_file.write("start_opening: " + ss2hhmmss(self.task.start_opening) + "\n\n")

        text_file.close()

if __name__ == '__main__':
    from main_pysoar import start_gui
    start_gui()

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
