from task import Task
from generalFunctions import determine_distance


class AAT(Task):

    def __init__(self, task_information):
        super(AAT, self).__init__(task_information)

        self.t_min = task_information['t_min']
        self.nominal_distances = []
        self.minimal_distances = []
        self.maximum_distances = []

        self.set_task_distances()

    def set_task_distances(self):
        for leg in range(self.no_legs):

            begin = self.taskpoints[leg]
            end = self.taskpoints[leg+1]  # next is built in name

            distance = determine_distance(begin.LCU_line, end.LCU_line, 'tsk', 'tsk')
            self.nominal_distances.append(distance)

            # calculating maximum distance
            distance_moved_begin = self.distance_moved_turnpoint(distance, begin, end, "begin")
            distance_minimal = self.distance_moved_turnpoint(distance_moved_begin, begin, end, "both_end")
            self.minimal_distances.append(distance_minimal)

            # calculate maximum distance
            distance_moved_begin = self.distance_moved_turnpoint(distance, begin, end, "begin", 'increase')
            distance_maximum = self.distance_moved_turnpoint(distance_moved_begin, begin, end, "both_end", 'increase')
            self.maximum_distances.append(distance_maximum)

    def apply_rules(self, trace, trip, trace_settings):
        self.determine_trip_fixes(trace, trip, trace_settings)
        self.refine_start(trip, trace)
        self.determine_trip_distances(trip)

    def get_sector_fixes(self, trace):
        sector_fixes = [[None]]
        first_start = None

        for trace_index, fix in trace[:-1]:

            taskpoints_completed = len(sector_fixes) if sector_fixes[0] is not None else 0

            # break when finish has been reached
            if taskpoints_completed == self.no_tps-1:
                break

            for tp_index, taskpoint in enumerate(self.taskpoints):

                # determine start fix
                if len(sector_fixes) == 1 and tp_index == 0:
                    fix2 = trace[trace_index+1]
                    if self.started(fix, fix2):
                        sector_fixes[0] = fix2
                        first_start = fix2 if first_start is None else first_start

                # determine finish fix
                elif tp_index == self.no_tps-1:
                    fix2 = trace[trace_index + 1]
                    if self.finished(fix, fix2):
                        sector_fixes.append(fix2)

                # determine fixes inside sectors
                elif tp_index > taskpoints_completed - 1:
                    if taskpoint.inside_sector(fix):
                        if len(sector_fixes) < (tp_index + 1):
                            sector_fixes.append([])
                        sector_fixes[tp_index].append(fix)

                else:
                    continue

        return sector_fixes

    def determine_trip_fixes(self, trace, trip, trace_settings):
        sector_fixes = self.get_sector_fixes(trace)

        # get start fix
        trip.fixes.append(sector_fixes[0][0])

        # determine sector fixes which give maximum distance
        pass

    def determine_outlanding_distance(self, outlanding_leg, fix):
        pass

    def determine_outlanding_fix(self, trip, trace):
        pass

    def determine_trip_distances(self, trip):
        for fix_index, fix1 in trip.fixes[:-1]:
            fix2 = trip.fixes[fix_index + 1]

            if fix_index == 0:  # start: using taskpoint
                distance = determine_distance(self.taskpoints[0], fix2, 'tsk', 'pnt')
            elif fix_index+1 == self.no_tps-1:  # finish: using taskpoint
                distance = determine_distance(fix1, self.taskpoints[-1], 'pnt', 'tsk')
            else:
                distance = determine_distance(fix1, fix2, 'pnt', 'pnt')

            trip.distances.append(distance)
