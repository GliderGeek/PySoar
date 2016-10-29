from generalFunctions import hhmmss2ss, get_date
from settingsClass import Settings
from phasesClass import FlightPhases
from performanceClass import Performance
from trip import Trip

settings = Settings()


class Flight(object):
    def __init__(self, folder_path, file_name, ranking):
        self.file_name = file_name
        self.folder_path = folder_path

        self.airplane = None
        self.competition_id = None
        self.ranking = ranking

        self.trace = []
        self.trace_settings = {
            'gps_altitude': True,
            'enl_indices': None
        }
        self.trip = None

        self.phases = None
        self.performance = None

    def analyze(self, competition_day):
        print self.file_name

        self.trip = Trip(competition_day.task, self.trace, self.trace_settings)

        if len(self.trip.fixes) >= 1:  # competitor must have started
            self.phases = FlightPhases(self.trip, self.trace, self.trace_settings)
            self.performance = Performance(self.trip, self.phases, self.trace, self.trace_settings)

    def read_igc(self, soaring_spot_info):
        # this is a candidate for and IGC reader class / aerofiles functionality
        f = open(soaring_spot_info.igc_directory + self.file_name, "U")  # U extension is a necessity for cross compatibility!
        full_file = f.readlines()
        f.close()

        for line in full_file:

            if line.startswith('B'):
                if len(self.trace) == 0 or (len(self.trace) > 0 and self.trace[-1][0:7] != line[0:7]):
                    self.trace.append(line)
                    continue

            if line.startswith('I'):
                no_extensions = int(line[1:3])
                i_record_byte = 3
                for extension_number in range(no_extensions):
                    extension_name = line[i_record_byte+4: i_record_byte+7]
                    extension_start_byte = int(line[i_record_byte:i_record_byte+2])
                    extension_end_byte = int(line[i_record_byte+2:i_record_byte+4])
                    i_record_byte += 7

                    if extension_name == 'ENL':
                        self.ENL = True
                        self.ENL_indices = [extension_start_byte, extension_end_byte]
                        self.trace_settings['enl_indices'] = [extension_start_byte, extension_end_byte]

            if line.startswith('LCU::HPGTYGLIDERTYPE:'):
                self.airplane = line[21:-1]
                continue

            if line.startswith('LCU::HPCIDCOMPETITIONID:'):
                self.competition_id = line[24:-1]
                continue

    def get_task_information(self):
        # this is a candidate for and IGC reader class / aerofiles functionality

        task_information = {
            't_min': None,
            'date': None,
            'start_opening': hhmmss2ss("09:00:00", 0),
            'multi_start': False,
            'aat': False,
            'lcu_lines': [],
            'lseeyou_lines': [],
            'utc_diff': None
        }

        f = open(self.folder_path + self.file_name, "U")  # U extension is a necessity for cross compatibility!
        full_file = f.readlines()
        f.close()

        for line in full_file:

            if line.startswith('LSEEYOU TSK'):

                tsk_split = line.split(',')
                for task_element in tsk_split:
                    if task_element.startswith('TaskTime'):
                        task_information['t_min'] = hhmmss2ss(task_element[9::], 0)  # assuming no UTC offset
                        task_information['aat'] = True
                    if task_element.startswith('NoStart'):
                        task_information['start_opening'] = hhmmss2ss(task_element[8::], 0)  # time in local time, not UTC
                    if task_element.startswith('MultiStart=True'):
                        task_information['multi_start'] = True
                continue

            if line.startswith('LCU::C'):
                task_information['lcu_lines'].append(line)
            if line.startswith('LSEEYOU OZ='):
                task_information['lseeyou_lines'].append(line)
            if line.startswith('LCU::HPTZNTIMEZONE:'):
                task_information['utc_diff'] = int(line[19:-1])

        # extract date from fist lcu line
        if len(task_information['lcu_lines']) != 0:
            task_information['date'] = get_date(task_information['lcu_lines'][0])

        return task_information

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
