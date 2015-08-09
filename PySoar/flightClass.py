from generalFunctions import hhmmss2ss


class Flight(object):

    def __init__(self, file_name):
        self.file_name = file_name

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
                if self.b_records.__len__() > 0 and self.b_records[-1][0:7] != line[0:7]:
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
                        competition_day.start_opening = hhmmss2ss(task_element[8::])

            if not task_found:
                if line.startswith('LCU::C'):
                    competition_day.task.append(line)
                if line.startswith('LSEEYOU OZ='):
                    competition_day.task_rules.append(line)
                if line.startswith('LCU::HPTZNTIMEZONE:'):
                    competition_day.utc_to_local = int(line[19:-1])

if __name__ == '__main__':
    from main import run
    run()
