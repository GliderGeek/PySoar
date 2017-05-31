from math import pi

from generalFunctions import det_average_bearing
from generalFunctions import calculate_distance, det_bearing, det_bearing_change


class Taskpoint(object):  # startpoint, turnpoints and finish

    def __init__(self, LCU_line, LSEEYOU_line):
        self.LCU_line = LCU_line
        self.LSEEYOU_line = LSEEYOU_line

        self.orientation_angle = None
        self.r_max = None
        self.angle_max = None
        self.r_min = None
        self.angle_min = None

        self.name = LCU_line[23::]
        self.line = 'Line=1\n' in self.LSEEYOU_line.split(',') or 'Line=1' in self.LSEEYOU_line.split(',')
        self.sector_orientation = self.det_sector_orientation()  # fixed, symmetrical, next, previous, start
        self.distance_correction = self.det_distance_correction()  # None, displace_tp, shorten_legs
        self.det_sector_sizes()

    def fixed_orientation_angle(self):
        components = self.LSEEYOU_line.rstrip().split(",")
        for component in components:
            if component.startswith("A12="):
                self.orientation_angle = float(component.split("=")[1])
                break

    def det_sector_orientation(self):
        components = self.LSEEYOU_line.rstrip().split(",")
        for component in components:
            if component.startswith("Style="):
                style = int(component.split("=")[1])
                if style == 0:
                    return "fixed"
                elif style == 1:
                    return "symmetrical"
                elif style == 2:
                    return "next"
                elif style == 3:
                    return "previous"
                elif style == 4:
                    return "start"
                else:
                    print "Unknown taskpoint style! " + str(style)
                    return ""

    def det_distance_correction(self):
        components = self.LSEEYOU_line.rstrip().split(",")
        reduce = False
        move = False
        for component in components:
            if component.startswith("Reduce="):
                reduce = bool(component.split("=")[1])
            elif component.startswith("Move="):
                move = bool(component.split("=")[1])

        if reduce and move:
            return "shorten_legs"
        elif reduce:
            return "shorten_legs"
        elif move:
            return "move_tp"
        else:
            return None

    def set_orientation_angle(self, angle_start=None, angle_previous=None, angle_next=None):
        if self.sector_orientation == "fixed":
            self.fixed_orientation_angle()
        elif self.sector_orientation == "symmetrical":
            self.orientation_angle = det_average_bearing(angle_previous, angle_next)
        elif self.sector_orientation == "next":
            self.orientation_angle = angle_next
        elif self.sector_orientation == "previous":
            self.orientation_angle = angle_previous
        elif self.sector_orientation == "start":
            self.orientation_angle = angle_start
        else:
            print "Unknown sector orientation! " + str(self.sector_orientation)

    def det_sector_sizes(self):
        components = self.LSEEYOU_line.rstrip().split(",")
        for component in components:
            if component.startswith("R1="):
                self.r_max = int(component.split("=")[1][:-1])
            elif component.startswith("A1="):
                self.angle_max = int(component.split("=")[1])
            elif component.startswith("R2="):
                self.r_min = int(component.split("=")[1][:-1])
            elif component.startswith("A2="):
                self.angle_min = int(component.split("=")[1])

    def inside_sector(self, fix):

        distance = calculate_distance(fix, self.LCU_line, 'pnt', 'tsk')
        bearing = det_bearing(self.LCU_line, fix, 'tsk', 'pnt')
        angle_wrt_orientation = abs(det_bearing_change(self.orientation_angle, bearing))

        if self.line:
            print 'Calling inside_sector on a line!'
            exit(1)
        elif self.r_min is not None:
            return self.r_min < distance < self.r_max and angle_wrt_orientation < self.angle_max
        else:  # self.r_min is None
            return distance < self.r_max and (pi - angle_wrt_orientation) < self.angle_max

    def outside_sector(self, fix):
        return not self.inside_sector(fix)

    def crossed_line(self, fix1, fix2):

        distance1 = calculate_distance(fix1, self.LCU_line, 'pnt', 'tsk')
        distance2 = calculate_distance(fix2, self.LCU_line, 'pnt', 'tsk')

        if not self.line:
            print 'Calling crossed_line on a sector!'
            exit(1)
        else:
            if distance2 > self.r_max or distance1 > self.r_max:
                return False
            else:
                bearing1 = det_bearing(self.LCU_line, fix1, 'tsk', 'pnt')
                bearing2 = det_bearing(self.LCU_line, fix2, 'tsk', 'pnt')

                angle_wrt_orientation1 = abs(det_bearing_change(self.orientation_angle, bearing1))
                angle_wrt_orientation2 = abs(det_bearing_change(self.orientation_angle, bearing2))

                if self.sector_orientation == "next":  # start line
                    return angle_wrt_orientation1 < 90 < angle_wrt_orientation2
                elif self.sector_orientation == "previous":  # finish line
                    return angle_wrt_orientation2 < 90 < angle_wrt_orientation1
                else:
                    print "A line with this orientation is not implemented!"
                    exit(1)



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
