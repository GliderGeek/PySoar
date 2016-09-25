from taskpoint import Taskpoint
from generalFunctions import det_final_bearing


class Task(object):

    def __init__(self, task_information):

        self.utc_diff = task_information['utc_diff']
        self.aat = task_information['aat']
        self.multi_start = task_information['multi_start']
        self.start_opening = task_information['start_opening']
        self.lcu_lines = task_information['lcu_lines']
        self.lseeyou_lines = task_information['lseeyou_lines']

        self.taskpoints = []
        self.initialize_taskpoints()
        self.no_tps = len(self.taskpoints) - 2  # excluding start and finish
        self.no_legs = self.no_tps + 1

    def initialize_taskpoints(self):

        # check on sizes
        if len(self.lcu_lines)-3 != len(self.lseeyou_lines):
            print 'lcu_lines and lseeyou_lines do not have expected lengths!'
            exit(1)

        for index in range(len(self.lcu_lines)):

            if index == 0 or index == 1 or index == len(self.lcu_lines)-1:  # omitting date, take-off and landing
                continue

            self.taskpoints.append(Taskpoint(self.lcu_lines[index], self.lseeyou_lines[index]))

        self.set_orientation_angles()

    def set_orientation_angles(self):
        # sector orientations and angles
        for index in range(len(self.taskpoints)):

            if index == 0:  # necessary for index out of bounds
                angle = det_final_bearing(self.taskpoints[index+1].LCU_line, self.taskpoints[index].LCU_line,
                                          'tsk', 'tsk')
                self.taskpoints[index].set_orientation_angle(angle_next=angle)
            elif index == len(self.taskpoints) - 1:  # necessary for index out of bounds
                angle = det_final_bearing(self.taskpoints[index-1].LCU_line, self.taskpoints[index].LCU_line,
                                          'tsk', 'tsk')
                self.taskpoints[index].set_orientation_angle(angle_previous=angle)
            else:
                angle_start = det_final_bearing(self.taskpoints[0].LCU_line, self.taskpoints[index].LCU_line,
                                                'tsk', 'tsk')
                angle_previous = det_final_bearing(self.taskpoints[index-1].LCU_line, self.taskpoints[index].LCU_line,
                                                   'tsk', 'tsk')
                angle_next = det_final_bearing(self.taskpoints[index+1].LCU_line, self.taskpoints[index].LCU_line,
                                               'tsk', 'tsk')

                self.taskpoints[index].set_orientation_angle(angle_start=angle_start,
                                                             angle_previous=angle_previous,
                                                             angle_next=angle_next)
