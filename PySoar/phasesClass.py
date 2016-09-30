from generalFunctions import det_local_time, determine_distance, det_bearing, det_bearing_change, ss2hhmmss,\
    det_height, determine_flown_task_distance
from settingsClass import Settings
import datetime

settings = Settings()


class FlightPhases(object):

    def get_difference_bib(self):
        return {"height_difference": [], "height":[], "distance": [], "distance_task": [], "time_difference": [], "time": [], "phase": []}

    def __init__(self, competition_day):
        self.all = []
        self.leg = []

        self.cruises_leg = []
        self.cruises_all = 0
        self.thermals_leg = []
        self.thermals_all = 0

        self.pointwise_all = {}
        self.pointwise_leg = []

        for leg in range(competition_day.task.no_legs):
            self.leg.append([])
            self.pointwise_leg.append(self.get_difference_bib())
            self.cruises_leg.append(0)
            self.thermals_leg.append(0)

    def create_entry(self, i_start, t_start, phase, leg):
        content = {'i_start': i_start, 'i_end': i_start, 't_start': t_start, 't_end': t_start, 'phase': phase}
        if leg == -2:  # whole flight, -1 reserved for phase before start-line has been crossed
            self.all.append(content)
            if phase == 'cruise':
                self.cruises_all += 1
            else:
                self.thermals_all += 1
        elif leg >= 0:
            self.leg[leg].append(content)
            if phase == 'cruise':
                self.cruises_leg[leg] += 1
            else:
                self.thermals_leg[leg] += 1

    def close_entry(self, i_end, t_end, leg):
        if leg == -2:  # whole flight, -1 reserved for phase before start-line has been crossed
            self.all[-1]['i_end'] = i_end
            self.all[-1]['t_end'] = t_end
        elif leg >= 0:
            self.leg[leg][-1]['i_end'] = i_end
            self.leg[leg][-1]['t_end'] = t_end

    def determine_phases(self, settings, competitionday, flight):

        b_record_m1 = flight.b_records[flight.tsk_i[0] - 2]
        time_m1 = det_local_time(b_record_m1, competitionday.utc_diff)

        b_record = flight.b_records[flight.tsk_i[0] - 1]
        time = det_local_time(b_record, competitionday.utc_diff)
        bearing = det_bearing(b_record_m1, b_record, 'pnt', 'pnt')

        cruise = True
        possible_cruise_start = 0
        possible_thermal_start = 0
        cruise_distance = 0
        temp_bearing_change = 0
        possible_turn_dir = 'left'
        sharp_thermal_entry_found = False
        bearing_change_tot = 0
        leg = 0

        self.create_entry(flight.tsk_i[0], time_m1, 'cruise', -2)
        self.create_entry(flight.tsk_i[0], time_m1, 'cruise', leg)

        for i in range(len(flight.b_records)):
            if flight.tsk_i[0] < i < flight.tsk_i[-1]:

                time_m2 = time_m1

                time_m1 = time
                bearing_m1 = bearing
                b_record_m1 = b_record

                b_record = flight.b_records[i]
                time = det_local_time(b_record, competitionday.utc_diff)

                bearing = det_bearing(b_record_m1, b_record, 'pnt', 'pnt')
                bearing_change = det_bearing_change(bearing_m1, bearing)
                bearing_change_rate = bearing_change / (time - 0.5*time_m1 - 0.5*time_m2)

                if i == flight.tsk_i[leg+1]:
                    phase = 'cruise' if cruise else 'thermal'
                    leg += 1
                    self.close_entry(i, time, leg-1)
                    self.create_entry(i, time, phase, leg)

                if cruise:

                    if (possible_turn_dir == 'left' and bearing_change_rate < 1e-2) or\
                            (possible_turn_dir == 'right' and bearing_change_rate > -1e-2):

                        bearing_change_tot += det_bearing_change(bearing_m1, bearing)

                        if possible_thermal_start == 0:
                            possible_thermal_start = i
                        elif (not sharp_thermal_entry_found) and abs(bearing_change_rate) > settings.cruise_threshold_bearingRate:
                            sharp_thermal_entry_found = True
                            possible_thermal_start = i

                    else:  # sign change
                        bearing_change_tot = det_bearing_change(bearing_m1, bearing)

                        if bearing_change_rate < 0:
                            possible_turn_dir = 'left'
                        else:
                            possible_turn_dir = 'right'

                        possible_thermal_start = i

                    if abs(bearing_change_tot) > settings.cruise_threshold_bearingTot:
                        cruise = False
                        thermal_start_time = det_local_time(flight.b_records[possible_thermal_start], competitionday.utc_diff)
                        self.close_entry(possible_thermal_start, thermal_start_time, -2)
                        self.close_entry(possible_thermal_start, thermal_start_time, leg)
                        self.create_entry(possible_thermal_start, thermal_start_time, 'thermal', -2)
                        self.create_entry(possible_thermal_start, thermal_start_time, 'thermal', leg)
                        possible_thermal_start = 0
                        sharp_thermal_entry_found = False
                        bearing_change_tot = 0

                else:  # thermal
                    if abs(bearing_change_rate) > settings.thermal_threshold_bearingRate:
                        if possible_cruise_start != 0:
                            cruise_distance = 0
                            temp_bearing_change = 0
                    else:  # possible cruise
                        if cruise_distance == 0:
                            possible_cruise_start = i
                            possible_cruise_t = time
                            temp_bearing_change += bearing_change
                            temp_bearing_rate_avg = 0
                        else:
                            temp_bearing_change += bearing_change
                            temp_bearing_rate_avg = temp_bearing_change / (time-possible_cruise_t)

                        cruise_distance = determine_distance(flight.b_records[possible_cruise_start-1], b_record,
                                                             'pnt', 'pnt')

                        if cruise_distance > settings.thermal_threshold_distance and \
                                        abs(temp_bearing_rate_avg) < settings.thermal_threshold_bearingRateAvg:

                            cruise = True
                            self.close_entry(possible_cruise_start, possible_cruise_t, -2)
                            self.close_entry(possible_cruise_start, possible_cruise_t, leg)
                            self.create_entry(possible_cruise_start, possible_cruise_t, 'cruise', -2)
                            self.create_entry(possible_cruise_start, possible_cruise_t, 'cruise', leg)
                            possible_cruise_start = 0
                            cruise_distance = 0
                            temp_bearing_change = 0
                            bearing_change_tot = 0

        time = det_local_time(flight.b_records[flight.tsk_i[-1]], competitionday.utc_diff)
        self.close_entry(flight.tsk_i[-1], time, -2)
        self.close_entry(flight.tsk_i[-1], time, leg)

    def append_differences(self, difference_indicators, leg):
        for key, value in difference_indicators.iteritems():
            self.pointwise_all[key].append(value)
            self.pointwise_leg[leg-1][key].append(value)

    def determine_point_statistics(self, flight, competition_day):

        self.pointwise_all = self.get_difference_bib()
        for leg in range(competition_day.task.no_legs):
            self.pointwise_leg.append(self.get_difference_bib())

        phase_number = 0
        leg = 0
        phase = self.all[phase_number]['phase']

        for i in range(flight.b_records.__len__()):
            if flight.tsk_i[0] <= i < flight.tsk_i[-1]:

                if self.all[phase_number]['i_end'] == i:
                    phase_number += 1
                    phase = self.all[phase_number]['phase']

                if i == flight.tsk_i[leg]:
                    leg += 1

                height_difference = det_height(flight.b_records[i+1], flight.gps_altitude) -\
                                    det_height(flight.b_records[i], flight.gps_altitude)
                height = det_height(flight.b_records[i], flight.gps_altitude)
                distance = determine_distance(flight.b_records[i], flight.b_records[i+1], 'pnt', 'pnt')
                time_difference = det_local_time(flight.b_records[i+1], competition_day.utc_diff) -\
                                  det_local_time(flight.b_records[i], competition_day.utc_diff)
                time_secs = det_local_time(flight.b_records[i], competition_day.utc_diff)
                date_obj = datetime.datetime(2014, 6, 21) + datetime.timedelta(seconds=time_secs)
                distance_task = determine_flown_task_distance(leg, flight.b_records[i], competition_day)

                difference_indicators = {'height_difference': height_difference,
                                         'height': height,
                                         'distance': distance,
                                         'distance_task': distance_task,
                                         'time_difference': time_difference,
                                         'time': date_obj,
                                         'phase': phase}

                self.append_differences(difference_indicators, leg)

    def save_phases(self, soaring_spot_info, flight):
        file_name = settings.current_dir + "/debug_logs/phasesClassPhaseDebug.txt"
        if flight.file_name == soaring_spot_info.file_names[0]:
            text_file = open(file_name, "w")  # overwriting if exist
        else:
            text_file = open(file_name, "a")  # appending

        text_file.write(flight.file_name + "\n\n")
        text_file.write("phases.all:\n")
        for entry in self.all:
            text_file.write(entry['phase'] + '\t' + ss2hhmmss(entry['t_start']) + '\t'
                            + ss2hhmmss(entry['t_end']) + '\t' + str(entry['i_start']) + '\t' + str(entry['i_end']) + "\n")
        text_file.write("\n")

        for leg in range(len(self.leg)):
            text_file.write('leg' + str(leg) + "\n")
            for entry in self.leg[leg]:
                text_file.write(entry['phase'] + '\t' + ss2hhmmss(entry['t_start'])
                                + '\t' + ss2hhmmss(entry['t_end']) + '\t' + str(entry['i_start']) + '\t' + str(entry['i_end']) + "\n")
            text_file.write("\n")

        text_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

        text_file.close()

    def save_point_stats(self, soaring_spot_info, flight):
        file_name = settings.current_dir + "/debug_logs/phasesClassPointStatsDebug.txt"
        if flight.file_name == soaring_spot_info.file_names[0]:
            text_file = open(file_name, "w")  # overwriting if exist
        else:
            text_file = open(file_name, "a")  # appending

        text_file.write(flight.file_name + "\n\n")
        text_file.write("pointwise_all:\n")

        for key in self.pointwise_all.iterkeys():
            text_file.write(key + ":" + str(self.pointwise_all[key]) + "\n")

        text_file.write("\n")
        for leg in range(len(self.leg)):
            text_file.write('leg' + str(leg) + "\n")
            for key in self.pointwise_leg[leg].iterkeys():
                text_file.write(key + ":" + str(self.pointwise_all[key]) + "\n")

        text_file.write("\n")
        text_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

        text_file.close()

    def save(self, soaring_spot_info, flight):
        self.save_phases(soaring_spot_info, flight)
        # self.save_point_stats(soaring_spot_info, flight)


if __name__ == '__main__':
    from main_pysoar import run
    run()

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
