from task import Task


class AAT(Task):

    def __init__(self, task_information):
        super(AAT, self).__init__(task_information)

        self.t_min = task_information['t_min']

    def set_task_distances(self, flight):  # different from racetask in that it takes the flight into account
        pass

    def apply_rules(self, trace, trip, trace_settings):
        self.determine_trip_fixes(trace, trip, trace_settings)
        self.determine_trip_distances(trip)

    def determine_trip_fixes(self, trace, trip, trace_settings):
        pass

    def determine_trip_distances(self, trip):
        pass
