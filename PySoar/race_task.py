from task import Task
from generalFunctions import determine_distance


class RaceTask(Task):

    def __init__(self, task_information):
        super(RaceTask, self).__init__(task_information)

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
