from generalFunctions import hhmmss2ss, det_local_time, det_height,\
    print_array_debug, ss2hhmmss, determine_distance, used_engine,\
    determine_engine_start_i, get_date
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
        self.tsk_t = []
        self.tsk_i = []
        self.first_start_i = 0  # necessary for determination of outlanding on leg 0. quite rare case

        self.trip = None

        self.gps_altitude = True
        self.outlanded = False
        self.ENL = False
        self.ENL_indices = [0, 0]  # to store indices within b record
        self.outlanding_leg = 0
        self.outlanding_b_record = ""
        self.outlanding_distance = 0

        self.trace_settings = {
            'gps_altitude': True,
            'enl_indices': None
        }

        self.phases = None
        self.performance = None

        self.phases2 = None
        self.performance2 = None

    def analyze(self, competition_day):
        print self.file_name

        self.trip = Trip(competition_day.task, self.trace, self.trace_settings)

        self.determine_tsk_times(competition_day)
        self.phases = FlightPhases(settings, competition_day, self)
        self.performance = Performance(competition_day, self)

        # expand constructors with needed arguments and default at None
        if len(self.trip.fixes) >= 1:  # at least started
            self.phases2 = FlightPhases(settings, competition_day, self, self.trip, self.trace, self.trace_settings)
            self.performance2 = Performance(competition_day, self, competition_day.task, self.trip, self.phases2, self.trace, self.trace_settings)

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

    def determine_outlanding_location(self, competition_day):

        task_pointM1 = competition_day.task.taskpoints[self.outlanding_leg].LCU_line
        task_point = competition_day.task.taskpoints[self.outlanding_leg+1].LCU_line

        if self.outlanding_b_record != "":
            b_rec = self.outlanding_b_record

            # outlanding distance = distance between tps minus distance from next tp to outlanding
            outlanding_dist = determine_distance(task_pointM1, task_point, 'tsk', 'tsk')
            outlanding_dist -= determine_distance(task_point, b_rec, 'tsk', 'pnt')

            self.outlanding_distance = outlanding_dist

        else:
            last_tp_i = self.first_start_i if self.outlanding_leg == 0 else self.tsk_i[-1]
            max_dist = 0

            self.outlanding_b_record = self.trace[last_tp_i]  # default
            for i in range(len(self.trace)):

                if i > last_tp_i:

                    b_rec = self.trace[i]

                    # outlanding distance = distance between tps minus distance from next tp to outlanding
                    outlanding_dist = determine_distance(task_pointM1, task_point, 'tsk', 'tsk')
                    outlanding_dist -= determine_distance(task_point, b_rec, 'tsk', 'pnt')

                    if outlanding_dist > max_dist:
                        max_dist = outlanding_dist
                        self.outlanding_b_record = b_rec

            self.outlanding_distance = max_dist

    def start_refinement(self, competition_day, b_record1, b_record2):
        from generalFunctions import interpolate_b_records

        b_records_interpolated = interpolate_b_records(b_record1, b_record2)

        refinement = 0
        for index in range(len(b_records_interpolated)-1):
            b_record1 = b_records_interpolated[-2-index]
            b_record2 = b_records_interpolated[-1-index]
            if competition_day.task.taskpoints[0].taskpoint_completed(b_record1, b_record2):
                return refinement
            else:
                refinement += 1

        return refinement

    def determine_tsk_times(self, competition_day):

        leg = -1  # leg before startline is crossed
        possible_enl = 0  # excluding motor test

        for i in range(len(self.trace)):

            if self.gps_altitude and det_height(self.trace[i], False) != 0:
                self.gps_altitude = False
                self.trace_settings['gps_altitude'] = False

            t = det_local_time(self.trace[i], competition_day.utc_diff)

            if leg == -1 and t > competition_day.task.start_opening and i > 0:
                start = competition_day.task.taskpoints[0]
                if start.taskpoint_completed(self.trace[i - 1], self.trace[i]):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    self.first_start_i = i
                    leg = 0
                    possible_enl = 0
            elif leg == 0:
                if used_engine(self, i):
                    possible_enl = determine_engine_start_i(self, i)
                start = competition_day.task.taskpoints[0]
                tp1 = competition_day.task.taskpoints[1]
                if start.taskpoint_completed(self.trace[i - 1], self.trace[i]):
                    self.tsk_t[0] = t
                    self.tsk_i[0] = i
                    possible_enl = 0
                if tp1.taskpoint_completed(self.trace[i - 1], self.trace[i]):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1
            elif 0 < leg < competition_day.task.no_tps:
                if used_engine(self, i):
                    possible_enl = determine_engine_start_i(self, i)
                    break
                next_tp = competition_day.task.taskpoints[leg+1]
                if next_tp.taskpoint_completed(self.trace[i - 1], self.trace[i]):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1
            elif leg == competition_day.task.no_legs - 1:
                if used_engine(self, i):
                    possible_enl = determine_engine_start_i(self, i)
                    break
                finish = competition_day.task.taskpoints[-1]
                if finish.taskpoint_completed(self.trace[i - 1], self.trace[i]):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1

        b_record1 = self.trace[self.tsk_i[0]-1]
        b_record2 = self.trace[self.tsk_i[0]]
        self.tsk_t[0] -= self.start_refinement(competition_day, b_record1, b_record2)
        self.tsk_t[0] -= 1  # Soaring spot takes point before start line!

        if not possible_enl == 0:
            self.outlanding_b_record = self.trace[possible_enl]

        if not possible_enl == 0 or len(self.tsk_t) != competition_day.task.no_legs + 1:
            self.outlanded = True
            self.outlanding_leg = len(self.tsk_t)-1
            self.determine_outlanding_location(competition_day)

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
