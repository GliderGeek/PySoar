from math import pi

from generalFunctions import det_average_bearing
from generalFunctions import calculate_distance2
from generalFunctions import det_lat_long
from generalFunctions import calculate_bearing
from generalFunctions import det_bearing_change


class Taskpoint(object):  # startpoint, turnpoints and finish

    def __init__(self, name, lat, lon, r_min, angle_min, r_max, angle_max, orientation_angle,
                 line, sector_orientation, distance_correction):

        self.name = name

        self.lat = lat
        self.lon = lon

        self.r_min = r_min
        self.angle_min = angle_min
        self.r_max = r_max
        self.angle_max = angle_max
        self.orientation_angle = orientation_angle

        self.line = line
        self.sector_orientation = sector_orientation  # fixed, symmetrical, next, previous, start
        self.distance_correction = distance_correction  # None, displace_tp, shorten_legs

    @staticmethod
    def cuc_fixed_orientation_angle(LSEEYOU_line):
        components = LSEEYOU_line.rstrip().split(",")
        for component in components:
            if component.startswith("A12="):
                return float(component.split("=")[1])

    @staticmethod
    def cuc_sector_orientation(LSEEYOU_line):
        components = LSEEYOU_line.rstrip().split(",")
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

    @staticmethod
    def cuc_distance_correction(LSEEYOU_line):
        components = LSEEYOU_line.rstrip().split(",")
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
        # Fixed orientation is skipped as that has already been set

        if self.sector_orientation == "symmetrical":
            self.orientation_angle = det_average_bearing(angle_previous, angle_next)
        elif self.sector_orientation == "next":
            self.orientation_angle = angle_next
        elif self.sector_orientation == "previous":
            self.orientation_angle = angle_previous
        elif self.sector_orientation == "start":
            self.orientation_angle = angle_start
        else:
            raise ValueError("Unknown sector orientation: %s " % self.sector_orientation)

    @staticmethod
    def cuc_sector_dimensions(LSEEYOU_line):
        components = LSEEYOU_line.rstrip().split(",")
        r_min = None
        angle_min = None
        r_max = None
        angle_max = None
        for component in components:
            if component.startswith("R1="):
                r_max = int(component.split("=")[1][:-1])
            elif component.startswith("A1="):
                angle_max = int(component.split("=")[1])
            elif component.startswith("R2="):
                r_min = int(component.split("=")[1][:-1])
            elif component.startswith("A2="):
                angle_min = int(component.split("=")[1])
        return r_min, angle_min, r_max, angle_max

    def inside_sector(self, fix):

        fix_lat, fix_lon = det_lat_long(fix, 'pnt')

        distance = calculate_distance2(fix_lat, fix_lon, self.lat, self.lon)
        bearing = calculate_bearing(self.lat, self.lon, fix_lat, fix_lon)

        angle_wrt_orientation = abs(det_bearing_change(self.orientation_angle, bearing))

        if self.line:
            print 'Calling inside_sector on a line!'
            exit(1)
        elif self.r_min is not None:
            inside_outer_sector = self.r_min < distance < self.r_max and angle_wrt_orientation < self.angle_max
            inside_inner_sector = distance < self.r_min and angle_wrt_orientation < self.angle_min
            return inside_outer_sector or inside_inner_sector
        else:  # self.r_min is None
            return distance < self.r_max and (pi - angle_wrt_orientation) < self.angle_max

    def outside_sector(self, fix):
        return not self.inside_sector(fix)

    def crossed_line(self, fix1, fix2):

        fix1_lat, fix1_lon = det_lat_long(fix1, 'pnt')
        fix2_lat, fix2_lon = det_lat_long(fix2, 'pnt')

        distance1 = calculate_distance2(fix1_lat, fix1_lon, self.lat, self.lon)
        distance2 = calculate_distance2(fix2_lat, fix2_lon, self.lat, self.lon)

        if not self.line:
            print 'Calling crossed_line on a sector!'
            exit(1)
        else:
            if distance2 > self.r_max and distance1 > self.r_max:
                return False
            else:  # either both within circle or only one, leading to small amount of false positives
                bearing1 = calculate_bearing(self.lat, self.lon, fix1_lat, fix1_lon)
                bearing2 = calculate_bearing(self.lat, self.lon, fix2_lat, fix2_lon)

                angle_wrt_orientation1 = abs(det_bearing_change(self.orientation_angle, bearing1))
                angle_wrt_orientation2 = abs(det_bearing_change(self.orientation_angle, bearing2))

                if self.sector_orientation == "next":  # start line
                    return angle_wrt_orientation1 < 90 < angle_wrt_orientation2
                elif self.sector_orientation == "previous":  # finish line
                    return angle_wrt_orientation2 < 90 < angle_wrt_orientation1
                else:
                    print "A line with this orientation is not implemented!"
                    exit(1)

    @classmethod
    def from_scs(cls):
        raise NotImplementedError()

    @classmethod
    def from_cuc(cls, LCU_line, LSEEYOU_line):

        name = LCU_line[23::]
        lat, lon = det_lat_long(LCU_line, 'tsk')
        r_min, angle_min, r_max, angle_max = cls.cuc_sector_dimensions(LSEEYOU_line)

        sector_orientation = cls.cuc_sector_orientation(LSEEYOU_line)
        if sector_orientation == 'fixed':
            orientation_angle = cls.cuc_fixed_orientation_angle(LSEEYOU_line)
        else:
            orientation_angle = None

        distance_correction = cls.cuc_distance_correction(LSEEYOU_line)

        line = 'Line=1\n' in LSEEYOU_line.split(',') or 'Line=1' in LSEEYOU_line.split(',')

        return cls(name, lat, lon, r_min, angle_min, r_max, angle_max, orientation_angle,
                   line, sector_orientation, distance_correction)


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
