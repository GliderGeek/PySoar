class Taskpoint(object):  # startpoint, turnpoints and finish

    def det_orientation_angle(self):
        components = self.LSEEYOU_line.split(",")
        for component in components:
            if component.startswith("A12="):
                self.orientation_angle = component.split("=")[1]
                break

    def det_sector_orientation(self):
        components = self.LSEEYOU_line.split(",")
        for component in components:
            if component.startswith("Style="):
                style = int(component.split("=")[1])
                if style == 0:
                    self.det_orientation_angle()
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
        components = self.LSEEYOU_line.split(",")
        reduce = False
        move = False
        for component in components:
            if component.startswith("Reduce="):
                reduce = component.split("=")[1]
            elif component.startswith("Move="):
                move = component.split("=")[1]

        if reduce and move:
            return "shorten_legs"
        elif reduce:
            return "shorten_legs"
        elif move:
            return "move_tp"
        else:
            return None

    def det_sector_sizes(self):
        components = self.LSEEYOU_line.split(",")
        for component in components:
            if component.startswith("R1="):
                self.r_max = int(component.split("=")[1][:-1])
            elif component.startswith("A1="):
                self.angle_max = int(component.split("=")[1])
            elif component.startswith("R2="):
                self.r_min = int(component.split("=")[1][:-1])
            elif component.startswith("A2="):
                self.angle_min = int(component.split("=")[1])

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

    def taskpoint_completed(self, brecord1, brecord2):
        from generalFunctions import det_bearing, det_bearing_change, determine_distance, det_local_time, ss2hhmmss

        distance1 = determine_distance(brecord1, self.LCU_line, 'pnt', 'tsk')
        distance2 = determine_distance(brecord2, self.LCU_line, 'pnt', 'tsk')

        if self.line:
            if distance2 > self.r_max or distance1 > self.r_max:
                return False
            else:  # both fixes within circle
                bearing1 = det_bearing(self.LCU_line, brecord1, 'tsk', 'pnt')
                bearing2 = det_bearing(self.LCU_line, brecord2, 'tsk', 'pnt')

                angle_wrt_orientation1 = abs(det_bearing_change(self.orientation_angle, bearing1))
                angle_wrt_orientation2 = abs(det_bearing_change(self.orientation_angle, bearing2))

                if self.sector_orientation == "next":  # start line
                    return angle_wrt_orientation1 < 90 < angle_wrt_orientation2
                elif self.sector_orientation == "previous":  # finish line
                    return angle_wrt_orientation2 < 90 < angle_wrt_orientation1
                else:
                    print "A line with this orientation is not implemented!"
        else:  # general sector
            bearing1 = det_bearing(self.LCU_line, brecord1, 'tsk', 'pnt')
            angle_wrt_orientation1 = abs(det_bearing_change(self.orientation_angle, bearing1))
            bearing2 = det_bearing(self.LCU_line, brecord2, 'tsk', 'pnt')
            angle_wrt_orientation2 = abs(det_bearing_change(self.orientation_angle, bearing2))

            if self.sector_orientation == "next":
                if self.r_min is not None:
                    if self.r_min < distance1 < self.r_max and angle_wrt_orientation1 < self.angle_max:
                        return (not self.r_min < distance2 < self.r_max) or angle_wrt_orientation2 > self.angle_max
                    elif distance1 < self.r_min and angle_wrt_orientation1 < self.angle_min:
                        return distance2 > self.r_min or angle_wrt_orientation2 > self.angle_max
                    else:
                        return False
                else:  # self.r_min is None
                    if distance1 < self.r_max and angle_wrt_orientation1 < self.angle_max:
                        return distance2 > self.r_min or angle_wrt_orientation2 > self.angle_max
                    else:
                        return False

            else:  # normal turnpoint or finish
                if self.r_min is not None:
                    if distance2 > self.r_max:
                        return False
                    elif self.r_min < distance2 < self.r_max:
                        return angle_wrt_orientation2 < self.angle_max
                    else:  # distance_2 < self.r_min
                        return angle_wrt_orientation2 < self.angle_min
                elif distance2 > self.r_max:
                    return False
                else:  # distance2 <= self.r_max
                    return angle_wrt_orientation2 < self.angle_max

#############################  LICENSE  #####################################
#																			#
#   PySoar - Automating gliding competition analysis						#
#   Copyright (C) 2016  Matthijs Beekman									#
# 																			#
#   This program is free software: you can redistribute it and/or modify	#
#   it under the terms of the GNU General Public License as published by	#
#   the Free Software Foundation, either version 3 of the License, or		#
#   (at your option) any later version.										#
# 																			#
#   This program is distributed in the hope that it will be useful,			#
#   but WITHOUT ANY WARRANTY; without even the implied warranty of			#
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the			#
#   GNU General Public License for more details.							#
# 																			#
#   You should have received a copy of the GNU General Public License		#
#   along with this program.  If not, see <http://www.gnu.org/licenses/>	#
