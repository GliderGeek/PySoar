from competitionDay import CompetitionDay
from phasesClass import FlightPhases
from performanceClass import Performance
from importClass import SoaringSpotImport
from exportClass import ExcelExport
from settingsClass import Settings

settings = Settings()


def run(url_entry, download_progress, url_status, analysis_progress):

    soaring_spot_info = SoaringSpotImport()
    competition_day = CompetitionDay()

    soaring_spot_info.load(url_entry.get())
    soaring_spot_info.download_flights(download_progress)

    if settings.debugging:
            soaring_spot_info.save(settings)

    competition_day.read_flights(soaring_spot_info)
    competition_day.load_task_information()

    if competition_day.task.multi_start:
        url_status.configure(text="Multiple starting points not implemented!", foreground='red')
        url_status.update()
        return

    if settings.debugging:
        competition_day.save()

    for flight in competition_day.flights:
        print flight.file_name

        flight.determine_tsk_times(competition_day)
        flight.save(soaring_spot_info)

        flight.phases = FlightPhases(competition_day)
        flight.phases.determine_phases(settings, competition_day, flight)

        if settings.debugging:
            flight.phases.save(soaring_spot_info, flight)
        flight.phases.determine_point_statistics(flight, competition_day)

        flight.performance = Performance(competition_day, flight)
        flight.performance.determine_performance(flight, competition_day)

        soaring_spot_info.flights_analyzed += 1
        analysis_progress.configure(text='Analyzed: ' + str(soaring_spot_info.flights_analyzed) + '/' + str(len(soaring_spot_info.file_names)))
        analysis_progress.update()

    excel_sheet = ExcelExport(settings, competition_day)
    excel_sheet.write_file(competition_day, settings)
