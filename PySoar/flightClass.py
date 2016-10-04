from generalFunctions import hhmmss2ss, det_local_time, det_height,\
    print_array_debug, ss2hhmmss, determine_distance, det_bearing, det_bearing_change, used_engine,\
    determine_engine_start_i, get_date
from settingsClass import Settings

settings = Settings()


class Flight(object):
    def __init__(self, folder_path, file_name, ranking):
        self.file_name = file_name

        self.folder_path = folder_path

        self.airplane = ""
        self.competition_id = ""
        self.ranking = ranking

        self.b_records = []
        self.tsk_t = []
        self.tsk_i = []
        self.first_start_i = 0  # necessary for determination of outlanding on leg 0. quite rare case

        self.gps_altitude = True
        self.outlanded = False
        self.ENL = False
        self.ENL_indices = [0, 0]  # to store indices within b record
        self.outlanding_leg = 0
        self.outlanding_b_record = ""
        self.outlanding_distance = 0

    def read_igc(self, soaring_spot_info):
        f = open(soaring_spot_info.igc_directory + self.file_name, "U")  # U extension is a necessity for cross compatibility!
        full_file = f.readlines()
        f.close()

        for line in full_file:

            if line.startswith('B'):
                if len(self.b_records) == 0 or (len(self.b_records) > 0 and self.b_records[-1][0:7] != line[0:7]):
                    self.b_records.append(line)
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

            self.outlanding_b_record = self.b_records[last_tp_i]  # default
            for i in range(len(self.b_records)):

                if i > last_tp_i:

                    b_rec = self.b_records[i]

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

        for i in range(len(self.b_records)):

            if self.gps_altitude and det_height(self.b_records[i], False) != 0:
                self.gps_altitude = False

            t = det_local_time(self.b_records[i], competition_day.utc_diff)

            if leg == -1 and t > competition_day.task.start_opening and i > 0:
                start = competition_day.task.taskpoints[0]
                if start.taskpoint_completed(self.b_records[i - 1], self.b_records[i]):
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
                if start.taskpoint_completed(self.b_records[i - 1], self.b_records[i]):
                    if self.file_name == "PR.igc":
                        print "PR restart at t=%s" % ss2hhmmss(t)
                    self.tsk_t[0] = t
                    self.tsk_i[0] = i
                    possible_enl = 0
                if tp1.taskpoint_completed(self.b_records[i - 1], self.b_records[i]):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1
            elif 0 < leg < competition_day.task.no_tps:
                if used_engine(self, i):
                    possible_enl = determine_engine_start_i(self, i)
                    break
                next_tp = competition_day.task.taskpoints[leg+1]
                if next_tp.taskpoint_completed(self.b_records[i - 1], self.b_records[i]):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1
            elif leg == competition_day.task.no_legs - 1:
                if used_engine(self, i):
                    possible_enl = determine_engine_start_i(self, i)
                    break
                finish = competition_day.task.taskpoints[-1]
                if finish.taskpoint_completed(self.b_records[i - 1], self.b_records[i]):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1

        b_record1 = self.b_records[self.tsk_i[0]-1]
        b_record2 = self.b_records[self.tsk_i[0]]
        self.tsk_t[0] -= self.start_refinement(competition_day, b_record1, b_record2)
        self.tsk_t[0] -= 1  # Soaring spot takes point before start line!

        if not possible_enl == 0:
            self.outlanding_b_record = self.b_records[possible_enl]

        if not possible_enl == 0 or len(self.tsk_t) != competition_day.task.no_legs + 1:
            self.outlanded = True
            self.outlanding_leg = len(self.tsk_t)-1
            self.determine_outlanding_location(competition_day)

    def save(self, soaring_spot_info):
        file_name = settings.current_dir + "/debug_logs/flightClassDebug.txt"
        if self.file_name == soaring_spot_info.file_names[0]:
            text_file = open(file_name, "w")  # overwriting if exist
        else:
            text_file = open(file_name, "a")  # appending

        text_file.write("file_name: " + self.file_name + "\n")
        text_file.write("airplane: " + self.airplane + "\n")
        text_file.write("competition_id: " + self.competition_id + "\n\n")

        print_array_debug(text_file, "tsk_t", self.tsk_t)

        tsk_t_temp = [""] * len(self.tsk_t)
        for ii in range(len(self.tsk_t)):
            tsk_t_temp[ii] = ss2hhmmss(self.tsk_t[ii])

        print_array_debug(text_file, "tsk_t", tsk_t_temp)
        print_array_debug(text_file, "tsk_i", self.tsk_i)

        text_file.write("gps_altitude: " + str(self.gps_altitude) + "\n")
        text_file.write("outlanded: " + str(self.outlanded) + "\n")
        if self.outlanded:
            text_file.write("outlanding_leg: " + str(self.outlanding_leg) + "\n")
            text_file.write("outlanding time(UTC): " + ss2hhmmss(det_local_time(self.outlanding_b_record, 0)) + "\n")
            text_file.write("outlanding distance from previous tp: " + str(self.outlanding_distance) + "\n")
        text_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

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
