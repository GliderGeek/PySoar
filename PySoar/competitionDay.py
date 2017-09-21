import copy
import os
import re

from task import Task
from generalFunctions import get_date_cuc, get_date_scs, det_height, hhmmss2ss
from settingsClass import Settings
from race_task import RaceTask
from aat import AAT
from flightClass import Flight

settings = Settings()


class CompetitionDay(object):

    def __init__(self, url_status, source, igc_directory, file_names, rankings, plane, date):

        self.source = source
        self.analyzed = False
        
        self.flights, task_infos = self.process_files(igc_directory, file_names, rankings, plane, date)
        
        self.task, self.date, self.utc_diff = self.get_task(task_infos)

        # shortcoming of PySoar
        if self.task.multi_start:
            url_status.configure(text="Multiple starting points not implemented!", foreground='red')
            url_status.update()
            return

    def analyze_flights(self, analysis_progress):
        flights_analyzed = 0
        for flight in self.flights:
            flight.analyze(self.task)

            flights_analyzed += 1
            if analysis_progress is not None:
                analysis_progress.configure(text='Analyzed: %s/%s' %
                                                 (str(flights_analyzed), str(len(self.flights))))
                analysis_progress.update()

        self.analyzed = True

    def process_files(self, igc_directory, file_names, rankings,plane, date):
        flights = list()
        task_infos = list()

        if self.source == 'cuc':
            for file_name, ranking in zip(file_names, rankings):

                trace, trace_settings, airplane, competition_id, task_information = self.read_igc(igc_directory, file_name,None,None)

                flights.append(Flight(file_name, competition_id, airplane, ranking, trace, trace_settings))
                task_infos.append(task_information)
        elif self.source == 'scs':
            for file_name, ranking, plane in zip(file_names, rankings, plane):

                trace, trace_settings, airplane, competition_id, task_information = self.read_igc(igc_directory, file_name, plane, date)

                flights.append(Flight(file_name, competition_id, airplane, ranking, trace, trace_settings))
                task_infos.append(task_information)
            
        return flights, task_infos

    def read_igc(self,folder_path, file_name, plane, date):
        # this is a candidate for and IGC reader class / aerofiles functionality
        
        with open(os.path.join(folder_path, file_name), "U") as f:  # U extension for cross compatibility!
            full_file = f.readlines()
        
        trace_settings = {
            'gps_altitude': True,
            'enl_indices': None
        }

        task_information = {
            't_min': None,
            'date': None,
            'start_opening': hhmmss2ss("09:00:00", 0),
            'multi_start': False,
            'aat': False,
            'lcu_lines': [],
            'lseeyou_lines': [],
            'utc_diff': None,
            'lscs_lines':[],
            'lscs_lines_tp':[]
        }

        trace = list()
        airplane = None
        competition_id = None
        for line in full_file:

            if line.startswith('B'):

                # put gps_altitude to False when nonzero pressure altitude is found
                if trace_settings['gps_altitude'] is True and det_height(line, gps_altitude=False) != 0:
                    trace_settings['gps_altitude'] = False

                if len(trace) == 0 or (len(trace) > 0 and trace[-1][0:7] != line[0:7]):
                    trace.append(line)
                    continue

            elif line.startswith('I'):
                no_extensions = int(line[1:3])
                i_record_byte = 3
                for extension_number in range(no_extensions):
                    extension_name = line[i_record_byte+4: i_record_byte+7]
                    extension_start_byte = int(line[i_record_byte:i_record_byte+2])
                    extension_end_byte = int(line[i_record_byte+2:i_record_byte+4])
                    i_record_byte += 7

                    if extension_name == 'ENL':
                        trace_settings['enl_indices'] = [extension_start_byte, extension_end_byte]

            if self.source == 'cuc':          
                if line.startswith('LCU::HPGTYGLIDERTYPE:'):
                    airplane = line[21:-1]
                    continue    

                elif line.startswith('LCU::HPCIDCOMPETITIONID:'):
                    competition_id = line[24:-1]
                    continue

                elif line.startswith('LSEEYOU TSK'):

                    tsk_split = line.split(',')
                    for task_element in tsk_split:
                        if task_element.startswith('TaskTime'):
                            task_information['t_min'] = hhmmss2ss(task_element[9::], 0)  # assuming no UTC offset
                            task_information['aat'] = True
                        if task_element.startswith('NoStart'):
                            task_information['start_opening'] = hhmmss2ss(task_element[8::],
                                                                          0)  # time in local time, not UTC
                        if task_element.startswith('MultiStart=True'):
                            task_information['multi_start'] = True
                    continue

                elif line.startswith('LCU::C'):
                    task_information['lcu_lines'].append(line)
                elif line.startswith('LSEEYOU OZ='):
                    task_information['lseeyou_lines'].append(line)
                elif line.startswith('LCU::HPTZNTIMEZONE:'):
                    task_information['utc_diff'] = int(line[19:-1])

                # extract date from fist lcu line
                if len(task_information['lcu_lines']) != 0:
                    task_information['date'] = get_date_cuc(task_information['lcu_lines'][0])


                # fix error in task definition: e.g.: LSEEYOU OZ=-1,Style=2SpeedStyle=0,R1=5000m,A1=180,Line=1
                # SpeedStyle=# is removed, where # is a number
                for line_index, line in enumerate(task_information['lseeyou_lines']):
                    task_information['lseeyou_lines'][line_index] = re.sub(r"SpeedStyle=\d", "", line)

                # fix wrong style definition on start and finish points
                    task_information['lseeyou_lines'][0] = task_information['lseeyou_lines'][0].replace('Style=1', 'Style=2')
                    task_information['lseeyou_lines'][-1] = task_information['lseeyou_lines'][-1].replace('Style=1', 'Style=3')

            elif self.source == 'scs':
                
                # all times are UTC, so utc_diff=0
                task_information['utc_diff'] = 0

                if line.startswith('LSCS'):
                
                    # is task AAT
                    if line.startswith('LSCSDCID:'):
                        competition_id = line[9:-1]
                        continue

                    if line.startswith('LSCSDGate open'):
                        task_information['start_opening'] = hhmmss2ss( ((line.split(':'))[1]+":"+((line.split(':'))[2])[0:-1]+":00"),0)
                        
                    if line.startswith('LSCSDTime window:'):
                        task_information['t_min'] = hhmmss2ss( ((line.split(':'))[1]+":"+((line.split(':'))[2])[0:-1]+":00"),0 )
                        if task_information['t_min'] > 0:
                            task_information['aat'] = True

                    if line.startswith('LSCSC'):
                        task_information['lscs_lines_tp'].append(line)
                        
                    if line.startswith('LSCS'):
                        task_information['lscs_lines'].append(line)

                    task_information['date'] = get_date_scs(date)
                    airplane = plane
                    
        return trace, trace_settings, airplane, competition_id, task_information

    @staticmethod
    def check_dates_in_cuc_task_info(task_info1, task_info2):
        current_task_date = get_date_cuc(task_info1['lcu_lines'][0])
        new_task_date = get_date_cuc(task_info2['lcu_lines'][0])
        if new_task_date != current_task_date:
            print('different task date present in igc files')
            # issue #65

    @staticmethod
    def check_cuc_task_info_equal(task_info1, task_info2):
        # temporarily take out first lcu_line (timestamped) for comparison
        temp_task_info = copy.deepcopy(task_info1)
        temp_new_task_info = copy.deepcopy(task_info2)
        del temp_task_info['lcu_lines'][0]
        del temp_new_task_info['lcu_lines'][0]

        if temp_task_info != temp_new_task_info:
            print 'different task information present in igc files'
            return False
            # issue #65

    @staticmethod
    def get_correct_cuc_task_info(task_info, new_task_info):

        # check dates separately because it is taken out for comparison later
        CompetitionDay.check_dates_in_cuc_task_info(task_info, new_task_info)

        CompetitionDay.check_cuc_task_info_equal(task_info, new_task_info)

        if len(task_info['lcu_lines']) == 0 and len(new_task_info['lcu_lines']) != 0:
            task_info = new_task_info
            print 'used new task info because old one did not have full task'  # uncertain if this happens

        return task_info

    def get_task(self, task_infos):

        task_info = None
        for flight, new_task_info in zip(self.flights, task_infos):
            if task_info is None:
                task_info = new_task_info
            else:
                if self.source == 'cuc':
                    task_info = self.get_correct_cuc_task_info(task_info, new_task_info)
                elif self.source == 'scs':
                    pass  # possibility to add logic in determining correct task

        multi_start = task_info['multi_start']
        start_opening = task_info['start_opening']
        utc_diff = task_info['utc_diff']

        if self.source == 'cuc':
            lcu_lines = task_info['lcu_lines']
            lseeyou_lines = task_info['lseeyou_lines']
            taskpoints = Task.taskpoints_from_cuc(lcu_lines, lseeyou_lines)
        elif self.source == 'scs':
            lscs_lines_tp = task_info['lscs_lines_tp']
            lscs_lines = task_info['lscs_lines']
            taskpoints = Task.taskpoints_from_scs(lscs_lines,lscs_lines_tp)
        else:
            raise ValueError('Source not implemented: %s' % self.source)

        
        if task_info['aat']:
            t_min = task_info['t_min']
            print(t_min)
            task = AAT(taskpoints, multi_start, start_opening, utc_diff, t_min)
        else:
            task = RaceTask(taskpoints, multi_start, start_opening, utc_diff)
            
        # utc difference and date
        date = task_info['date']
        utc_diff = task_info['utc_diff']

        return task, date, utc_diff


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
