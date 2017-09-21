from taskpoint import Taskpoint
from generalFunctions import det_bearing_change
from generalFunctions import interpolate_b_records
from generalFunctions import det_local_time
from generalFunctions import calculate_final_bearing
from generalFunctions import calculate_bearing
from generalFunctions import calculate_distance2


class Task(object):

    def __init__(self, task_points, aat, multi_start, start_opening, utc_diff):

        self.aat = aat
        self.multi_start = multi_start
        self.start_opening = start_opening
        self.utc_diff = utc_diff

        self.taskpoints = task_points
        self.set_orientation_angles(self.taskpoints)

    @property
    def no_tps(self):
        return len(self.taskpoints) - 2

    @property
    def no_legs(self):
        return self.no_tps + 1

    @staticmethod
    def taskpoints_from_cuc(lcu_lines, lseeyou_lines):

        # check on sizes
        if len(lcu_lines) - 3 != len(lseeyou_lines):
            raise ValueError('lcu_lines and lseeyou_lines do not have expected lengths!')

        taskpoints = []
        for lcu_lines, lseeyou_line in zip(lcu_lines[2:-1], lseeyou_lines):
            taskpoint = Taskpoint.from_cuc(lcu_lines, lseeyou_line)
            taskpoints.append(taskpoint)
            
        return taskpoints

    @staticmethod
    def taskpoints_from_scs(lscs_lines,lscs_lines_tp):
        
        taskpoints = []
        scs_tps = []

        # get task information
        task_info = Taskpoint.scs_task_info(lscs_lines)

        # create turnpoints
        n_tp=len(lscs_lines_tp)
        n=0
        for tp in lscs_lines_tp:
            scs_tp = Taskpoint.scs_tp_create(task_info,n,n_tp)
            scs_tps.append(scs_tp)
            n=n+1

        for lscs_lines_tp,scs_tps in zip(lscs_lines_tp,scs_tps):
            taskpoint = Taskpoint.from_scs(lscs_lines_tp,scs_tps)
            taskpoints.append(taskpoint)

        return taskpoints

    @staticmethod
    def set_orientation_angles(taskpoints):
        # sector orientations and angles
        for index in range(len(taskpoints)):

            if index == 0:  # necessary for index out of bounds
                angle = calculate_final_bearing(
                    taskpoints[index + 1].lat, taskpoints[index + 1].lon,
                    taskpoints[index].lat, taskpoints[index].lon)

                taskpoints[index].set_orientation_angle(angle_next=angle)
            elif index == len(taskpoints) - 1:  # necessary for index out of bounds
                angle = calculate_final_bearing(
                    taskpoints[index - 1].lat, taskpoints[index - 1].lon,
                    taskpoints[index].lat, taskpoints[index].lon)
                taskpoints[index].set_orientation_angle(angle_previous=angle)
            else:

                angle_start = calculate_final_bearing(
                    taskpoints[0].lat, taskpoints[0].lon,
                    taskpoints[index].lat, taskpoints[index].lon)

                angle_previous = calculate_final_bearing(
                    taskpoints[index - 1].lat, taskpoints[index - 1].lon,
                    taskpoints[index].lat, taskpoints[index].lon)

                angle_next = calculate_final_bearing(
                    taskpoints[index + 1].lat, taskpoints[index + 1].lon,
                    taskpoints[index].lat, taskpoints[index].lon)

                taskpoints[index].set_orientation_angle(angle_start=angle_start,
                                                        angle_previous=angle_previous,
                                                        angle_next=angle_next)

    @staticmethod
    def distance_shortened_leg(distance, current, currentP1, shortened_point):
        if shortened_point == "current":
            distance -= current.r_max if current.r_max is not None else current.r_min
            return distance
        elif shortened_point == "end":
            distance -= currentP1.r_max if currentP1.r_max is not None else currentP1.r_min
            return distance
        else:
            print "Shortened point is not recognized! " + shortened_point

    @staticmethod
    def distance_moved_turnpoint(distance, begin, end, moved_point, move_direction='reduce'):
        from math import sqrt, cos, pi, acos

        if moved_point == "begin":
            moved = begin
            other = end
            angle_reduction = 0
        elif moved_point == "end":
            moved = end
            other = begin
            angle_reduction = 0
        elif moved_point == "both_end":
            moved = end
            other = begin
            original_distance = calculate_distance2(begin.lat, begin.lon, end.lat, end.lon)

            distance_moved_current = begin.r_max if begin.angle_max == 180 else begin.r_min
            angle_reduction = abs(acos((distance_moved_current ** 2 - distance ** 2 - original_distance ** 2) / (-2 * distance * original_distance))) * 180 / pi
        else:
            raise ValueError("Displaced point is not recognized: %s" % moved_point)

        displacement_dist = moved.r_max if moved.angle_max == 180 else moved.r_min
        bearing1 = moved.orientation_angle
        bearing2 = calculate_bearing(other.lat, other.lon, moved.lat, moved.lon)

        if move_direction == 'increase':
            angle = 180 - abs(det_bearing_change(bearing1, bearing2)) - angle_reduction
        else:
            angle = abs(det_bearing_change(bearing1, bearing2)) - angle_reduction
        distance = sqrt(distance**2 + displacement_dist**2 - 2 * distance * displacement_dist * cos(angle * pi / 180))

        return distance

    def started(self, fix1, fix2):
        start = self.taskpoints[0]
        if start.line:
            return start.crossed_line(fix1, fix2)
        else:
            return start.inside_sector(fix1) and start.outside_sector(fix2)

    def finished(self, fix1, fix2):
        finish = self.taskpoints[-1]
        if finish.line:
            return finish.crossed_line(fix1, fix2)
        else:
            return finish.outside_sector(fix1) and finish.inside_sector(fix2)

    def refine_start(self, trip, trace):
        start_i = trace.index(trip.fixes[0])
        fixes = interpolate_b_records(trace[start_i-1], trace[start_i])

        for i, fix in enumerate(fixes[:-1]):
            if self.started(fixes[i], fixes[i + 1]):
                trip.refined_start_time = det_local_time(fixes[i], 0)
                break
