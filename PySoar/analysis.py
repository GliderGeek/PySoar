import os

from aerofiles.igc import Reader
from opensoar.competition.strepla import StreplaDaily
from opensoar.competition.soaringspot import SoaringSpotDaily, get_info_from_comment_lines
from PySoar.exportClass import ExcelExport
from PySoar.settingsClass import Settings

settings = Settings()


def get_analysis_progress_function(analysis_progress_label):
    analysis_progress = None
    if analysis_progress_label is not None:
        def analysis_progress(analyzed, total_number_of_flights):
            analysis_progress_label.configure(text=f'Downloaded: {analyzed}/{total_number_of_flights}')
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
    # todo: re-implement url_status

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

    # assign traces to competitors
    competition_info_list = list()
    for competitor in competition_day.competitors:

        with open(competitor.igc_path, 'r') as f:
            parsed_igc_file = Reader().read(f)

        competition_info = get_info_from_comment_lines(parsed_igc_file)
        competition_info_list.append(competition_info)

        # is this covered for both strepla and soaringspot? not same information present in igc file

        header_errors, headers = parsed_igc_file['header']
        competitor.plane = headers['glider_model']

        trace_errors, trace = parsed_igc_file['fix_records']
        if len(trace_errors) == 0:
            competitor.trace = trace

    # todo: determine which task to be taken and assign to competition_day
    competition_day.task = None
    competition_day.analyse_flights(analysis_progress)

    # todo: add performance to competitors

    excel_sheet = ExcelExport(settings, competition_day.task.no_legs)
    excel_sheet.write_file(competition_day, settings, daily_result_page.igc_directory)
