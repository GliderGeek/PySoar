import platform
import os
import subprocess

from mechanize import Browser
from BeautifulSoup import BeautifulSoup
from settingsClass import Settings
from datetime import date
from math import radians, degrees, sin, cos, atan2, pi
from numpy import isclose

from pygeodesy.ellipsoidalVincenty import LatLon

settings = Settings()


def det_local_time(b_record, utc_to_local):
    return hhmmss2ss(b_record[1:3] + ':' + b_record[3:5] + ':' + b_record[5:7], utc_to_local)


def dms2dd(dms):
    cardinal = dms[-1]
    if cardinal in ('N', 'S'):
        dd = float(dms[0:2]) + ((float(dms[2:4]) + (float(dms[4:7]) / 1000.0)) / 60.0)
    else:
        dd = float(dms[0:3]) + ((float(dms[3:5]) + (float(dms[5:8]) / 1000.0)) / 60.0)
    if cardinal in ('S', 'W'):
        dd *= -1
    return dd


def dd2dm(dd, lat_lon_str):
    if dd < 0:
        if lat_lon_str == "lat":
            cardinal = "S"
        elif lat_lon_str == "lon":
            cardinal = "W"
        else:
            raise ValueError('Unsupported cardinal')

    else:
        if lat_lon_str == "lat":
            cardinal = "N"
        elif lat_lon_str == "lon":
            cardinal = "E"
        else:
            raise ValueError('Unsupported cardinal')

    d = int(abs(dd))
    m = (abs(dd) - d)*60
    mm = int(m)
    mm_thousands = int((m - mm) * 1000)

    if lat_lon_str == "lat":
        return "%02d%02d%03d%s" % (d, mm, mm_thousands, cardinal)
    elif lat_lon_str == "lon":
        return "%03d%02d%03d%s" % (d, m, mm_thousands, cardinal)


def det_time_difference(location_record1, location_record2, record_type1, record_type2):
    if record_type1 == 'tsk' or record_type2 == 'tsk':
        exit('only implemented for pnt record types!')

    return det_local_time(location_record2, 0) - det_local_time(location_record1, 0)


def det_velocity(location_record1, location_record2, record_type1, record_type2):
    if record_type1 == 'tsk' or record_type2 == 'tsk':
        exit('only implemented for pnt record types!')

    dist = calculate_distance(location_record1, location_record2, record_type1, record_type2)
    delta_t = det_time_difference(location_record1, location_record2, record_type1, record_type2)

    return dist/delta_t


def det_lat_long(location_record, record_type, return_radians=True):

    pnt_lat = 7
    pnt_long = 15
    tsk_lat = 6
    tsk_long = 14

    if record_type == 'pnt':
        latitude_dms = location_record[pnt_lat:pnt_lat+8]
        longitude_dms = location_record[pnt_long:pnt_long+8]
    elif record_type == 'tsk':
        latitude_dms = location_record[tsk_lat:tsk_lat+8]
        longitude_dms = location_record[tsk_long:tsk_long+8]
    else:
        raise ValueError('Unsupported record_type')

    if return_radians:
        return radians(dms2dd(latitude_dms)), radians(dms2dd(longitude_dms))
    else:
        return dms2dd(latitude_dms), dms2dd(longitude_dms)


def determine_destination(location_record, record_type, bearing, distance):
    start_lat, start_lon = det_lat_long(location_record, record_type, return_radians=False)
    start_latlon = LatLon(start_lat, start_lon)

    return start_latlon.destination(distance, bearing)


def calculate_distance(location_record1, location_record2, record_type1, record_type2):
    loc1_lat, loc1_lon = det_lat_long(location_record1, record_type1, return_radians=False)
    loc1_lat_lon = LatLon(loc1_lat, loc1_lon)

    loc2_lat, loc2_lon = det_lat_long(location_record2, record_type2, return_radians=False)
    loc2_lat_lon = LatLon(loc2_lat, loc2_lon)

    # pygeodesy raises exception when same locations are used
    if isclose(loc1_lat, loc2_lat) and isclose(loc1_lon, loc2_lon):
        return 0

    return loc1_lat_lon.distanceTo(loc2_lat_lon)


