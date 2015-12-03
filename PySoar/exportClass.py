import xlwt


class ExcelExport(object):

    def initiate_style_dict(self):
        self.style_dict['text'] = xlwt.easyxf('font: name Times New Roman')
        self.style_dict['text_bst'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour light_green')
        self.style_dict['text_wrst'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour rose')

        self.style_dict['number'] = xlwt.easyxf('font: name Times New Roman, bold off', num_format_str='#,##0.00')
        self.style_dict['number_best'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour light_green', num_format_str='#,##0.00')
        self.style_dict['number_worst'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour rose', num_format_str='#,##0.00')

        self.style_dict['int'] = xlwt.easyxf('font: name Times New Roman, bold off', num_format_str='#,##0.')
        self.style_dict['int_best'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour light_green', num_format_str='#,##0.')
        self.style_dict['int_worst'] = xlwt.easyxf('font: name Times New Roman, bold on; pattern: pattern solid, fore_colour rose', num_format_str='#,##0.')

        self.style_dict['style_phase'] = xlwt.easyxf('font: name Arial, bold on; pattern: pattern solid, fore_colour yellow; align: horiz center')
        self.style_dict['performance_names'] = xlwt.easyxf('font: name Arial, bold on; align: rotation 90')

    def initiate_labels(self, settings, ):
        for perf_ind in settings.perf_indic_all:
            self.labels_all.append(settings.perf_dict[perf_ind]["name"])
            if perf_ind not in settings.exclude_perf_indic_leg:
                self.labels_leg.append(settings.perf_dict[perf_ind]["name"])

    def fill_best_worst_bib(self, leg, settings):
        for perf_ind in settings.perf_indic_all:

            if leg != -1 and perf_ind in settings.exclude_perf_indic_leg:
                continue

            if leg == -1:
                self.best_parameters_all[perf_ind] = ""
                self.worst_parameters_all[perf_ind] = ""
            else:
                self.best_parameters_leg[leg][perf_ind] = ""
                self.worst_parameters_leg[leg][perf_ind] = ""

    def initiate_best_worst(self, settings, competition_day):
        self.fill_best_worst_bib(-1, settings)
        for leg in range(competition_day.no_legs):
            self.best_parameters_leg.append({})
            self.worst_parameters_leg.append({})

            self.fill_best_worst_bib(leg, settings)

    def __init__(self, settings, competition_day):
        self.file_name = settings.file_name

        self.wb = xlwt.Workbook()  # initialize excel sheet
        self.ws_all = self.wb.add_sheet('Entire Flight', cell_overwrite_ok=True)
        self.ws_legs = []
        for leg in range(competition_day.no_legs):
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
        self.initiate_best_worst(settings, competition_day)

    def determine_best_worst(self, competition_day, settings):
        for perf_ind in settings.perf_indic_all:

            order = settings.perf_dict[perf_ind]["order"]

            temp_best = 0
            temp_worst = 0

            for flight in competition_day.flights:

                if flight.outlanded:
                    continue

                if flight.performance.no_thermals == 0 and perf_ind in settings.thermal_indicators:
                    continue

                value = flight.performance.all[perf_ind]
                filename = flight.file_name

                # initiate values
                if (order == 'high' or order == 'low') and temp_best == 0:
                    temp_best = value
                    temp_worst = value
                    self.best_parameters_all[perf_ind] = filename
                    self.worst_parameters_all[perf_ind] = filename

                # check for best value
                if order == "high" and (value > temp_best or (value < 0 and value < temp_best)):
                    temp_best = value
                    self.best_parameters_all[perf_ind] = filename
                elif order == "low" and value < temp_best:
                    temp_best = value
                    self.best_parameters_all[perf_ind] = filename

                # check for worst value
                if order == 'high' and 0 < value < temp_worst:
                    temp_worst = value
                    self.worst_parameters_all[perf_ind] = filename
                elif order == "low" and value > temp_worst:
                    temp_worst = value
                    self.worst_parameters_all[perf_ind] = filename

            if perf_ind in settings.exclude_perf_indic_leg:  # continue to next performance indicator
                continue

            for leg in range(competition_day.no_legs):

                temp_best = 0
                temp_worst = 0

                for flight in competition_day.flights:

                    if flight.outlanded and flight.outlanding_leg <= leg and perf_ind not in settings.perf_indic_outland:
                        continue

                    if flight.performance.no_thermals_leg[leg] == 0 and perf_ind in settings.thermal_indicators:
                        continue

                    value = flight.performance.leg[leg][perf_ind]
                    filename = flight.file_name

                    if (order == 'high' or order == 'low') and temp_best == 0:
                        temp_best = value
                        temp_worst = value
                        self.best_parameters_leg[leg][perf_ind] = filename
                        self.worst_parameters_leg[leg][perf_ind] = filename

                    # check for best value
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

    def write_general_info(self, competition_day):
        date = competition_day.task_date
        self.ws_all.write(0, 0, date)

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

            if leg != -1 and perf_ind in settings.exclude_perf_indic_leg:
                continue

            row = 1
            content = settings.perf_dict[perf_ind]['name']
            style = self.style_dict['performance_names']
            perf_format = settings.perf_dict[perf_ind]['format']
            self.write_cell(leg, row, col, content, style)

            for flight in competition_day.flights:
                row += 1

                if leg == -1:
                    if flight.outlanded and perf_ind not in settings.perf_indic_outland or\
                            flight.performance.no_thermals == 0 and perf_ind in settings.thermal_indicators:
                        continue
                    else:
                        content = flight.performance.all[perf_ind]
                else:
                    if flight.outlanded and flight.outlanding_leg < leg or\
                        flight.outlanded and flight.outlanding_leg <= leg and perf_ind not in settings.perf_indic_outland or\
                                            flight.performance.no_thermals_leg[leg] == 0 and perf_ind in settings.thermal_indicators:
                        continue
                    else:
                        content = flight.performance.leg[leg][perf_ind]
                style = self.style_dict[perf_format + self.style_addition(leg, perf_ind, flight.file_name)]
                self.write_cell(leg, row, col, content, style)

            col += 1

    def write_title(self, leg, settings, competition_day):
        row = 0
        col = 1

        if leg == -1:
            no_cols = len(settings.perf_indic_all)
            title = "Entire flight"
            self.ws_all.write_merge(row, row, col, col+no_cols, title, self.style_dict['style_phase'])
        else:
            no_cols = len(settings.perf_indic_all) - len(settings.exclude_perf_indic_leg)
            name1 = competition_day.tp_names[leg]
            name2 = competition_day.tp_names[leg+1]
            title = "Leg " + str(leg+1) + ": " + name1 + " - " + name2
            self.ws_legs[leg].write_merge(row, row, col, col+no_cols, title, self.style_dict['style_phase'])

    def write_whole_flight(self, settings, competition_day):
        self.write_title(-1, settings, competition_day)
        self.write_perf_indics(-1, settings, competition_day)

    def write_legs(self, settings, competition_day):
        for leg in range(competition_day.no_legs):
            self.write_title(leg, settings, competition_day)
            self.write_perf_indics(leg, settings, competition_day)

    def write_file(self, competition_day, settings):

        self.write_general_info(competition_day)
        self.determine_best_worst(competition_day, settings)
        self.write_whole_flight(settings, competition_day)
        self.write_legs(settings, competition_day)

        self.wb.save(self.file_name)


if __name__ == '__main__':
    from main_pysoar import run
    run()
