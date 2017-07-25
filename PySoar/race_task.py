from taskpoint import Taskpoint
from task import Task
from generalFunctions import det_local_time
from generalFunctions import enl_value_exceeded
from generalFunctions import enl_time_exceeded
from generalFunctions import det_time_difference
from generalFunctions import calculate_distance2
from generalFunctions import det_lat_long


class RaceTask(Task):

    def __init__(self, taskpoints, multi_start, start_opening, utc_diff):

        aat = False
        super(RaceTask, self).__init__(taskpoints, aat, multi_start, start_opening, utc_diff)

        self.distances = self.calculate_task_distances()

    def calculate_task_distances(self):

        distances = []

        for leg in range(self.no_legs):

            begin = self.taskpoints[leg]
            end = self.taskpoints[leg+1]  # next is built in name
            distance = calculate_distance2(begin.lat, begin.lon, end.lat, end.lon)

            if begin.distance_correction is "shorten_legs":
                if end.distance_correction is "shorten_legs":
                    distance = Task.distance_shortened_leg(distance, begin, end, "begin")
                    distance = Task.distance_shortened_leg(distance, begin, end, "end")
                elif end.distance_correction is "move_tp":
                    distance = Task.distance_moved_turnpoint(distance, begin, end, "end")
                    distance = Task.distance_shortened_leg(distance, begin, end, "begin")
                elif end.distance_correction is None:
                    distance = Task.distance_shortened_leg(distance, begin, end, "begin")
                else:
                    raise ValueError("This distance correction does not exist: %s" % end.distance_correction)

            elif begin.distance_correction is "move_tp":
                if end.distance_correction is "shorten_legs":
                    distance = Task.distance_moved_turnpoint(distance, begin, end, "begin")
                    distance = Task.distance_shortened_leg(distance, begin, end, "end")
                elif end.distance_correction is "move_tp":
                    distance = Task.distance_moved_turnpoint(distance, begin, end, "begin")
                    distance = Task.distance_moved_turnpoint(distance, begin, end, "both_end")
                elif end.distance_correction is None:
                    distance = Task.distance_moved_turnpoint(distance, begin, end, "begin")
                else:
                    raise ValueError("This distance correction does not exist: %s" % end.distance_correction)

            elif begin.distance_correction is None:
                if end.distance_correction is "shorten_legs":
                    distance = Task.distance_shortened_leg(distance, begin, end, "end")
                elif end.distance_correction is "move_tp":
                    distance = Task.distance_moved_turnpoint(distance, begin, end, "end")
                elif end.distance_correction is None:
                    pass
                else:
                    raise ValueError("This distance correction does not exist: %s" % end.distance_correction)

            else:
                raise ValueError("This distance correction does not exist: %s" % self.taskpoints[leg].distance_correction)

            distances.append(distance)

        return distances

    def apply_rules(self, trace, trip, trace_settings):

        self.determine_trip_fixes(trip, trace, trace_settings)
        self.determine_trip_distances(trip)
        self.refine_start(trip, trace)

    def determine_trip_fixes(self, trip, trace, trace_settings):

        leg = -1
        enl_time = 0
        enl_first_fix = None
        enl_registered = False

        for i in range(len(trace)):

            t = det_local_time(trace[i], self.utc_diff)

            if trace_settings['enl_indices'] is not None\
                    and not enl_registered\
                    and enl_value_exceeded(trace[i], trace_settings['enl_indices']):

                if enl_time == 0:
                    enl_first_fix = trace[i-1]
                enl_time += det_time_difference(trace[i-1], trace[i], 'pnt', 'pnt')
                enl_registered = enl_registered or enl_time_exceeded(enl_time)
            elif not enl_registered:
                enl_time = 0
                enl_first_fix = None

            start_time_buffer = 15
            if leg == -1 and t + start_time_buffer > self.start_opening and i > 0:
                if self.started(trace[i - 1], trace[i]):
                    start_fix = trace[i]
                    trip.fixes.append(start_fix)
                    trip.start_fixes.append(start_fix)
                    leg += 1
                    enl_time = 0
                    enl_first_fix = None
                    enl_registered = False
            elif leg == 0:
                if self.started(trace[i - 1], trace[i]):  # restart
                    start_fix = trace[i]
                    trip.fixes[0] = start_fix
                    trip.start_fixes.append(start_fix)
                    enl_time = 0
                    enl_first_fix = None
                    enl_registered = False
                if self.finished_leg(leg, trace[i - 1], trace[i]) and not enl_registered:
                    trip.fixes.append(trace[i])
                    leg += 1
            elif 0 < leg < self.no_legs:
                if self.finished_leg(leg, trace[i - 1], trace[i]) and not enl_registered:
                    trip.fixes.append(trace[i])
                    leg += 1

        if enl_registered:
            trip.enl_fix = enl_first_fix

        if len(trip.fixes) is not len(self.taskpoints):
            self.determine_outlanding_fix(trip, trace)

    def determine_outlanding_fix(self, trip, trace):

        last_tp_i = trace.index(trip.fixes[-1]) if trip.outlanding_leg() != 0 else trace.index(trip.start_fixes[0])
        if trip.enl_fix is not None:
            enl_i = trace.index(trip.enl_fix)

        max_dist = 0
        outlanding_fix = None
        for i, fix in enumerate(trace):

            if (trip.enl_fix is None and last_tp_i < i) or (trip.enl_fix is not None and last_tp_i <i < enl_i):

                outlanding_dist = self.determine_outlanding_distance(trip.outlanding_leg(), fix)

                if outlanding_dist > max_dist:
                    max_dist = outlanding_dist
                    outlanding_fix = fix

        if outlanding_fix is None:  # no outlanding fix that improves the distance
            if trip.enl_fix is not None:
                trip.outlanding_fix = trip.enl_fix
            else:
                trip.outlanding_fix = trace[-1]
        else:
            trip.outlanding_fix = outlanding_fix

    def determine_outlanding_distance(self, outlanding_leg, fix):

        task_pointM1 = self.taskpoints[outlanding_leg]
        task_point = self.taskpoints[outlanding_leg + 1]

        fix_lat, fix_lon = det_lat_long(fix, 'pnt')

        # outlanding distance = distance between tps minus distance from next tp to outlanding
        outlanding_dist = calculate_distance2(task_pointM1.lat, task_pointM1.lon, task_point.lat, task_point.lon)
        outlanding_dist -= calculate_distance2(task_point.lat, task_point.lon, fix_lat, fix_lon)

        if outlanding_dist > 0:
            return outlanding_dist
        else:
            return 0

    def determine_trip_distances(self, trip):

        for leg, fix in enumerate(trip.fixes[1:]):
            trip.distances.append(self.distances[leg])

        if trip.outlanding_fix is not None:
            trip.distances.append(self.determine_outlanding_distance(trip.outlanding_leg(), trip.outlanding_fix))

    # function instead of variable to keep it linked
    # maybe also idea for no_tps and no_legs?
    def total_distance(self):
        return sum(self.distances)

    def finished_leg(self, leg, fix1, fix2):
        """Determines whether leg is finished."""

        next_waypoint = self.taskpoints[leg + 1]
        if next_waypoint.line:
            return next_waypoint.crossed_line(fix1, fix2)
        else:
            return next_waypoint.outside_sector(fix1) and next_waypoint.inside_sector(fix2)
