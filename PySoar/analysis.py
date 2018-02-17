import os
from opensoar.competition.strepla import StreplaDaily
from opensoar.competition.soaringspot import SoaringSpotDaily
from PySoar.exportClass import ExcelExport
from PySoar.settingsClass import Settings

settings = Settings()


def run(url, source, url_status=None, download_progress=None, analysis_progress=None):
    # todo: decide what to do with this url_status, analysis_progress and download_progress
    # maybe add an optional input to analyse flights. this input is an update function

    start_directory = os.path.join(settings.current_dir, 'bin')
    if source == 'cuc':
        daily_result_page = SoaringSpotDaily(url, start_directory)
    elif source == 'scs':
        daily_result_page = StreplaDaily(url, start_directory)
    else:
        raise ValueError('This source is not supported: %s' % source)

    daily_result_page.download_flights(download_progress)

    competition_day = daily_result_page.get_competition_day()

    competition_day.analyse_flights()

    excel_sheet = ExcelExport(settings, competition_day.task.no_legs)
    excel_sheet.write_file(competition_day, settings, daily_result_page.igc_directory)
