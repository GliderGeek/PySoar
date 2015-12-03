class Settings(object):

    def set_performance_entry(self, key, name, _format, order):
        self.perf_dict[key] = {"name": name, "format": _format, "order": order}

    def determine_performance_dictionary(self):
        self.set_performance_entry("ranking",           "Ranking",                      "int",      "neutral")
        self.set_performance_entry("airplane",          "Airplane",                     "text",     "neutral")
        self.set_performance_entry("compID",            "Callsign",                     "text",     "neutral")
        self.set_performance_entry("t_start",           "Start time",                   "text",     "neutral")
        self.set_performance_entry("t_finish",          "Finish time",                  "text",     "neutral")
        self.set_performance_entry("h_start",           "Start height",                 "number",   "high")
        self.set_performance_entry("vario_gem",         "Average rate of climb",        "number",   "high")
        self.set_performance_entry("v_glide_avg",       "Average cruise speed (GS)",    "number",   "high")
        self.set_performance_entry("v_turn_avg",        "Speed during turning (GS)",    "number",   "low")
        self.set_performance_entry("s_glide_avg",       "Average cruise distance",      "number",   "high")
        self.set_performance_entry("LD_avg",            "Average L/D",                  "number",   "high")
        self.set_performance_entry("s_extra",           "Excess distance covered",      "number",   "low")
        self.set_performance_entry("xc_v",              "XC speed",                     "number",   "high")
        self.set_performance_entry("turn_percentage",   "Percentage turning",           "number",   "low")
        self.set_performance_entry("s_flown_task",      "Distance covered from task",   "number",   "neutral")
        self.set_performance_entry("h_loss_turn",       "Height lost during circling",  "number",   "low")

    def __init__(self):
        import platform

        stand_alone_build = True

        self.version = 0.70
        self.file_name = 'Analysis_PySoar.xls'
        if platform.system() == 'Darwin' and stand_alone_build:
            self.file_name = '../../../Analysis_PySoar.xls'

        self.perf_dict = {}
        self.determine_performance_dictionary()

    turn_threshold_bearingRate = 6
    turn_threshold_bearingTot = 200

    glide_threshold_dist = 400
    glide_threshold_bearingRateAvg = 2
    glide_threshold_bearingRate = 6

    perf_indic_all = ["ranking", "airplane", "compID", "s_flown_task", "t_start", "t_finish", "h_start", "vario_gem",
                      "v_glide_avg", "v_turn_avg", "s_glide_avg", "LD_avg", "s_extra", "xc_v",
                      "turn_percentage", "h_loss_turn"]

    exclude_perf_indic_leg = ["h_start"]  # performance indicators which are not shown on legs
    perf_indic_outland = ["ranking", "airplane", "compID", "s_flown_task", "h_start", "t_start", "h_start"]

    thermal_indicators = ["vario_gem", "v_turn_avg", "h_loss_turn"]  # perf_indicators which should be disabled when only cruise

    earth_radius = 6371

if __name__ == '__main__':
    from main_pysoar import run
    run()
