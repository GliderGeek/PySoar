from generalFunctions import det_height, ss2hhmmss, determine_distance


class Performance(object):
    def __init__(self, competition_day, flight):

        self.tsk_distance_all = sum(competition_day.task_distances)
        self.tsk_distance_leg = competition_day.task_distances

        self.no_cruises = flight.phases.cruises_all
        self.no_cruises_leg = flight.phases.cruises_leg

        self.no_thermals = flight.phases.thermals_all
        self.no_thermals_leg = flight.phases.thermals_leg

        startheight = det_height(flight.b_records[flight.tsk_i[0]], flight.gps_altitude)

        if flight.outlanded:
            s_flown_task_all = 0
            for leg in range(flight.outlanding_leg):
                s_flown_task_all += competition_day.task_distances[leg]
            s_flown_task_all += flight.outlanding_distance
            s_flown_task_all /= 1000
        else:
            s_flown_task_all = sum(competition_day.task_distances) / 1000

        self.all = {"ranking": flight.ranking,
                    "airplane": flight.airplane,
                    "compID": flight.competition_id,
                    "t_start": ss2hhmmss(flight.tsk_t[0]),
                    "t_finish": ss2hhmmss(flight.tsk_t[-1]),
                    "h_start": startheight,
                    "s_flown_task": s_flown_task_all}

        self.leg = []

        # in case of outlanding: only performance is stored from completed legs
        for leg in range(competition_day.no_legs):
            if flight.outlanded and leg == flight.outlanding_leg:
                t_start = flight.tsk_t[leg]
                t_finish = 0
                s_flown_task_leg = flight.outlanding_distance / 1000
            elif flight.outlanded and leg > flight.outlanding_leg:
                t_start = 0
                t_finish = 0
                s_flown_task_leg = 0
            else:
                t_start = flight.tsk_t[leg]
                t_finish = flight.tsk_t[leg+1]
                s_flown_task_leg = competition_day.task_distances[leg] / 1000
            self.leg.append({"ranking": self.all["ranking"],
                             "airplane": self.all["airplane"],
                             "compID": self.all["compID"],
                             "t_start": ss2hhmmss(t_start),
                             "t_finish": ss2hhmmss(t_finish),
                             "s_flown_task": s_flown_task_leg})

    def store_perf(self, leg, key, value):
        if leg == -1:
            self.all[key] = value
        else:
            self.leg[leg][key] = value

    def det_vario_gem(self, leg, thermal_time, thermal_altitude_loss, thermal_altitude_gain):
        if thermal_time == 0:
            vario_gem = 0
        else:
            vario_gem = float(thermal_altitude_loss + thermal_altitude_gain) / thermal_time
        self.store_perf(leg, "vario_gem", vario_gem)

    def det_v_glide_avg(self, leg, cruise_distance, cruise_time):
        # returns the average speed during cruise in kmh
        if cruise_time == 0:
            v_glide_avg = 42
        else:
            v_glide_avg = float(cruise_distance) / cruise_time
        self.store_perf(leg, "v_glide_avg", v_glide_avg * 3.6)

    def det_v_turn_avg(self, leg, thermal_distance, thermal_time):
        # returns the average speed during thermal in kmh
        if thermal_time == 0:
            v_turn_avg = 0
        else:
            v_turn_avg = float(thermal_distance) / thermal_time
        self.store_perf(leg, "v_turn_avg", v_turn_avg * 3.6)

    def det_LD_avg(self, leg, cruise_distance, cruise_height_diff):
        if cruise_height_diff == 0:
            LD_avg = 42
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
            h_loss_turn = 42
        else:
            h_loss_turn = float(abs(thermal_altitude_loss)) / (abs(thermal_altitude_loss) + abs(thermal_altitude_gain))
            h_loss_turn *= 100
        self.store_perf(leg, "h_loss_turn", h_loss_turn)

    def det_s_glide_avg(self, leg, cruise_distance, no_cruises):
        # return the average cruise distance in kms
        if no_cruises == 0:
            s_glide_avg = 42
        else:
            s_glide_avg = float(cruise_distance) / no_cruises
        self.store_perf(leg, "s_glide_avg", s_glide_avg / 1000)

    def det_s_extra(self, leg, cruise_distance, task_distance, thermal_drift):
        s_extra = float(cruise_distance + thermal_drift - task_distance) / task_distance
        s_extra *= 100
        self.store_perf(leg, "s_extra", s_extra)

    def det_xc_v(self, leg, task_distance, thermal_time, cruise_time):
        # return the cross country speed in kmh
        if (thermal_time + cruise_time) == 0:
            xc_v = 42
        else:
            xc_v = float(task_distance) / (thermal_time + cruise_time)
        self.store_perf(leg, "xc_v", xc_v * 3.6)

    def write_perfs(self, leg,
                    thermal_altitude_gain, thermal_altitude_loss, thermal_time, thermal_distance, thermal_drift,
                    cruise_time, cruise_distance, cruise_height_diff):

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
        self.det_v_glide_avg(leg, cruise_distance, cruise_time)
        self.det_xc_v(leg, task_distance, thermal_time, cruise_time)

    def determine_performance(self, flight, competitionday):

        thermal_altitude_gain_tot = 0
        thermal_altitude_loss_tot = 0
        thermal_time_tot = 0
        thermal_distance_tot = 0
        thermal_drift_tot = 0
        cruise_time_tot = 0
        cruise_distance_tot = 0
        cruise_height_diff_tot = 0

        for leg in range(competitionday.no_legs):

            thermal_altitude_gain = 0
            thermal_altitude_loss = 0
            thermal_time = 0
            thermal_distance = 0
            thermal_drift = 0
            cruise_time = 0
            cruise_distance = 0
            cruise_height_diff = 0

            for point in range(len(flight.phases.pointwise_leg[leg]['phase'])):

                leg_pointwise = flight.phases.pointwise_leg[leg]
                cruise = True if leg_pointwise["phase"][point] == 'cruise' else False

                if cruise:
                    cruise_time += leg_pointwise["time_difference"][point]
                    cruise_distance += leg_pointwise["distance"][point]
                    cruise_height_diff += leg_pointwise["height_difference"][point]
                else:
                    thermal_time += leg_pointwise["time_difference"][point]
                    thermal_distance += leg_pointwise["distance"][point]
                    if leg_pointwise["height_difference"][point] > 0:
                        thermal_altitude_gain += leg_pointwise["height_difference"][point]
                    else:
                        thermal_altitude_loss += leg_pointwise["height_difference"][point]

            for entry in flight.phases.leg[leg]:
                if entry["phase"] == "thermal":
                    i_st = entry["i_start"]
                    i_end = entry["i_end"]
                    thermal_drift += determine_distance(flight.b_records[i_st], flight.b_records[i_end], 'pnt', 'pnt')

            # write to total performance values
            thermal_altitude_gain_tot += thermal_altitude_gain
            thermal_altitude_loss_tot += thermal_altitude_loss
            thermal_time_tot += thermal_time
            thermal_distance_tot += thermal_distance
            thermal_drift_tot += thermal_drift
            cruise_time_tot += cruise_time
            cruise_distance_tot += cruise_distance
            cruise_height_diff_tot += cruise_height_diff

            self.write_perfs(leg,
                             thermal_altitude_gain, thermal_altitude_loss, thermal_time, thermal_distance, thermal_drift,
                             cruise_time, cruise_distance, cruise_height_diff)
        self.write_perfs(-1,
                         thermal_altitude_gain_tot, thermal_altitude_loss_tot, thermal_time_tot, thermal_distance_tot, thermal_drift_tot,
                         cruise_time_tot, cruise_distance_tot, cruise_height_diff_tot)


if __name__ == '__main__':
    from main_pysoar import run

    run()
