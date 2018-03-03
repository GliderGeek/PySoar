import operator
import os

from aerofiles.igc import Reader
from opensoar.competition.strepla import StreplaDaily
from opensoar.competition.soaringspot import SoaringSpotDaily, get_task_from_igc
from PySoar.exportClass import ExcelExport
from PySoar.performanceClass import Performance
from PySoar.settingsClass import Settings

settings = Settings()


def get_analysis_progress_function(analysis_progress_label):
    analysis_progress = None
    if analysis_progress_label is not None:
        def analysis_progress(analyzed, total_number_of_flights):
            analysis_progress_label.configure(text=f'Analyzed: {analyzed}/{total_number_of_flights}')
            analysis_progress_label.update()

    return analysis_progress


def get_download_progress_function(download_progress_label):
    download_progress = None
    if download_progress_label is not None:
        def download_progress(downloads, total_number_of_flights):
            download_progress_label.configure(text=f'Downloaded: {downloads}/{total_number_of_flights}')
            download_progress_label.update()

    return download_progress


def run(url, source, url_status=None, download_progress_label=None, analysis_progress_label=None):
    # todo: is next check performed?
    # fix error in task definition: e.g.: LSEEYOU OZ=-1,Style=2SpeedStyle=0,R1=5000m,A1=180,Line=1
    # SpeedStyle=# is removed, where # is a number

    # todo: is next check performed?
    # fix wrong style definition on start and finish points
    # task_information['lseeyou_lines'][0] = task_information['lseeyou_lines'][0].replace('Style=1', 'Style=2')

    # todo: check strepla

    start_directory = os.path.join(settings.current_dir, 'bin')
    if source == 'cuc':
        daily_result_page = SoaringSpotDaily(url, start_directory)
    elif source == 'scs':
        daily_result_page = StreplaDaily(url, start_directory)
    else:
        raise ValueError('This source is not supported: %s' % source)

    analysis_progress = get_analysis_progress_function(analysis_progress_label)
    download_progress = get_download_progress_function(download_progress_label)

    daily_result_page.download_flights(download_progress)

    competition_day = daily_result_page.competition_day

    tasks = list()
    tasks_rules = list()
    number_of_times_present = list()
    for competitor in competition_day.competitors:

        with open(competitor.file_path, 'r') as f:
            parsed_igc_file = Reader().read(f)

        task, task_rules = get_task_from_igc(parsed_igc_file)

        if task in tasks:
            index = tasks.index(task)
            number_of_times_present[index] += 1
        else:
            tasks.append(task)
            number_of_times_present.append(1)
            tasks_rules.append(task_rules)

        # is this covered for both strepla and soaringspot? not same information present in igc file
        header_errors, headers = parsed_igc_file['header']
        competitor.plane = headers['glider_model']

        trace_errors, trace = parsed_igc_file['fix_records']
        if len(trace_errors) == 0:
            competitor.trace = trace

    max_index, max_value = max(enumerate(number_of_times_present), key=operator.itemgetter(1))

    task = tasks[max_index]
    task_rules = tasks_rules[max_index]

    multi_start = task_rules.get('multi_start', False)
    utc_diff = task_rules.get('multi_start', False)
    if url_status is not None and multi_start:
        url_status.configure(text="Multiple starting points not implemented!", foreground='red')
        url_status.update()
        return

    competition_day.task = task
    classification_method = 'pysoar'
    competition_day.analyse_flights(classification_method, analysis_progress)

    for competitor in competition_day.competitors:

        # put gps_altitude to False when nonzero pressure altitude is found
        gps_altitude = True
        for fix in competitor.trace:
            if fix['pressure_alt'] != 0:
                gps_altitude = False

        competitor.performance = Performance(competition_day.task, competitor.trip, competitor.phases,
                                             gps_altitude)

    excel_sheet = ExcelExport(settings, competition_day.task.no_legs)
    excel_sheet.write_file(competition_day, settings, daily_result_page.igc_directory)
