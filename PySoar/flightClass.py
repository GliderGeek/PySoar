from generalFunctions import hhmmss2ss, det_local_time, line_crossed, turnpoint_rounded, det_height


class Flight(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.outlanded = False

    def read_igc(self, competition_day):
        print 'reading: ' + self.file_name

        f = open(competition_day.file_paths[self.file_name])
        full_file = f.readlines()
        f.close()

        self.b_records = []
        competition_day.aat = False

        if len(competition_day.task) == 0:
            task_found = False
        else:
            task_found = True

        for line in full_file:

            if line.startswith('B'):
                if len(self.b_records) == 0 or (len(self.b_records) > 0 and self.b_records[-1][0:7] != line[0:7]):
                    self.b_records.append(line)

            if line.startswith('LCU::HPGTYGLIDERTYPE:'):
                self.airplane = line[21:-1]

            if line.startswith('LCU::HPCIDCOMPETITIONID:'):
                self.competition_id = line[24:-1]

            if line.startswith('LSEEYOU TSK'):
                tsk_split = line.split(',')
                for task_element in tsk_split:
                    if task_element.startswith('TaskTime') and not hasattr(competition_day, 't_min'):
                        competition_day.t_min = hhmmss2ss(task_element[9::])
                        competition_day.aat = True
                    if task_element.startswith('NoStart') and not hasattr(competition_day, 'start_opening'):
                        competition_day.start_opening = hhmmss2ss(task_element[8::], 0)  # time in local time, not UTC

            if not task_found:
                if line.startswith('LCU::C'):
                    competition_day.task.append(line)
                if line.startswith('LSEEYOU OZ='):
                    competition_day.task_rules.append(line)
                if line.startswith('LCU::HPTZNTIMEZONE:'):
                    competition_day.utc_to_local = int(line[19:-1])

    def determine_tsk_times(self, competition_day):
        leg = 0
        self.tsk_t = []
        self.tsk_i = []
        self.gps_altitude = True

        for i in range(self.b_records.__len__()):

            # Construction to determine gps or baro altitude usage
            if self.gps_altitude and det_height(self.b_records[i], self.gps_altitude) != 0:
                self.gps_altitude = False

            t = det_local_time(self.b_records[i], competition_day.utc_to_local)

            if leg == 0 and t > competition_day.start_opening and i > 0:
                if line_crossed(self.b_records[i - 1], self.b_records[i], 'start', competition_day):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg = 1
            elif leg == 1:
                if line_crossed(self.b_records[i - 1], self.b_records[i], 'start', competition_day):
                    self.tsk_t[0] = t
                    self.tsk_i[0] = i
                if turnpoint_rounded(self.b_records[i], leg, competition_day):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1
            elif 1 < leg <= competition_day.no_tps:
                if turnpoint_rounded(self.b_records[i], leg, competition_day):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1
            elif leg == competition_day.no_tps + 1:
                if line_crossed(self.b_records[i - 1], self.b_records[i], 'finish', competition_day):
                    self.tsk_t.append(t)
                    self.tsk_i.append(i)
                    leg += 1

        if self.tsk_t.__len__() != competition_day.no_tps + 1:
            self.outlanded = True


if __name__ == '__main__':
    from main import run

    run()
