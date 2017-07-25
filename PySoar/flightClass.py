from settingsClass import Settings
from phasesClass import FlightPhases
from performanceClass import Performance
from trip import Trip

settings = Settings()


class Flight(object):

    df_categories = ['ranking', 'airplane', 'compID']

    def __init__(self, file_name, competition_id, airplane, ranking, trace, trace_settings):
        self.file_name = file_name

        self.airplane = airplane
        self.competition_id = competition_id
        self.ranking = ranking

        self.trace = trace
        self.trace_settings = trace_settings

        # to be setup during analyze
        self.trip = None
        self.phases = None
        self.performance = None

    @property
    def df_dict(self):

        df_dict = {'ranking': self.ranking,
                   'airplane': self.airplane,
                   'compID': self.competition_id}

        # check consistency with df_categories
        assert sum(1 for key in df_dict if key not in self.df_categories) == 0

        return df_dict

    def analyze(self, task):
        print self.competition_id

        self.trip = Trip(task, self.trace, self.trace_settings)

        if len(self.trip.fixes) >= 1:  # competitor must have started
            self.phases = FlightPhases(self.trip, self.trace, self.trace_settings)
            self.performance = Performance(task, self.trip, self.phases, self.trace, self.trace_settings)

#############################  LICENSE  #####################################

#   PySoar - Automating gliding competition analysis
#   Copyright (C) 2016  Matthijs Beekman
# 
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
# 
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
