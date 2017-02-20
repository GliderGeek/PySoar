from competitionDay import CompetitionDay
from importClass import SoaringSpotImport
from exportClass import ExcelExport
from settingsClass import Settings

settings = Settings()


def run(url, url_status=None, download_progress=None, analysis_progress=None):

    soaring_spot_info = SoaringSpotImport(url, download_progress)
    competition_day = CompetitionDay(soaring_spot_info, url_status)

    competition_day.analyze_flights(soaring_spot_info, analysis_progress)

    excel_sheet = ExcelExport(settings, competition_day)
    excel_sheet.write_file(competition_day, settings, soaring_spot_info)
