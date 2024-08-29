import datetime
import xlwt
from opensoar.utilities.helper_functions import add_times


def ss2hhmmss(time_ss, colon=True):
    if time_ss is None:
        return None

    seconds = (time_ss % 3600) % 60
    minutes = ((time_ss % 3600) - seconds) / 60
    hours = (time_ss - (time_ss % 3600)) / 3600

    if colon:
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    else:
        return "%02d%02d%02d" % (hours, minutes, seconds)


class ExcelExport(object):

    def initiate_style_dict(self):
        self.style_dict['text'] = xlwt.easyxf('font: name Times New Roman')
        self.style_dict['text_best'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour light_green')
        self.style_dict['text_worst'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour rose')

        self.style_dict['number'] = xlwt.easyxf('font: name Times New Roman, bold off', num_format_str='#,##0.00')
        self.style_dict['number_best'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour light_green', num_format_str='#,##0.00')
        self.style_dict['number_worst'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour rose', num_format_str='#,##0.00')

        self.style_dict['int'] = xlwt.easyxf('font: name Times New Roman, bold off', num_format_str='#,##0.')
        self.style_dict['int_best'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour light_green', num_format_str='#,##0.')
        self.style_dict['int_worst'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour rose', num_format_str='#,##0.')

        self.style_dict['style_phase'] = xlwt.easyxf('font: name Arial, bold on; pattern: pattern solid, fore_colour yellow; align: horiz center')
        self.style_dict['performance_names'] = xlwt.easyxf('font: name Arial, bold on; align: rotation 90, horiz center')
        self.style_dict['units'] = xlwt.easyxf('font: name Arial, bold on; align: horiz center')

    def initiate_labels(self, settings):
        for perf_ind in settings.perf_indic_all:
            self.labels_all.append(settings.perf_dict[perf_ind]["name"])
            if settings.perf_dict[perf_ind]["visible_on_leg"]:
                self.labels_leg.append(settings.perf_dict[perf_ind]["name"])

    def fill_best_worst_bib(self, leg, settings):
        for perf_ind in settings.perf_indic_all:

            if leg != -1 and not settings.perf_dict[perf_ind]["visible_on_leg"]:
                continue

            if leg == -1:
                self.best_parameters_all[perf_ind] = ""
                self.worst_parameters_all[perf_ind] = ""
            else:
                self.best_parameters_leg[leg][perf_ind] = ""
                self.worst_parameters_leg[leg][perf_ind] = ""

    def initiate_best_worst(self, settings, no_legs):
        self.fill_best_worst_bib(-1, settings)
        for leg in range(no_legs):
            self.best_parameters_leg.append({})
            self.worst_parameters_leg.append({})

            self.fill_best_worst_bib(leg, settings)

    def __init__(self, settings, no_legs):
        self.file_name = settings.file_name

        self.wb = xlwt.Workbook(encoding='latin-1')  # initialize excel sheet
        self.ws_all = self.wb.add_sheet('Entire Flight', cell_overwrite_ok=True)
        self.ws_legs = []
        for leg in range(no_legs):
            self.ws_legs.append(self.wb.add_sheet("Leg " + str(leg+1), cell_overwrite_ok=True))

        self.style_dict = {}
        self.initiate_style_dict()

        self.labels_all = []
        self.labels_leg = []
        self.initiate_labels(settings)

        # store filenames corresponding to perf indicators
        self.best_parameters_all = {}
        self.best_parameters_leg = []
        self.worst_parameters_all = {}
        self.worst_parameters_leg = []
        self.initiate_best_worst(settings, no_legs)

    def determine_best_worst(self, competition_day, settings):
        for perf_ind in settings.perf_indic_all:

            order = settings.perf_dict[perf_ind]["order"]

            if order == 'neutral':
                continue

            temp_best = 0
            temp_worst = 0

            for competitor in competition_day.competitors:

                if not settings.perf_dict[perf_ind]["visible_on_entire_flight"]:  # continue to next performance indicator
                    continue

                if competitor.trip.outlanded():
                    continue

                if competitor.performance.no_thermals == 0 and not settings.perf_dict[perf_ind]["visible_only_cruise"]:
                    continue

                value = competitor.performance.all[perf_ind]
                filename = competitor.competition_id

                # initiate values
                if (order == 'high' or order == 'low') and temp_best == 0:
                    temp_best = value
                    temp_worst = value
                    self.best_parameters_all[perf_ind] = filename
                    self.worst_parameters_all[perf_ind] = filename

                # check for best value
                if order == "high" and value is not None and (value > temp_best or (value < 0 and value < temp_best)):
                    temp_best = value
                    self.best_parameters_all[perf_ind] = filename
                elif order == "low" and value is not None and value < temp_best:
                    temp_best = value
                    self.best_parameters_all[perf_ind] = filename

                # check for worst value
                if order == 'high' and value is not None and 0 < value < temp_worst:
                    temp_worst = value
                    self.worst_parameters_all[perf_ind] = filename
                elif order == "low" and value is not None and value > temp_worst:
                    temp_worst = value
                    self.worst_parameters_all[perf_ind] = filename

            if not settings.perf_dict[perf_ind]["visible_on_leg"]:  # continue to next performance indicator
                continue

            for leg in range(competition_day.task.no_legs):

                temp_best = 0
                temp_worst = 0

                for competitor in competition_day.competitors:

                    if competitor.trip.outlanded() and competitor.trip.outlanding_leg() < leg:
                        continue
                    elif competitor.trip.outlanded()\
                            and competitor.trip.outlanding_leg() == leg\
                            and not settings.perf_dict[perf_ind]["visible_on_outlanding"]:
                        continue

                    if competitor.performance.no_thermals_leg[leg] == 0 and not settings.perf_dict[perf_ind]["visible_only_cruise"]:
                        continue

                    value = competitor.performance.leg[leg][perf_ind]
                    filename = competitor.competition_id

                    if (order == 'high' or order == 'low') and temp_best == 0:
                        temp_best = value if value is not None else 0
                        temp_worst = value if value is not None else 0
                        self.best_parameters_leg[leg][perf_ind] = filename
                        self.worst_parameters_leg[leg][perf_ind] = filename

                    # check for best value

                    if value is not None:
                        if order == "high" and (value > temp_best or (value < 0 and value < temp_best)):
                            temp_best = value
                            self.best_parameters_leg[leg][perf_ind] = filename
                        elif order == "low" and value < temp_best:
                            temp_best = value
                            self.best_parameters_leg[leg][perf_ind] = filename

                        # check for worst value
                        if order == 'high' and 0 < value < temp_worst:
                            temp_worst = value
                            self.worst_parameters_leg[leg][perf_ind] = filename
                        elif order == "low" and value > temp_worst:
                            temp_worst = value
                            self.worst_parameters_leg[leg][perf_ind] = filename

    def write_general_info(self, date):
        self.ws_all.write(0, 0, date.strftime('%d-%m-%y'))

    def write_cell(self, leg, row, col, content, style):
        if leg == -1:
            self.ws_all.write(row, col, content, style)
        else:
            self.ws_legs[leg].write(row, col, content, style)

    def style_addition(self, leg, perf_ind, filename):
        if leg == -1:
            if self.best_parameters_all[perf_ind] == filename:
                return "_best"
            elif self.worst_parameters_all[perf_ind] == filename:
                return "_worst"
            else:
                return ""
        else:
            if self.best_parameters_leg[leg][perf_ind] == filename:
                return "_best"
            elif self.worst_parameters_leg[leg][perf_ind] == filename:
                return "_worst"
            else:
                return ""

    def write_perf_indics(self, leg, settings, competition_day):
        col = 0
        for perf_ind in settings.perf_indic_all:

            if leg != -1 and not settings.perf_dict[perf_ind]["visible_on_leg"]:
                continue

            if leg == -1 and not settings.perf_dict[perf_ind]["visible_on_entire_flight"]:
                continue

            row = 1
            content = settings.perf_dict[perf_ind]['name']
            style = self.style_dict['performance_names']
            perf_format = settings.perf_dict[perf_ind]['format']
            self.write_cell(leg, row, col, content, style)

            row += 1
            content = settings.perf_dict[perf_ind]['unit']
            style = self.style_dict['units']
            perf_format = settings.perf_dict[perf_ind]['format']
            self.write_cell(leg, row, col, content, style)

            row += 1  # empty line

            for competitor in competition_day.competitors:
                row += 1

                if leg == -1:
                    if competitor.trip.outlanded() and not settings.perf_dict[perf_ind]["visible_on_outlanding"]\
                            or competitor.performance.no_thermals == 0 and not settings.perf_dict[perf_ind]["visible_only_cruise"]:
                        continue
                    else:
                        if perf_ind == 'ranking':
                            content = competitor.ranking
                        elif perf_ind == 'airplane':
                            content = competitor.plane_model
                        elif perf_ind == 'compID':
                            content = competitor.competition_id
                        else:
                            content = competitor.performance.all[perf_ind]
                else:
                    if competitor.trip.outlanded() and competitor.trip.outlanding_leg() < leg or\
                        competitor.trip.outlanded() and competitor.trip.outlanding_leg() <= leg and not settings.perf_dict[perf_ind]["visible_on_outlanding"] or\
                                            competitor.performance.no_thermals_leg[leg] == 0 and not settings.perf_dict[perf_ind]["visible_only_cruise"]:
                        continue
                    else:
                        if perf_ind == 'ranking':
                            content = competitor.ranking
                        elif perf_ind == 'airplane':
                            content = competitor.plane_model
                        elif perf_ind == 'compID':
                            content = competitor.competition_id
                        else:
                            content = competitor.performance.leg[leg][perf_ind]

                if perf_ind in ['t_start', 't_finish']:
                    content = content.strftime('%H:%M:%S')

                style = self.style_dict[perf_format + self.style_addition(leg, perf_ind, competitor.competition_id)]
                self.write_cell(leg, row, col, content, style)

            col += 1

    def write_title(self, leg, settings, taskpoints):
        row = 0
        col = 1

        if leg == -1:
            no_cols = settings.no_indicators
            title = "Entire flight"
            self.ws_all.write_merge(row, row, col, col+no_cols, title, self.style_dict['style_phase'])
        else:
            no_cols = settings.no_leg_indicators
            title = "Leg %s: %s - %s" % (leg + 1, taskpoints[leg].name, taskpoints[leg+1].name)
            self.ws_legs[leg].write_merge(row, row, col, col+no_cols, title, self.style_dict['style_phase'])

    def write_whole_flight(self, settings, competition_day):
        self.write_title(-1, settings, competition_day.task.waypoints)
        self.write_perf_indics(-1, settings, competition_day)

    def write_legs(self, settings, competition_day):
        for leg in range(competition_day.task.no_legs):
            self.write_title(leg, settings, competition_day.task.waypoints)
            self.write_perf_indics(leg, settings, competition_day)

    def write_file(self, competition_day, settings, igc_directory):

        self.write_general_info(competition_day.date)
        self.determine_best_worst(competition_day, settings)
        self.write_whole_flight(settings, competition_day)
        self.write_legs(settings, competition_day)

        self.wb.save(self.file_name)
        self.wb.save(igc_directory +('/')+self.file_name.split('/')[-1])


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
