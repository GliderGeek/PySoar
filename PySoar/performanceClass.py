from opensoar.task.aat import AAT
from opensoar.utilities.helper_functions import calculate_distance, \
    seconds_time_difference_fixes, total_distance_travelled, height_difference_fixes, altitude_gain_and_loss, \
    seconds_time_difference


class Performance(object):
    df_categories = ['t_start', 't_finish', 'h_start', 'h_finish', 's_flown_task', 'vario_gem', 'v_glide_avg',
                     'v_turn_avg', 'LD_avg', 'turn_percentage', 'h_loss_turn', 's_glide_avg', 'dh_cruise_avg',
                     's_extra', 'tsk_v']

    def __init__(self, task, trip, phases, gps_altitude):

        self.all = None
        self.leg = None

        self.tsk_distance_all = sum(trip.distances)
        self.tsk_distance_leg = trip.distances

        # why not use phases directly? pass in functions as argument?
        self.no_cruises_leg = [len(phases.cruises(leg)) for leg in range(trip.started_legs())]
        self.no_cruises = len(phases.cruises(leg='all'))
        self.no_thermals_leg = [len(phases.thermals(leg)) for leg in range(trip.started_legs())]
        self.no_thermals = len(phases.thermals(leg='all'))

        self.init_all(trip, gps_altitude)
        self.init_leg(trip, gps_altitude)

        self.determine_performance(task, trip, phases, gps_altitude)

    def init_all(self, trip, gps_altitude):
        start_h = trip.fixes[0]['gps_alt'] if gps_altitude else trip.fixes[0]['pressure_alt']
        start_t = trip.refined_start_time

        if len(trip.fixes) == 1:
            finish_h = None
            finish_t = None
        else:
            finish_h = trip.fixes[-1]['gps_alt'] if gps_altitude else trip.fixes[-1]['pressure_alt']
            finish_t = trip.fixes[-1]['time']

        s_flown_task_all = sum(trip.distances) / 1000

        self.all = {"t_start": start_t,
                    "t_finish": finish_t,
                    "h_start": start_h,
                    "h_finish": finish_h,
                    "s_flown_task": s_flown_task_all}

    def init_leg(self, trip, gps_altitude):
        leg_values = []

        for leg in range(len(trip.distances)):
            if trip.outlanding_fix is not None and leg == trip.outlanding_leg():
                start_h = trip.fixes[leg]['gps_alt'] if gps_altitude else trip.fixes[leg]['pressure_alt']
                start_t = trip.refined_start_time if leg == 0 else trip.fixes[leg]['time']

                finish_t = 0
                finish_h = 0

                s_flown_task_leg = trip.distances[-1] / 1000
            elif trip.outlanding_fix is not None and leg > trip.outlanding_leg():
                start_t = 0
                start_h = 0

                finish_t = 0
                finish_h = 0

                s_flown_task_leg = 0
            else:
                start_h = trip.fixes[leg]['gps_alt'] if gps_altitude else trip.fixes[leg]['pressure_alt']
                start_t = trip.refined_start_time if leg == 0 else trip.fixes[leg]['time']

                finish_t = trip.fixes[leg+1]['time']
                finish_h = trip.fixes[leg+1]['gps_alt'] if gps_altitude else trip.fixes[leg+1]['pressure_alt']

                s_flown_task_leg = trip.distances[leg] / 1000

            leg_values.append({"t_start": start_t,
                         "t_finish": finish_t,
                         "h_start": start_h,
                         "h_finish": finish_h,
                         "s_flown_task": s_flown_task_leg})

        self.leg = leg_values

    def store_perf(self, leg, key, value):
        if key not in self.df_categories:
            raise ValueError('This performance category is not supported')

        if leg == -1:
            self.all[key] = value
        else:
            self.leg[leg][key] = value

    def det_vario_gem(self, leg, thermal_time, thermal_altitude_loss, thermal_altitude_gain):
        if thermal_time == 0:
            vario_gem = 0
        else:
            vario_gem = float(thermal_altitude_gain - thermal_altitude_loss) / thermal_time
        self.store_perf(leg, "vario_gem", vario_gem)

    def det_v_glide_avg(self, leg, cruise_distance, cruise_time):
        # returns the average speed during cruise in kmh
        if cruise_time == 0:
            v_glide_avg = None
        else:
            v_glide_avg = float(cruise_distance) / cruise_time
            v_glide_avg *= 3.6
        self.store_perf(leg, "v_glide_avg", v_glide_avg)

    def det_v_turn_avg(self, leg, thermal_distance, thermal_time):
        # returns the average speed during thermal in kmh
        if thermal_time == 0:
            v_turn_avg = 0
        else:
            v_turn_avg = float(thermal_distance) / thermal_time
        self.store_perf(leg, "v_turn_avg", v_turn_avg * 3.6)

    def det_LD_avg(self, leg, cruise_distance, cruise_height_diff):
        if cruise_height_diff == 0:
            LD_avg = None
        else:
            LD_avg = float(cruise_distance) / -cruise_height_diff
        self.store_perf(leg, "LD_avg", LD_avg)

    def det_turn_percentage(self, leg, thermal_time, cruise_time):
        if (thermal_time + cruise_time) == 0:
            turn_percentage = 0
        else:
            turn_percentage = float(thermal_time) / (thermal_time + cruise_time)
            turn_percentage *= 100
        self.store_perf(leg, "turn_percentage", turn_percentage)

    def det_h_loss_turn(self, leg, thermal_altitude_loss, thermal_altitude_gain):
        if (abs(thermal_altitude_loss) + abs(thermal_altitude_gain)) == 0:
            h_loss_turn = None
        else:
            h_loss_turn = float(abs(thermal_altitude_loss)) / (abs(thermal_altitude_loss) + abs(thermal_altitude_gain))
            h_loss_turn *= 100
        self.store_perf(leg, "h_loss_turn", h_loss_turn)

    def det_s_glide_avg(self, leg, cruise_distance, no_cruises):
        # return the average cruise distance in kms
        if no_cruises == 0:
            s_glide_avg = None
        else:
            s_glide_avg = float(cruise_distance) / no_cruises
            s_glide_avg /= 1000  # convert to km
        self.store_perf(leg, "s_glide_avg", s_glide_avg)

    def det_dh_cruise_avg(self, leg, cruise_dh, no_cruises):
        if no_cruises == 0:
            dh_cruise_avg = 0
        else:
            dh_cruise_avg = float(cruise_dh) / no_cruises
        self.store_perf(leg, "dh_cruise_avg", dh_cruise_avg)

    def det_s_extra(self, leg, cruise_distance, task_distance, thermal_drift):
        if task_distance > 0:
            s_extra = float(cruise_distance + thermal_drift - task_distance) / task_distance
            s_extra *= 100
        else:
            s_extra = None
        self.store_perf(leg, "s_extra", s_extra)

    def det_tsk_v(self, leg, task_distance, task_time):
        # return the cross country speed in kmh
        if task_time == 0:
            tsk_v = None
        else:
            tsk_v = float(task_distance) / task_time
            tsk_v *= 3.6
        self.store_perf(leg, "tsk_v", tsk_v)

    def write_perfs(self, leg,
                    thermal_altitude_gain, thermal_altitude_loss, thermal_time, thermal_distance, thermal_drift,
                    cruise_time, cruise_distance, cruise_height_diff, task_time):

        if leg == -1:
            no_cruises = self.no_cruises
            no_thermals = self.no_thermals
            task_distance = self.tsk_distance_all
        else:
            no_cruises = self.no_cruises_leg[leg]
            no_thermals = self.no_thermals_leg[leg]
            task_distance = self.tsk_distance_leg[leg]

        # implement performance column with number of thermals?
        self.det_vario_gem(leg, thermal_time, thermal_altitude_loss, thermal_altitude_gain)
        self.det_v_turn_avg(leg, thermal_distance, thermal_time)
        self.det_turn_percentage(leg, thermal_time, cruise_time)
        self.det_LD_avg(leg, cruise_distance, cruise_height_diff)
        self.det_s_extra(leg, cruise_distance, task_distance, thermal_drift)
        self.det_h_loss_turn(leg, thermal_altitude_loss, thermal_altitude_gain)
        self.det_s_glide_avg(leg, cruise_distance, no_cruises)
        self.det_dh_cruise_avg(leg, cruise_height_diff, no_cruises)
        self.det_v_glide_avg(leg, cruise_distance, cruise_time)
        self.det_tsk_v(leg, task_distance, task_time)

    def determine_performance(self, task, trip, phases, gps_altitude):

        thermal_altitude_gain_tot = 0
        thermal_altitude_loss_tot = 0
        thermal_time_tot = 0
        thermal_distance_tot = 0
        thermal_drift_tot = 0
        cruise_time_tot = 0
        cruise_distance_tot = 0
        cruise_height_diff_tot = 0
        task_time_tot = 0

        for leg in range(trip.completed_legs()):

            thermal_altitude_gain = 0
            thermal_altitude_loss = 0
            thermal_time = 0
            thermal_distance = 0
            thermal_drift = 0
            cruise_time = 0
            cruise_distance = 0
            cruise_height_diff = 0
            task_time = 0

            for i, phase in enumerate(phases.all_phases(leg)):

                # take refined start
                if leg == 0 and i == 0:
                    phase_duration = seconds_time_difference(trip.refined_start_time, phase.fixes[-1]['time'])
                else:
                    phase_duration = seconds_time_difference_fixes(phase.fixes[0], phase.fixes[-1])

                phase_distance_traveled = total_distance_travelled(phase.fixes)

                task_time += phase_duration
                if phase.is_cruise:
                    cruise_time += phase_duration
                    cruise_distance += phase_distance_traveled
                    cruise_height_diff += height_difference_fixes(phase.fixes[0], phase.fixes[-1], gps_altitude)
                else:
                    thermal_time += phase_duration
                    thermal_distance += phase_distance_traveled
                    gain, loss = altitude_gain_and_loss(phase.fixes, gps_altitude)
                    thermal_altitude_gain += gain
                    thermal_altitude_loss += loss
                    thermal_drift += calculate_distance(phase.fixes[0], phase.fixes[-1])

            # write to total performance values
            thermal_altitude_gain_tot += thermal_altitude_gain
            thermal_altitude_loss_tot += thermal_altitude_loss
            thermal_time_tot += thermal_time
            thermal_distance_tot += thermal_distance
            thermal_drift_tot += thermal_drift
            cruise_time_tot += cruise_time
            cruise_distance_tot += cruise_distance
            cruise_height_diff_tot += cruise_height_diff
            task_time_tot += task_time

            self.write_perfs(leg,
                             thermal_altitude_gain, thermal_altitude_loss, thermal_time, thermal_distance, thermal_drift,
                             cruise_time, cruise_distance, cruise_height_diff, task_time)

        if isinstance(task, AAT) and task_time_tot < task.t_min:
            task_time_tot = task.t_min

        self.write_perfs(-1,
                         thermal_altitude_gain_tot, thermal_altitude_loss_tot, thermal_time_tot, thermal_distance_tot, thermal_drift_tot,
                         cruise_time_tot, cruise_distance_tot, cruise_height_diff_tot, task_time_tot)

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
