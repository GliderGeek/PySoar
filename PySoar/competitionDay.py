import copy

from task import Task
from generalFunctions import get_date
from settingsClass import Settings
from race_task import RaceTask
from aat import AAT
from flightClass import Flight

settings = Settings()


class CompetitionDay(object):

    def __init__(self, soaring_spot_info, url_status):
        self.flights = []
        self.file_paths = []

        self.task = None
        self.utc_diff = None
        self.date = None
        self.analyzed = False

        self.read_flights(soaring_spot_info)
        self.load_task_information()

        # shortcoming of PySoar
        if self.task.multi_start:
            url_status.configure(text="Multiple starting points not implemented!", foreground='red')
            url_status.update()
            return

    def analyze_flights(self, soaring_spot_info, analysis_progress):
        flights_analyzed = 0
        for flight in self.flights:
            flight.analyze(self.task)

            flights_analyzed += 1
            if analysis_progress is not None:
                analysis_progress.configure(text='Analyzed: %s/%s' %
                                                 (str(flights_analyzed), str(len(soaring_spot_info.file_names))))
                analysis_progress.update()

        self.analyzed = True

    def read_flights(self, soaring_spot_info):
        for ii in range(len(soaring_spot_info.file_names)):
            file_name = soaring_spot_info.file_names[ii]
            ranking = soaring_spot_info.rankings[ii]
            self.file_paths.append(soaring_spot_info.igc_directory + file_name)
            self.flights.append(Flight(soaring_spot_info.igc_directory, file_name, ranking))
            self.flights[-1].read_igc(soaring_spot_info.igc_directory)

    def load_task_information(self):

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

        lcu_lines = task_info['lcu_lines']
        lseeyou_lines = task_info['lseeyou_lines']
        multi_start = task_info['multi_start']
        start_opening = task_info['start_opening']
        utc_diff = task_info['utc_diff']
        taskpoints = Task.taskpoints_from_cuc(lcu_lines, lseeyou_lines)

        if task_info['aat']:
            t_min = task_info['t_min']
            self.task = AAT(taskpoints, multi_start, start_opening, utc_diff, t_min)
        else:
            self.task = RaceTask(taskpoints, multi_start, start_opening, utc_diff)

        # utc difference and date
        self.date = task_info['date']
        self.utc_diff = task_info['utc_diff']


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
