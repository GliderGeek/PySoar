import os

from opensoar.competition.strepla import StreplaDaily
from opensoar.competition.soaringspot import SoaringSpotDaily
from PySoar.exportClass import ExcelExport
from PySoar.performanceClass import Performance
from PySoar.settingsClass import Settings

settings = Settings()


def get_analysis_progress_function(analysis_progress_label):
    if analysis_progress_label is None:
        def analysis_progress(analyzed, total_number_of_flights):
            print(f'Analyzed: {analyzed}/{total_number_of_flights}')

        return analysis_progress
    else:  # analysis_progress_label is not None:
        def analysis_progress(analyzed, total_number_of_flights):
            analysis_progress_label.configure(text=f'Analyzed: {analyzed}/{total_number_of_flights}')
            analysis_progress_label.update()

        return analysis_progress


def get_download_progress_function(download_progress_label):
    if download_progress_label is None:
        def download_progress(downloads, total_number_of_flights):
            print(f'Downloaded: {downloads}/{total_number_of_flights}')

        return download_progress
    else:  # download_progress_label is not None
        def download_progress(downloads, total_number_of_flights):
            download_progress_label.configure(text=f'Downloaded: {downloads}/{total_number_of_flights}')
            download_progress_label.update()

        return download_progress


def run(url, source, url_status=None, download_progress_label=None, analysis_progress_label=None):
    target_directory = os.path.join(settings.current_dir, 'bin')
    if source == 'cuc':
        daily_result_page = SoaringSpotDaily(url)
    elif source == 'scs':
        daily_result_page = StreplaDaily(url)
    else:
        raise ValueError('This source is not supported: %s' % source)

    analysis_progress = get_analysis_progress_function(analysis_progress_label)
    download_progress = get_download_progress_function(download_progress_label)

    competition_day = daily_result_page.generate_competition_day(target_directory, download_progress)

    if url_status is not None and competition_day.task.multistart:
        url_status.configure(text="Multiple starting points not implemented!", foreground='red')
        url_status.update()
        return

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
