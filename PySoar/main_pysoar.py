from settingsClass import Settings
from competitionDay import CompetitionDay
from flightClass import Flight
from phasesClass import FlightPhases
from performanceClass import Performance
from importClass import SoaringSpotImport
from exportClass import ExcelExport


def run():
    settings = Settings()
    soaring_spot_info = SoaringSpotImport()
    competition_day = CompetitionDay()

    debugging = True

    # either load from soaring spot or prompt input box
    # soaring_spot_info.load()
    soaring_spot_info.load("http://www.soaringspot.com/en/sallandse-tweedaagse-2014/results/club/task-1-on-2014-06-21/daily")
    if debugging:
        soaring_spot_info.save(settings)

    for ii in range(len(soaring_spot_info.file_names)):
        file_name = soaring_spot_info.file_names[ii]
        ranking = soaring_spot_info.rankings[ii]
        competition_day.file_paths.append(soaring_spot_info.igc_directory + file_name)
        competition_day.flights.append(Flight(file_name, ranking))
        competition_day.flights[-1].read_igc(competition_day, soaring_spot_info)

    if competition_day.start_opening == 0:
        competition_day.ask_start_opening()

    competition_day.obtain_task_info()

    if debugging:
        competition_day.save()

    for flight in competition_day.flights:

        print flight.file_name

        flight.determine_tsk_times(competition_day)
        flight.save(soaring_spot_info)

        flight.phases = FlightPhases(competition_day)
        flight.phases.determine_phases(settings, competition_day, flight)
        if debugging:
            flight.phases.save(soaring_spot_info, flight)
        flight.phases.determine_point_statistics(flight, competition_day)

        flight.performance = Performance(competition_day, flight)
        flight.performance.determine_performance(flight, competition_day)

    excel_sheet = ExcelExport(settings, competition_day)
    excel_sheet.write_file(competition_day, settings)

if __name__ == '__main__':
    from main_pysoar import run
    run()
