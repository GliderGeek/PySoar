import os
import sys


class Settings(object):

    def set_performance_entry(self, key, name, _format, order, unit, visible_only_cruise, visible_on_outlanding, visible_on_leg):
        self.perf_dict[key] = {"name": name, "format": _format, "order": order, "unit": unit,
                               "visible_only_cruise": visible_only_cruise,
                               "visible_on_outlanding": visible_on_outlanding,
                               "visible_on_leg": visible_on_leg}

    def determine_performance_dictionary(self):
        self.set_performance_entry("ranking",           "Ranking",                      "int",      "neutral", "", True, True, True)
        self.set_performance_entry("airplane",          "Airplane",                     "text",     "neutral", "", True, True, True)
        self.set_performance_entry("compID",            "Callsign",                     "text",     "neutral", "", True, True, True)
        self.set_performance_entry("t_start",           "Start time",                   "text",     "neutral", "[local time]", True, True, True)
        self.set_performance_entry("t_finish",          "Finish time",                  "text",     "neutral", "[local time]", True, False, True)
        self.set_performance_entry("h_start",           "Start height",                 "number",   "high", "[m]", True, True, False)
        self.set_performance_entry("vario_gem",         "Average rate of climb",        "number",   "high", "[m/s]", False, False, True)
        self.set_performance_entry("v_glide_avg",       "Average cruise speed (GS)",    "number",   "high", "[km/h]", True, False, True)
        self.set_performance_entry("v_turn_avg",        "Average thermal speed (GS)",   "number",   "low", "[km/h]", False, False, True)
        self.set_performance_entry("s_glide_avg",       "Average cruise distance",      "number",   "high", "[km]", True, False, True)
        self.set_performance_entry("LD_avg",            "Average L/D",                  "number",   "high", "[-]", True, False, True)
        self.set_performance_entry("s_extra",           "Excess distance covered",      "number",   "low", "[%]", True, False, True)
        self.set_performance_entry("xc_v",              "XC speed",                     "number",   "high", "[km/h]", True, False, True)
        self.set_performance_entry("turn_percentage",   "Percentage turning",           "number",   "low", "[%]", True, False, True)
        self.set_performance_entry("s_flown_task",      "Distance covered from task",   "number",   "neutral", "[km", True, True, True)
        self.set_performance_entry("h_loss_turn",       "Height loss during circling",  "number",   "low", "[%]", False, False, True)

    def __init__(self):
        import platform

        self.debugging = True

        self.version = 0.70

        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            self.current_dir = os.path.dirname(sys.executable)
            if platform.system() == "Darwin":
                self.current_dir += "/../../.."
        elif __file__:
            self.current_dir = os.path.dirname(__file__)

        self.file_name = self.current_dir + '/Analysis_PySoar.xls'

        self.perf_dict = {}
        self.determine_performance_dictionary()
        self.no_leg_indicators = 0
        self.no_indicators = 0
        for pi in self.perf_dict:
            self.no_indicators += 1
            if self.perf_dict[pi]["visible_on_leg"]:
                self.no_leg_indicators += 1

    # thresholds while in cruise
    cruise_threshold_bearingRate = 6
    cruise_threshold_bearingTot = 200

    # thresholds while in thermal
    thermal_threshold_distance = 400
    thermal_threshold_bearingRateAvg = 2
    thermal_threshold_bearingRate = 6

    perf_indic_all = ["ranking", "airplane", "compID", "s_flown_task", "t_start", "t_finish", "h_start",
                      "vario_gem","v_glide_avg", "v_turn_avg", "s_glide_avg", "LD_avg", "s_extra", "xc_v",
                      "turn_percentage", "h_loss_turn"]

    WGS84_mayor_axis = 6378137
    WGS84_minor_axis = 6356752.3142
    FAI_sphere_radius = 6371
    distance_method = "WGS84 elipse"  # choose between 'FAI sphere' and 'WGS84 elipse'

if __name__ == '__main__':
    from main_pysoar import run
    run()
