from competitionDay import CompetitionDay
from phasesClass import FlightPhases
from performanceClass import Performance
from importClass import SoaringSpotImport
from exportClass import ExcelExport
from settingsClass import Settings

settings = Settings()


def run(url, download_progress, url_status, analysis_progress):

    soaring_spot_info = SoaringSpotImport(url, download_progress)
    competition_day = CompetitionDay(soaring_spot_info)
    excel_sheet = ExcelExport(settings, competition_day)

    # shortcoming of PySoar
    if competition_day.task.multi_start:
        url_status.configure(text="Multiple starting points not implemented!", foreground='red')
        url_status.update()
        return

    for flight in competition_day.flights:
        print flight.file_name

        flight.determine_tsk_times(competition_day)
        flight.phases = FlightPhases(settings, competition_day, flight)
        flight.performance = Performance(competition_day, flight)

        soaring_spot_info.flights_analyzed += 1
        analysis_progress.configure(text='Analyzed: ' + str(soaring_spot_info.flights_analyzed) + '/' + str(len(soaring_spot_info.file_names)))
        analysis_progress.update()

    excel_sheet.write_file(competition_day, settings)
