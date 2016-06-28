from generalFunctions import hhmmss2ss, determine_distance, print_array_debug,\
    ss2hhmmss, det_bearing, det_average_bearing, det_bearing_change, det_final_bearing
from settingsClass import Settings
from taskpoints import Taskpoint

settings = Settings()


class CompetitionDay(object):

    def __init__(self):
        self.flights = []
        self.file_paths = []

        self.task = []
        self.LCU_lines = []
        self.LSEEYOU_lines = []
        self.task_distances = []

        self.task_date = ""

        self.no_tps = 0
        self.no_legs = 0

        self.aat = False
        self.multi_start = False
        self.task_found = False
        self.start_opening = hhmmss2ss("09:00:00", 0)

    def distance_shortened_leg(self, distance, current, currentP1, shortened_point):
        if shortened_point == "current":
            distance -= current.r_max if current.r_max is not None else current.r_min
            return distance
        elif shortened_point == "currentP1":
            distance -= currentP1.r_max if currentP1.r_max is not None else currentP1.r_min
            return distance
        else:
            print "Shortened point is not recognized! " + shortened_point

    def distance_moved_turnpoint(self, distance, current, currentP1, moved_point):
        from math import sqrt, cos, pi, acos

        if moved_point == "current":
            moved = current
            other = currentP1
            angle_reduction = 0
        elif moved_point == "currentP1":
            moved = currentP1
            other = current
            angle_reduction = 0
        elif moved_point == "both_currentP1":
            moved = currentP1
            other = current
            original_distance = determine_distance(current.LCU_line, currentP1.LCU_line, 'tsk', 'tsk')
            distance_moved_current = current.r_max if current.angle_max == 180 else current.r_min
            angle_reduction = abs(acos((distance_moved_current ** 2 - distance ** 2 - original_distance ** 2) / (-2 * distance * original_distance))) * 180 / pi
        else:
            print "Displaced point is not recognized! " + moved_point

        displacement_dist = moved.r_max if moved.angle_max == 180 else moved.r_min
        bearing1 = moved.orientation_angle
        bearing2 = det_bearing(other.LCU_line, moved.LCU_line, 'tsk', 'tsk')
        angle = abs(det_bearing_change(bearing1, bearing2)) - angle_reduction
        distance = sqrt(distance**2 + displacement_dist**2 - 2 * distance * displacement_dist * cos(angle * pi / 180))

        return distance

    def write_task(self):

        date_raw = self.LCU_lines[0][6:12]
        self.task_date = date_raw[0:2] + "-" + date_raw[2:4] + "-" + date_raw[4::]

        for index in range(len(self.LSEEYOU_lines)):
            taskpoint = Taskpoint(self.LCU_lines[index+2], self.LSEEYOU_lines[index])
            self.task.append(taskpoint)

        for index in range(len(self.task)):
            if index == 0:  # necessary for index out of bounds
                angle = det_final_bearing(self.task[index+1].LCU_line, self.task[index].LCU_line, 'tsk', 'tsk')
                self.task[index].orientation_angle = angle
            elif index == len(self.task) - 1:  # necessary for index out of bounds
                angle = det_final_bearing(self.task[index-1].LCU_line, self.task[index].LCU_line, 'tsk', 'tsk')
                self.task[index].orientation_angle = angle
            else:
                angle_start = det_final_bearing(self.task[0].LCU_line, self.task[index].LCU_line, 'tsk', 'tsk')
                angle_previous = det_final_bearing(self.task[index-1].LCU_line, self.task[index].LCU_line, 'tsk', 'tsk')
                angle_next = det_final_bearing(self.task[index+1].LCU_line, self.task[index].LCU_line, 'tsk', 'tsk')

                if self.task[index].sector_orientation == "fixed":
                    pass
                elif self.task[index].sector_orientation == "symmetrical":
                    self.task[index].orientation_angle = det_average_bearing(angle_previous, angle_next)
                elif self.task[index].sector_orientation == "next":
                    self.task[index].orientation_angle = angle_next
                elif self.task[index].sector_orientation == "previous":
                    self.task[index].orientation_angle = angle_previous
                elif self.task[index].sector_orientation == "start":
                    self.task[index].orientation_angle = angle_start
                else:
                    print "Unknown sector orientation! " + str(self.task[index].sector_orientation)

        self.no_tps = len(self.task) - 2  # excluding start and finish
        self.no_legs = self.no_tps + 1

        for index in range(len(self.task)-1):

            current = self.task[index]
            currentP1 = self.task[index+1]  # next is built in name
            distance = determine_distance(current.LCU_line, currentP1.LCU_line, 'tsk', 'tsk')

            if current.distance_correction is "shorten_legs":
                if currentP1.distance_correction is "shorten_legs":
                    distance = self.distance_shortened_leg(distance, current, currentP1, "current")
                    distance = self.distance_shortened_leg(distance, current, currentP1, "currentP1")
                elif currentP1.distance_correction is "move_tp":
                    distance = self.distance_moved_turnpoint(distance, current, currentP1, "currentP1")
                    distance = self.distance_shortened_leg(distance, current, currentP1, "current")
                elif currentP1.distance_correction is None:
                    distance = self.distance_shortened_leg(distance, current, currentP1, "current")
                else:
                    print "This distance correction does not exist! " + currentP1.distance_correction

            elif current.distance_correction is "move_tp":
                if currentP1.distance_correction is "shorten_legs":
                    distance = self.distance_moved_turnpoint(distance, current, currentP1, "current")
                    distance = self.distance_shortened_leg(distance, current, currentP1, "currentP1")
                elif currentP1.distance_correction is "move_tp":
                    distance = self.distance_moved_turnpoint(distance, current, currentP1, "current")
                    distance = self.distance_moved_turnpoint(distance, current, currentP1, "both_currentP1")
                elif currentP1.distance_correction is None:
                    distance = self.distance_moved_turnpoint(distance, current, currentP1, "current")
                else:
                    print "This distance correction does not exist! " + currentP1.distance_correction

            elif current.distance_correction is None:
                if currentP1.distance_correction is "shorten_legs":
                    distance = self.distance_shortened_leg(distance, current, currentP1, "currentP1")
                elif currentP1.distance_correction is "move_tp":
                    distance = self.distance_moved_turnpoint(distance, current, currentP1, "currentP1")
                elif currentP1.distance_correction is None:
                    pass
                else:
                    print "This distance correction does not exist! " + currentP1.distance_correction

            else:
                print "This distance correction does not exist! " + self.task[index].distance_correction

            self.task_distances.append(distance)

    def save(self):
        file_name = settings.current_dir + "/debug_logs/competitionDayDebug.txt"
        text_file = open(file_name, "w")

        print_array_debug(text_file, "task", self.task)
        print_array_debug(text_file, "task_dists", self.task_distances)

        text_file.write("task_date: " + self.task_date + "\n\n")

        text_file.write("no_tps: " + str(self.no_tps) + "\n")
        text_file.write("no_legs: " + str(self.no_legs) + "\n\n")

        text_file.write("aat: " + str(self.aat) + "\n")
        text_file.write("task_found: " + str(self.task_found) + "\n")
        text_file.write("start_opening: " + ss2hhmmss(self.start_opening) + "\n\n")

        text_file.close()

if __name__ == '__main__':
    from main_pysoar import run
    run()

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
