from scs import StreplaDaily
from cuc import SoaringSpotDaily
from competitionDay import CompetitionDay
from exportClass import ExcelExport
from settingsClass import Settings

settings = Settings()


def run(url, source, url_status=None, download_progress=None, analysis_progress=None):

    if source == 'cuc':
        daily_result_page = SoaringSpotDaily(url)
    elif source == 'scs':
        daily_result_page = StreplaDaily(url)
    else:
        raise ValueError('This source is not supported: %s' % source)

    daily_result_page.download_flights(download_progress)

    competition_day = CompetitionDay(url_status, source, daily_result_page.igc_directory,
                                     daily_result_page.file_names, daily_result_page.rankings,
                                     daily_result_page.planes, daily_result_page.date)

    competition_day.analyze_flights(analysis_progress)

    excel_sheet = ExcelExport(settings, competition_day.task.no_legs)
    excel_sheet.write_file(competition_day, settings, daily_result_page.igc_directory)
