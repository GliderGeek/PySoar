from generalFunctions import hhmmss2ss, det_local_time, line_crossed, turnpoint_rounded, det_height,\
    print_array_debug, ss2hhmmss, determine_distance, det_bearing, det_bearing_change, start_refinement
from settingsClass import Settings

settings = Settings()


class Flight(object):
    def __init__(self, file_name, ranking):
        self.file_name = file_name

        self.airplane = ""
        self.competition_id = ""
        self.ranking = ranking

        self.b_records = []
        self.tsk_t = []
        self.tsk_i = []
        self.first_start_i = 0  # necessary for determination of outlanding on leg 0. quite rare case

        self.gps_altitude = True
        self.outlanded = False
        self.outlanding_leg = 0
        self.outlanding_b_record = ""
        self.outlanding_distance = 0

    def read_igc(self, competition_day, soaring_spot_info):
        f = open(soaring_spot_info.igc_directory + self.file_name, "U")  # U extension is a necessity for cross compatibility!
        full_file = f.readlines()
        f.close()

        if len(competition_day.task) != 0:
            competition_day.task_found = True

        for line in full_file:

            if line.startswith('B'):
                if len(self.b_records) == 0 or (len(self.b_records) > 0 and self.b_records[-1][0:7] != line[0:7]):
                    self.b_records.append(line)
                    continue

            if line.startswith('LCU::HPGTYGLIDERTYPE:'):
                self.airplane = line[21:-1]
                continue

            if line.startswith('LCU::HPCIDCOMPETITIONID:'):
                self.competition_id = line[24:-1]
                continue

            if line.startswith('LSEEYOU TSK'):

                tsk_split = line.split(',')
                for task_element in tsk_split:
                    if task_element.startswith('TaskTime') and not hasattr(competition_day, 't_min'):
                        competition_day.t_min = hhmmss2ss(task_element[9::], 0)  # asuming no UTC offset
                        competition_day.aat = True  # Default is False
                    if task_element.startswith('NoStart') and competition_day.start_opening == 0:
                        competition_day.start_opening = hhmmss2ss(task_element[8::], 0)  # time in local time, not UTC
                continue

            if not competition_day.task_found:
                if line.startswith('LCU::C'):
                    competition_day.task.append(line)
                if line.startswith('LSEEYOU OZ='):
                    competition_day.task_rules.append(line)
                if line.startswith('LCU::HPTZNTIMEZONE:'):
                    competition_day.utc_to_local = int(line[19:-1])

    def determine_outlanding_location(self, competition_day):
        from math import cos, pi, radians
        max_dist = 0

        task_pointM1 = competition_day.task[self.outlanding_leg+2]
        task_point = competition_day.task[self.outlanding_leg+2+1]
        bearing_to_next_tp = det_bearing(task_pointM1, task_point, 'tsk', 'tsk')

        last_tp_i = self.first_start_i if self.outlanding_leg == 0 else self.tsk_i[-1]

        for i in range(self.b_records.__len__()):

            if i > last_tp_i:

                b_rec = self.b_records[i]

                temp_dist = determine_distance(task_pointM1, b_rec, 'tsk', 'pnt')
                bearing_to_point = det_bearing(task_pointM1, b_rec, 'tsk', 'pnt')

                angle = abs(det_bearing_change(bearing_to_point, bearing_to_next_tp))
                projected_dist = cos(radians(angle)) * temp_dist

                if projected_dist > max_dist:
                    max_dist = projected_dist
                    self.outlanding_b_record = b_rec

        self.outlanding_distance = max_dist

    def determine_tsk_times(self, competition_day):
        leg = -1  # leg before startline is crossed

        for i in range(self.b_records.__len__()):
            if self.gps_altitude and det_height(self.b_records[i], False) != 0:
                self.gps_altitude = False

            t = det_local_time(self.b_records[i], competition_day.utc_to_local)

            if leg == -1 and t > competition_day.start_opening and i > 0:
                if line_crossed(self.b_records[i - 1], self.b_records[i], 'start', competition_day):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    self.first_start_i = i
                    leg = 0
            elif leg == 0:
                if line_crossed(self.b_records[i - 1], self.b_records[i], 'start', competition_day):
                    self.tsk_t[0] = t
                    self.tsk_i[0] = i
                if turnpoint_rounded(self.b_records[i], leg, competition_day):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1
            elif 0 < leg < competition_day.no_tps:
                if turnpoint_rounded(self.b_records[i], leg, competition_day):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1
            elif leg == competition_day.no_legs - 1:
                if competition_day.tp_line[-1]:  # finish line
                    finished = line_crossed(self.b_records[i - 1], self.b_records[i], 'finish', competition_day)
                else:  # finish circle
                    finished = turnpoint_rounded(self.b_records[i], leg, competition_day)
                if finished:
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1

        b_record1 = self.b_records[self.tsk_i[0]-1]
        b_record2 = self.b_records[self.tsk_i[0]]
        self.tsk_t[0] += start_refinement(competition_day, b_record1, b_record2)
        self.tsk_t[0] -= 1  # Soaring spot takes point before start line!

        if self.tsk_t.__len__() != competition_day.no_legs + 1:
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
    from main_pysoar import run

    run()