def det_bearing(location_record1, location_record2, type1, type2):

    latitude1, longitude1 = det_lat_long(location_record1, type1)
    latitude2, longitude2 = det_lat_long(location_record2, type2)

    bearing = degrees(
        atan2(
            sin(longitude2 - longitude1) * cos(latitude2),
            cos(latitude1) * sin(latitude2)
            - sin(latitude1) * cos(latitude2) * cos(longitude2 - longitude1)
        ) % (2 * pi)
    )

    return bearing


# normal det_bearing function calculates initial bearing
def det_final_bearing(location_record1, location_record2, type1, type2):
    reversed_bearing = det_bearing(location_record2, location_record1, type2, type1)
    return (reversed_bearing + 180) % 360


def det_bearing_change(bearing1, bearing2):
    # always return difference between -180 and +180 degrees
    difference = bearing2 - bearing1
    if -180 < difference < 180:
        return difference
    elif difference <= -180:
        return difference + 360
    elif difference >= 180:
        return difference - 360


def det_bearing_change_rad(bearing1, bearing2):
    # always return difference between -pi and +pi radians
    difference = bearing2 - bearing1
    if -pi < difference < pi:
        return difference
    elif difference <= -pi:
        return difference + 2*pi
    elif difference >= pi:
        return difference - 2*pi


def det_height(b_record, gps_altitude):
    return int(b_record[30:35]) if gps_altitude else int(b_record[25:30])


def hhmmss2ss(time_string, utc_to_local):
    return (
        int(time_string[0:2]) + int(utc_to_local)) * 3600+\
        int(time_string[3:5]) * 60 +\
        int(time_string[6:8])


def ss2hhmmss(time_ss, colon=True):

    if time_ss is None:
        return None

    seconds = (time_ss % 3600) % 60
    minutes = ((time_ss % 3600) - seconds) / 60
    hours = (time_ss - (time_ss % 3600)) / 3600

    if colon:
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    else:
        return "%02d%02d%02d" % (hours, minutes, seconds)


def url_is_aat(url):
    mech = Browser()
    mech.set_handle_robots(False)
    page = mech.open(url)
    html = page.read()
    soup = BeautifulSoup(html)
    spans = soup.findAll("span")

    for span in spans:
        if span.text == 'Task duration:':
            return True
    return False


def task_url_from_daily(daily_url):
    split_daily = daily_url.split("/")
    split_daily.remove("daily")
    for index, item in enumerate(split_daily):
        if item == "results":
            split_daily[index] = "tasks"

    task_url = "/".join(split_daily)
    return task_url


def url_format_correct(url_string):
    if (url_string[0:26] != "http://www.soaringspot.com" and url_string[0:21] != "http://www.strepla.de") :        
        return 'URL should start with http://www.soaringspot.com'
    elif (url_string[-5::] != 'daily' and url_string[33:41] != 'scoreDay'): 
        return 'URL does not give daily results'
    else:
        return 'URL correct'


def go_bugform(url_entry, event):
    import webbrowser

    form_url = settings.debug_form_url
    versionID = settings.pysoar_version_formID
    urlID = settings.competition_url_formID
    pysoar_version = settings.version

    comp_url = url_entry.get()

    complete_url = '%s?entry.%s=%s&entry.%s=%s' % (form_url, versionID, pysoar_version, urlID, comp_url)
    webbrowser.open(complete_url)


def print_array_debug(text_file, array_name, array):
    text_file.write(array_name + " \n")
    for ii in range(len(array)):
        text_file.write(str(array[ii])+"\n")
    text_file.write("\n")


def open_analysis_file():

    if platform.system() == "Darwin":
        subprocess.call(["open", settings.file_name])
    elif platform.system() == "Linux":
        subprocess.call(["xdg-open", settings.file_name])
    elif platform.system() == "Windows":
        os.startfile(settings.file_name)


def determine_flown_task_distance(_leg, b_record, competition_day):

    task_distance = 0
    for leg in range(_leg-1):
        task_distance += competition_day.task.distances[leg]

    previous_tp = competition_day.task.taskpoints[_leg-1].LCU_line
    next_tp = competition_day.task.taskpoints[_leg].LCU_line

    bearing1 = det_bearing(previous_tp, next_tp, 'tsk', 'tsk')
    bearing2 = det_bearing(previous_tp, b_record, 'tsk', 'pnt')
    angle_task_point = det_bearing_change(bearing1, bearing2) * pi / 180

    temp_distance = calculate_distance(previous_tp, b_record, 'tsk', 'pnt')
    return (task_distance + cos(angle_task_point)*temp_distance) / 1000


