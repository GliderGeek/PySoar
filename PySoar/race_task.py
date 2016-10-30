from task import Task
from generalFunctions import determine_distance, det_local_time, enl_value_exceeded, enl_time_exceeded, \
    det_time_difference


class RaceTask(Task):

    def __init__(self, task_information):
        super(RaceTask, self).__init__(task_information)

        self.distances = []
        self.set_task_distances()

    def set_task_distances(self):

        for leg in range(self.no_legs):

            begin = self.taskpoints[leg]
            end = self.taskpoints[leg+1]  # next is built in name
            distance = determine_distance(begin.LCU_line, end.LCU_line, 'tsk', 'tsk')

            if begin.distance_correction is "shorten_legs":
                if end.distance_correction is "shorten_legs":
                    distance = self.distance_shortened_leg(distance, begin, end, "begin")
                    distance = self.distance_shortened_leg(distance, begin, end, "end")
                elif end.distance_correction is "move_tp":
                    distance = self.distance_moved_turnpoint(distance, begin, end, "end")
                    distance = self.distance_shortened_leg(distance, begin, end, "begin")
                elif end.distance_correction is None:
                    distance = self.distance_shortened_leg(distance, begin, end, "begin")
                else:
                    print "This distance correction does not exist! " + end.distance_correction

            elif begin.distance_correction is "move_tp":
                if end.distance_correction is "shorten_legs":
                    distance = self.distance_moved_turnpoint(distance, begin, end, "begin")
                    distance = self.distance_shortened_leg(distance, begin, end, "end")
                elif end.distance_correction is "move_tp":
                    distance = self.distance_moved_turnpoint(distance, begin, end, "begin")
                    distance = self.distance_moved_turnpoint(distance, begin, end, "both_end")
                elif end.distance_correction is None:
                    distance = self.distance_moved_turnpoint(distance, begin, end, "begin")
                else:
                    print "This distance correction does not exist! " + end.distance_correction

            elif begin.distance_correction is None:
                if end.distance_correction is "shorten_legs":
                    distance = self.distance_shortened_leg(distance, begin, end, "end")
                elif end.distance_correction is "move_tp":
                    distance = self.distance_moved_turnpoint(distance, begin, end, "end")
                elif end.distance_correction is None:
                    pass
                else:
                    print "This distance correction does not exist! " + end.distance_correction

            else:
                print "This distance correction does not exist! " + self.taskpoints[leg].distance_correction

            self.distances.append(distance)

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

            if leg == -1 and t > self.start_opening and i > 0:
                if self.taskpoints[0].taskpoint_completed(trace[i - 1], trace[i]):
                    start_fix = trace[i]
                    trip.fixes.append(start_fix)
                    trip.start_fixes.append(start_fix)
                    leg += 1
            elif leg == 0:
                if self.taskpoints[0].taskpoint_completed(trace[i - 1], trace[i]):  # restart
                    start_fix = trace[i]
                    trip.fixes[0] = start_fix
                    trip.start_fixes.append(start_fix)
                    enl_time = 0
                    enl_first_fix = None
                    enl_registered = False
                if self.taskpoints[leg + 1].taskpoint_completed(trace[i - 1], trace[i]) and not enl_registered:
                    trip.fixes.append(trace[i])
                    leg += 1
            elif 0 < leg < self.no_legs:
                if self.taskpoints[leg + 1].taskpoint_completed(trace[i - 1], trace[i]) and not enl_registered:
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

        trip.outlanding_fix = outlanding_fix

    def determine_outlanding_distance(self, outlanding_leg, fix):

        task_pointM1 = self.taskpoints[outlanding_leg].LCU_line
        task_point = self.taskpoints[outlanding_leg + 1].LCU_line

        # outlanding distance = distance between tps minus distance from next tp to outlanding
        outlanding_dist = determine_distance(task_pointM1, task_point, 'tsk', 'tsk')
        outlanding_dist -= determine_distance(task_point, fix, 'tsk', 'pnt')

        return outlanding_dist

    def determine_trip_distances(self, trip):

        for leg, fix in enumerate(trip.fixes[1:]):
            trip.distances.append(self.distances[leg])

        if trip.outlanding_fix is not None:
            trip.distances.append(self.determine_outlanding_distance(trip.outlanding_leg(), trip.outlanding_fix))

    # function instead of variable to keep it linked
    # maybe also idea for no_tps and no_legs?
    def total_distance(self):
        return sum(self.distances)
