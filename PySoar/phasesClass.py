from generalFunctions import det_local_time, determine_distance, det_bearing, det_bearing_change, ss2hhmmss,\
    det_height
from settingsClass import Settings
import datetime

settings = Settings()


class FlightPhases(object):

    def get_difference_bib(self):
        return {"height_difference": [], "height":[], "distance": [], "time_difference": [], "time": [], "phase": []}

    def __init__(self, trip, trace, trace_settings):
        self.all = []
        self.leg = []

        self.cruises_leg = []
        self.cruises_all = 0
        self.thermals_leg = []
        self.thermals_all = 0

        self.pointwise_all = self.get_difference_bib()
        self.pointwise_leg = []

        no_trip_legs = len(trip.distances)
        self.leg = [[] for i in range(no_trip_legs)]
        self.pointwise_leg = [self.get_difference_bib() for i in range(no_trip_legs)]
        self.cruises_leg = [0] * no_trip_legs
        self.thermals_leg = [0] * no_trip_legs

        self.determine_phases(trip, trace)
        self.determine_point_statistics(trip, trace, trace_settings)

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

    def determine_phases(self, trip, trace):

        start_i = trace.index(trip.fixes[0])

        if trip.outlanding_fix is not None:
            last_tp_i = trace.index(trip.outlanding_fix)
        else:
            last_tp_i = trace.index(trip.fixes[-1])

        if trip.outlanding_leg() == 0:
            next_tp_i = trace.index(trip.outlanding_fix)
        else:
            next_tp_i = trace.index(trip.fixes[1])

        b_record_m1 = trace[start_i-2]
        time_m1 = det_local_time(b_record_m1, 0)

        b_record = trace[start_i-1]
        time = det_local_time(b_record, 0)
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

        self.create_entry(start_i, time_m1, 'cruise', -2)
        self.create_entry(start_i, time_m1, 'cruise', leg)

        for i in range(len(trace)):
            if start_i < i < last_tp_i:

                time_m2 = time_m1

                time_m1 = time
                bearing_m1 = bearing
                b_record_m1 = b_record

                b_record = trace[i]
                time = det_local_time(b_record, 0)

                bearing = det_bearing(b_record_m1, b_record, 'pnt', 'pnt')
                bearing_change = det_bearing_change(bearing_m1, bearing)
                bearing_change_rate = bearing_change / (time - 0.5*time_m1 - 0.5*time_m2)

                if i == next_tp_i:
                    phase = 'cruise' if cruise else 'thermal'
                    self.close_entry(i, time, leg)
                    self.create_entry(i, time, phase, leg + 1)
                    leg += 1
                    if trip.outlanding_leg() == leg:
                        next_tp_i = trace.index(trip.outlanding_fix)
                    else:
                        next_tp_i = trace.index(trip.fixes[leg+1])

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
                        thermal_start_time = det_local_time(trace[possible_thermal_start], 0)
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

                        cruise_distance = determine_distance(trace[possible_cruise_start-1], b_record,
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

        time = det_local_time(trace[last_tp_i], 0)
        self.close_entry(last_tp_i, time, -2)
        self.close_entry(last_tp_i, time, leg)

    def append_differences(self, difference_indicators, leg):
        for key, value in difference_indicators.iteritems():
            self.pointwise_all[key].append(value)
            self.pointwise_leg[leg-1][key].append(value)

    def determine_point_statistics(self, trip, trace, trace_settings):

        phase_number = 0
        leg = 0
        phase = self.all[phase_number]['phase']

        start_i = trace.index(trip.fixes[0])

        if trip.outlanding_fix is not None:
            last_tp_i = trace.index(trip.outlanding_fix)
        else:
            last_tp_i = trace.index(trip.fixes[-1])

        if trip.outlanding_leg() == 0:
            next_tp_i = trace.index(trip.outlanding_fix)
        else:
            next_tp_i = trace.index(trip.fixes[1])

        for i in range(len(trace)):
            if start_i <= i < last_tp_i:

                if self.all[phase_number]['i_end'] == i:
                    phase_number += 1
                    phase = self.all[phase_number]['phase']

                if i == next_tp_i:
                    leg += 1
                    if trip.outlanding_leg() == leg:
                        next_tp_i = trace.index(trip.outlanding_fix)
                    else:
                        next_tp_i = trace.index(trip.fixes[leg+1])

                height_difference = det_height(trace[i+1], trace_settings['gps_altitude']) -\
                                    det_height(trace[i], trace_settings['gps_altitude'])
                height = det_height(trace[i], trace_settings['gps_altitude'])
                distance = determine_distance(trace[i], trace[i+1], 'pnt', 'pnt')
                time_difference = det_local_time(trace[i+1], 0) -\
                                  det_local_time(trace[i], 0)
                time_secs = det_local_time(trace[i], 0)
                date_obj = datetime.datetime(2014, 6, 21) + datetime.timedelta(seconds=time_secs)

                difference_indicators = {'height_difference': height_difference,
                                         'height': height,
                                         'distance': distance,
                                         'time_difference': time_difference,
                                         'time': date_obj,
                                         'phase': phase}

                self.append_differences(difference_indicators, leg+1)

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
