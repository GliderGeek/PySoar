class Performance(object):
    def __init__(self, competition_day):
        self.perf_dict = {}
        self.perf_dict_names = {}
        self.perf_dict_format = {}
        self.perf_dict_good = {}
        self.determine_performance_dictionary()

        self.all = {}
        self.leg = []

        for leg in range(competition_day.no_legs):
            self.leg[str(leg+1)] = {}

    def determine_performance(self, flight):

        phase = 0
        cruise = True if flight.phases.all[0]["phase"] == 'cruise' else False

        thermal_altitude_gain = 0
        thermal_altitude_loss = 0
        thermal_time = 0
        cruise_time = 0
        cruise_distance = 0
        leg = 1

        for i in range(flight.b_records.__len__()):

            distance = 0
            height_difference = 0

            if flight.tsk_i[0] < i <= flight.tsk_i[-1]:

                if i == flight.phases.all[phase]['i_begin']:
                    phase += 1
                    cruise = True if flight.phases.all[phase]['phase'] == 'cruise' else False

                if i == flight.tsk_i[leg]:
                    if height_difference > 0:
                        self.all['thermal_altitude_gain'] += thermal_altitude_gain
                    else:
                        self.all['thermal_altitude_loss'] += thermal_altitude_loss

                    self.leg[]
                    leg += 1

                if cruise:
                    pass
                else:  # thermal
                    pass


    def determine_point_stats(self):
        pass

    def determine_performance_dictionary(self):

        self.perf_dict['compID'] = '-'
        self.perf_dict['t_start'] = '-'
        self.perf_dict['t_finish'] = '-'
        self.perf_dict['h_start'] = '-'
        self.perf_dict['vario_gem'] = '-'
        self.perf_dict['v_glide_avg'] = '-'
        self.perf_dict['v_turn_avg'] = '-'
        self.perf_dict['s_glide_avg'] = '-'
        self.perf_dict['LD_avg'] = '-'
        self.perf_dict['s_extra'] = '-'
        self.perf_dict['xc_v'] = '-'
        self.perf_dict['airplane'] = '-'
        self.perf_dict['ranking'] = '-'
        self.perf_dict['turn_percentage'] = '-'
        self.perf_dict['s_flown_task'] = '-'
        self.perf_dict['h_loss_turn'] = '-'

        self.perf_dict_names['t_start'] = 'Start time:'
        self.perf_dict_names['ranking'] = 'Ranking'
        self.perf_dict_names['airplane'] = 'Airplane:'
        self.perf_dict_names['comp_ID'] = 'Callsign:'
        self.perf_dict_names['t_finish'] = 'Finish time:'
        self.perf_dict_names['h_start'] = 'Start height[m]:'
        self.perf_dict_names['vario_gem'] = 'Average rate of climb[m/s]:'
        self.perf_dict_names['v_glide_avg'] = 'Average cruise speed (GS)[km/h]:'
        self.perf_dict_names['v_turn_avg'] = 'Speed during turning (GS)[km/h]'
        self.perf_dict_names['s_glide_avg'] = 'Average cruise distance[km]:'
        self.perf_dict_names['LD_avg'] = 'Average L/D:'
        self.perf_dict_names['s_extra'] = 'Excess distance covered[%]:'
        self.perf_dict_names['xc_v'] = 'XC speed[km/h]:'
        self.perf_dict_names['turn_percentage'] = 'Percentage turning[%]:'
        self.perf_dict_names['s_flown_task'] = 'Distance covered from task[km]:'
        self.perf_dict_names['h_loss_turn'] = 'Height lost during circling[%]'

        self.perf_dict_format['t_start'] = 'text'
        self.perf_dict_format['ranking'] = 'int'
        self.perf_dict_format['airplane'] = 'text'
        self.perf_dict_format['comp_ID'] = 'text'
        self.perf_dict_format['t_finish'] = 'text'
        self.perf_dict_format['h_start'] = 'number'
        self.perf_dict_format['vario_gem'] = 'number'
        self.perf_dict_format['v_glide_avg'] = 'number'
        self.perf_dict_format['v_turn_avg'] = 'number'
        self.perf_dict_format['s_glide_avg'] = 'number'
        self.perf_dict_format['LD_avg'] = 'number'
        self.perf_dict_format['s_extra'] = 'number'
        self.perf_dict_format['xc_v'] = 'number'
        self.perf_dict_format['turn_percentage'] = 'number'
        self.perf_dict_format['s_flown_task'] = 'number'
        self.perf_dict_format['h_loss_turn'] = 'number'

        self.perf_dict_good['ranking'] = 'neutral'
        self.perf_dict_good['t_start'] = 'neutral'
        self.perf_dict_good['t_finish'] = 'neutral'
        self.perf_dict_good['airplane'] = 'neutral'
        self.perf_dict_good['comp_ID'] = 'neutral'
        self.perf_dict_good['h_start'] = 'high'
        self.perf_dict_good['vario_gem'] = 'high'
        self.perf_dict_good['v_glide_avg'] = 'high'
        self.perf_dict_good['v_turn_avg'] = 'low'
        self.perf_dict_good['s_glide_avg'] = 'high'
        self.perf_dict_good['LD_avg'] = 'high'
        self.perf_dict_good['s_extra'] = 'low'
        self.perf_dict_good['xc_v'] = 'high'
        self.perf_dict_good['turn_percentage'] = 'low'
        self.perf_dict_good['s_flown_task'] = 'high'
        self.perf_dict_good['h_loss_turn'] = 'low'


if __name__ == '__main__':
    from main import run

    run()