def used_engine(flight, i):
    if not flight.ENL:
        return False
    else:
        ENL_start_byte = flight.ENL_indices[0]
        ENL_end_byte = flight.ENL_indices[1]

        ENL_value = int(flight.trace[i][ENL_start_byte-1:ENL_end_byte])
        if ENL_value < settings.ENL_value_threshold:
            return False
        else:
            time_now = det_local_time(flight.trace[i], 0)
            i -= 1
            time = det_local_time(flight.trace[i], 0)
            while time_now - time < settings.ENL_time_threshold:

                ENL_value = int(flight.trace[i][ENL_start_byte-1:ENL_end_byte])
                if ENL_value < settings.ENL_value_threshold:
                    return False

                i -= 1
                time = det_local_time(flight.trace[i], 0)

            print "ENL land out at i=%s, t=%s" % (i, ss2hhmmss(time))
            print ENL_value
            return True


def enl_value_exceeded(fix, enl_indices):
    enl_value_threshold = 500
    enl_value = int(fix[enl_indices[0] - 1:enl_indices[1]])
    return enl_value > enl_value_threshold


def enl_time_exceeded(enl_time):
    enl_time_threshold = 30
    return enl_time >= enl_time_threshold


def determine_engine_start_i(flight, i):

    time_last = det_local_time(flight.trace[i], 0)
    i -= 1
    time = det_local_time(flight.trace[i], 0)
    while time_last - time < settings.ENL_time_threshold:
        i -= 1
        time = det_local_time(flight.trace[i], 0)

    return i


def det_average_bearing(bearing1, bearing2):

    sin_a = sin(bearing1 * pi / 180)
    sin_b = sin(bearing2 * pi / 180)
    cos_a = cos(bearing1 * pi / 180)
    cos_b = cos(bearing2 * pi / 180)

    avg_bearing = atan2(sin_a + sin_b, cos_a + cos_b) * 180 / pi
    return (avg_bearing + 360) % 360


def create_b_record(time_s, lat_dd, lon_dd, altitude_baro, altitude_gps):
    b_record = "B"
    b_record += ss2hhmmss(time_s, colon=False)
    b_record += dd2dm(lat_dd, "lat")
    b_record += dd2dm(lon_dd, "lon")
    b_record += "A"
    b_record += "%05d" % altitude_baro
    b_record += "%05d" % altitude_gps
    return b_record


def interpolate_b_records(b_record1, b_record2):
    b_records = [b_record1]

    time1 = det_local_time(b_record1, 0)
    time2 = det_local_time(b_record2, 0)
    lat1, lon1 = det_lat_long(b_record1, 'pnt')
    lat2, lon2 = det_lat_long(b_record2, 'pnt')
    height1_baro = det_height(b_record1, False)
    height1_gps = det_height(b_record1, True)
    height2_baro = det_height(b_record2, False)
    height2_gps = det_height(b_record2, True)

    dtime = time2-time1
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    dheight_baro = height2_baro - height1_baro
    dheight_gps = height2_gps - height1_gps

    for index in range(dtime-1):
        fraction = float(index+1) / dtime
        time_s = time1 + int(fraction*dtime)
        lat = lat1 + fraction*d_lat
        lon = lon1 + fraction*d_lon
        lat_dd = lat * 180 / pi
        lon_dd = lon * 180 / pi
        height_baro = height1_baro + fraction*dheight_baro
        height_gps = height1_gps + fraction*dheight_gps

        b_record = create_b_record(time_s, lat_dd, lon_dd, height_baro, height_gps)
        b_records.append(b_record)

    b_records.append(b_record2)
    return b_records


def get_date(lcu_line):
    date_raw = lcu_line[6:12]

    year = int(date_raw[4::])
    year = 1900+year if year > 90 else 2000+year
    month = int(date_raw[2:4])
    day = int(date_raw[0:2])

    return date(year, month, day)

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
