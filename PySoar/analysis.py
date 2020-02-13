import os

from opensoar.competition.strepla import StreplaDaily
from opensoar.competition.soaringspot import SoaringSpotDaily

from exportClass import ExcelExport
from performanceClass import Performance
from settingsClass import Settings

settings = Settings()


def run(url, source, download_progress=None, analysis_progress=None, on_success=None, on_failure=None):
    target_directory = os.path.join(settings.current_dir, 'bin')
    if source == 'cuc':
        daily_result_page = SoaringSpotDaily(url)
    elif source == 'scs':
        daily_result_page = StreplaDaily(url)
    else:
        raise ValueError('This source is not supported: %s' % source)

    competition_day = daily_result_page.generate_competition_day(target_directory, download_progress)

    if competition_day.task.multistart:
        if on_failure is not None:
            on_failure("Multiple starting points not implemented!")
        return

    classification_method = 'pysoar'
    failed_comp_ids = competition_day.analyse_flights(classification_method, analysis_progress,
                                                      skip_failed_analyses=True)

    for competitor in competition_day.competitors:

        if competitor.competition_id in failed_comp_ids:
            continue
        else:
            try:
                # put gps_altitude to False when nonzero pressure altitude is found
                gps_altitude = True
                for fix in competitor.trace:
                    if fix['pressure_alt'] != 0:
                        gps_altitude = False

                competitor.performance = Performance(competition_day.task, competitor.trip, competitor.phases,
                                                     gps_altitude)
            except Exception:
                failed_comp_ids.append(competitor.competition_id)

    failed_competitors = []
    for competitor in competition_day.competitors:
        if competitor.competition_id in failed_comp_ids:
            failed_competitors.append(competitor)

    # remove failed competitors for which the analysis failed
    for failed_competitor in failed_competitors:
        competition_day.competitors.remove(failed_competitor)

    excel_sheet = ExcelExport(settings, competition_day.task.no_legs)
    excel_sheet.write_file(competition_day, settings, daily_result_page.igc_directory)

    on_success()
