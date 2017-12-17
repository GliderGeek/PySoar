import os
import sys


class Settings(object):

    def set_performance_entry(self, key, name, _format, order, unit, visible_only_cruise, visible_on_outlanding, visible_on_leg, visible_on_flight):
        self.perf_dict[key] = {"name": name, "format": _format, "order": order, "unit": unit,
                               "visible_only_cruise": visible_only_cruise,
                               "visible_on_outlanding": visible_on_outlanding,
                               "visible_on_leg": visible_on_leg,
                               "visible_on_entire_flight": visible_on_flight}

    def determine_performance_dictionary(self):
        self.set_performance_entry("ranking",           "Ranking",                      "int",      "neutral", "", True, True, True, True)
        self.set_performance_entry("airplane",          "Airplane",                     "text",     "neutral", "", True, True, True, True)
        self.set_performance_entry("compID",            "Callsign",                     "text",     "neutral", "", True, True, True, True)
        self.set_performance_entry("t_start",           "Start time",                   "text",     "neutral", "[local time]", True, True, True, True)
        self.set_performance_entry("t_finish",          "Finish time",                  "text",     "neutral", "[local time]", True, False, True, True)
        self.set_performance_entry("h_start",           "Start height",                 "number",   "high", "[m]", True, True, True, True)
        self.set_performance_entry("h_finish",          "Finish height",                "number",   "high", "[m]", True, False, True, False)
        self.set_performance_entry("vario_gem",         "Average rate of climb",        "number",   "high", "[m/s]", False, False, True, True)
        self.set_performance_entry("v_glide_avg",       "Average cruise speed (GS)",    "number",   "high", "[km/h]", True, False, True, True)
        self.set_performance_entry("v_turn_avg",        "Average thermal speed (GS)",   "number",   "low", "[km/h]", False, False, True, True)
        self.set_performance_entry("s_glide_avg",       "Average cruise distance",      "number",   "high", "[km]", True, False, True, True)
        self.set_performance_entry("dh_cruise_avg",     "Average cruise height difference",      "number",   "low", "[m]", True, False, True, True)
        self.set_performance_entry("LD_avg",            "Average L/D",                  "number",   "high", "[-]", True, False, True, True)
        self.set_performance_entry("s_extra",           "Excess distance covered",      "number",   "low", "[%]", True, False, True, True)
        self.set_performance_entry("tsk_v",              "Task speed",                   "number",   "high", "[km/h]", True, False, True, True)
        self.set_performance_entry("turn_percentage",   "Percentage turning",           "number",   "low", "[%]", False, False, True, True)
        self.set_performance_entry("s_flown_task",      "Distance covered from task",   "number",   "neutral", "[km]", True, True, True, True)
        self.set_performance_entry("h_loss_turn",       "Height loss during circling",  "number",   "low", "[%]", False, False, True, True)

    def __init__(self):
        import platform

        self.debugging = True
        self.debug_form_url = 'https://docs.google.com/forms/d/1uWxTA5Hka6rbXzDOJDX9dRhZ7OwIoqN5Do0e27B0q-M/viewform'
        self.pysoar_version_formID = 891402426
        self.competition_url_formID = 174131444
        self.version = '0.56.2'

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
    cruise_threshold_bearingRate = 4 #degr/s
    cruise_threshold_bearingTot = 225 #degr

    # thresholds while in thermal
    thermal_threshold_distance = 1000 #m
    thermal_threshold_bearingRateAvg = 2 #degr/s
    thermal_threshold_bearingRate = 4 #degr/s

    perf_indic_all = ["ranking", "airplane", "compID", "s_flown_task", "t_start", "t_finish", "h_start", "h_finish",
                      "vario_gem", "v_glide_avg", "v_turn_avg", "s_glide_avg", "dh_cruise_avg", "LD_avg", "s_extra", "tsk_v",
                      "turn_percentage", "h_loss_turn"]

    ENL_value_threshold = 500  # above which it is seen as engine noise
    ENL_time_threshold = 30  # seconds

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
