import os
from threading import Thread

import wx
from opensoar.competition.strepla import StreplaDaily
from opensoar.competition.soaringspot import SoaringSpotDaily

from exportClass import ExcelExport
from performanceClass import Performance
from settingsClass import Settings

settings = Settings()


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data, event_result_id):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(event_result_id)
        self.data = data


class AnalysisThread(Thread):

    def __init__(self, notify_window, download_event_id, analysis_event_id, finish_event_id, url, source):
        Thread.__init__(self)
        self._notify_window = notify_window
        self._download_event_id = download_event_id
        self._analysis_event_id = analysis_event_id
        self._finish_event_id = finish_event_id
        self._url = url
        self._source = source

    def download_progress(self, number=None, total=None):
        if None in (number, total):
            wx.PostEvent(self._notify_window, ResultEvent(f'Downloaded: -', self._download_event_id))
        else:
            wx.PostEvent(self._notify_window, ResultEvent(f'Downloaded: {number}/{total}', self._download_event_id))

    def analysis_progress(self, number=None, total=None):
        if None in (number, total):
            wx.PostEvent(self._notify_window, ResultEvent(f'Analyzed: -', self._analysis_event_id))
        else:
            wx.PostEvent(self._notify_window, ResultEvent(f'Analyzed: {number}/{total}', self._analysis_event_id))

    def run(self):
        target_directory = os.path.join(settings.current_dir, 'bin')
        if self._source == 'cuc':
            daily_result_page = SoaringSpotDaily(self._url)
        elif self._source == 'scs':
            daily_result_page = StreplaDaily(self._url)
        else:
            raise ValueError('This source is not supported: %s' % self._source)

        self.download_progress(None, None)
        competition_day = daily_result_page.generate_competition_day(target_directory, self.download_progress)

        if competition_day.task.multistart:
            wx.PostEvent(self._notify_window, ResultEvent((False, 'Multiple starting points not implemented!'), self._finish_event_id))
            return

        classification_method = 'pysoar'
        self.analysis_progress(None, None)
        failed_comp_ids = competition_day.analyse_flights(classification_method, self.analysis_progress,
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

        wx.PostEvent(self._notify_window, ResultEvent((True, ''), self._finish_event_id))
