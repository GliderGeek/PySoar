from settingsClass import Settings
from competitionDay import CompetitionDay
from flightClass import Flight
from phasesClass import FlightPhases
# from performanceClass import Performance


def run():
    settings = Settings()
    competition_day = CompetitionDay()

    file_paths = ["../46L_GO4.igc", "../46L_HS.igc", "../46L_SW.igc"]
    for path in file_paths:
        file_name = path.split("/")[-1]
        competition_day.file_paths[file_name] = path
        competition_day.flights[file_name] = Flight(file_name)
        competition_day.flights[file_name].read_igc(competition_day)

    if not hasattr(competition_day, 'start_opening'):
        competition_day.ask_start_opening()

    competition_day.obtain_task_info()

    for flight in competition_day.flights.itervalues():

        flight.determine_tsk_times(competition_day)

        flight.phases = FlightPhases(competition_day)
        flight.phases.determine_phases(settings, competition_day, flight)
        flight.phases.determine_point_statistics(flight, competition_day)

        flight.phases.print_phases()

        # flight.performance = Performance(competition_day)
        # flight.performance.determine_performance(flight)

if __name__ == '__main__':
    from main import run
    run()
