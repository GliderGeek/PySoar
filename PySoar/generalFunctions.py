from mechanize import Browser
from BeautifulSoup import BeautifulSoup
from settingsClass import Settings
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


def det_time_difference(location_record1, location_record2, record_type1, record_type2):
    if record_type1 == 'tsk' or record_type2 == 'tsk':
        exit('only implemented for pnt record types!')

    return det_local_time(location_record2, 0) - det_local_time(location_record1, 0)


def det_velocity(location_record1, location_record2, record_type1, record_type2):
    if record_type1 == 'tsk' or record_type2 == 'tsk':
        exit('only implemented for pnt record types!')

    dist = determine_distance(location_record1, location_record2, record_type1, record_type2)
    delta_t = det_time_difference(location_record1, location_record2, record_type1, record_type2)

    return dist/delta_t


def det_lat_long(location_record, record_type):
    from math import radians

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

    return radians(dms2dd(latitude_dms)), radians(dms2dd(longitude_dms))


def determine_distance(location_record1, location_record2, record_type1, record_type2):
    from math import sin, cos, asin, sqrt, atan2, pi, copysign, atan, tan, isnan

    # in radians
    phi1, labda1 = det_lat_long(location_record1, record_type1)
    phi2, labda2 = det_lat_long(location_record2, record_type2)

    if settings.distance_method == "FAI sphere":
        dist = 2 * asin(
            sqrt((sin((phi1 - phi2) / 2)) ** 2
                 + cos(phi1) * cos(phi2) * (sin((labda1 - labda2) / 2)) ** 2
                 )
        ) * settings.FAI_sphere_radius * 1000

    elif settings.distance_method == "WGS84 elipse":
    # adapted from http://www.movable-type.co.uk/scripts/latlong-vincenty.html

        a = settings.WGS84_mayor_axis
        b = settings.WGS84_minor_axis

        f = (a-b) / a

        L = labda2 - labda1
        tanU1 = (1-f) * tan(phi1)
        cosU1 = 1 / sqrt((1 + tanU1*tanU1))
        sinU1 = tanU1 * cosU1
        tanU2 = (1-f) * tan(phi2)
        cosU2 = 1 / sqrt((1 + tanU2*tanU2))
        sinU2 = tanU2 * cosU2

        labda = L
        labda_new = 0.  # initialization
        iterationLimit = 100
        while True:
            sin_lab = sin(labda)
            cos_lab = cos(labda)
            sinSq_sigma = (cosU2*sin_lab) * (cosU2*sin_lab) + (cosU1*sinU2-sinU1*cosU2*cos_lab) * (cosU1*sinU2-sinU1*cosU2*cos_lab)
            sin_sigma = sqrt(sinSq_sigma)
            if (sin_sigma == 0):
                return 0
            cos_sig = sinU1*sinU2 + cosU1*cosU2*cos_lab
            sigma = atan2(sin_sigma, cos_sig)
            sin_alfa = cosU1 * cosU2 * sin_lab / sin_sigma
            cosSq_alfa = 1 - sin_alfa*sin_alfa
            cos2_sigmaM = cos_sig - 2*sinU1*sinU2/cosSq_alfa
            if (isnan(cos2_sigmaM)):
                cos2_sigmaM = 0  # equatorial line: cosSqsig=0 (paragraph6)
            C = f/16*cosSq_alfa*(4+f*(4-3*cosSq_alfa))
            labda_new = labda
            labda = L + (1-C) * f * sin_alfa * (sigma + C*sin_sigma*(cos2_sigmaM+C*cos_sig*(-1+2*cos2_sigmaM*cos2_sigmaM)))
            iterationLimit -= 1
            if iterationLimit <= 0 or abs(labda-labda_new) < 1e-12:
                break

        if (iterationLimit==0):
            print 'Formula failed to converge'

        uSq = cosSq_alfa * (a*a - b*b) / (b*b)
        A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
        B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
        delta_sigma = B*sin_sigma*(cos2_sigmaM+B/4*(cos_sig*(-1+2*cos2_sigmaM*cos2_sigmaM) - B/6*cos2_sigmaM*(-3+4*sin_sigma*sin_sigma)*(-3+4*cos2_sigmaM*cos2_sigmaM)))

        dist = b*A*(sigma-delta_sigma)

    return dist


def det_bearing(location_record1, location_record2, type1, type2):
    from math import sin, cos, atan2, radians, degrees, pi

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
    from math import pi
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


def ss2hhmmss(time_ss):
    seconds = (time_ss % 3600) % 60
    minutes = ((time_ss % 3600) - seconds) / 60
    hours = (time_ss - (time_ss % 3600)) / 3600

    if seconds < 10:
        seconds_str = '0' + str(int(seconds))
    else:
        seconds_str = str(int(seconds))

    if minutes < 10:
        min_str = '0' + str(int(minutes))
    else:
        min_str = str(int(minutes))

    hrs_str = str(int(hours))

    return hrs_str + ':' + min_str + ':' + seconds_str


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


def url_is_startline(daily_url):
    task_url = task_url_from_daily(daily_url)

    mech = Browser()
    mech.set_handle_robots(False)
    page = mech.open(task_url)
    html = page.read()
    soup = BeautifulSoup(html)

    table_rows = soup.findAll("table")[0].findAll("tr")
    start_observation = table_rows[1].findAll("td")[3].text

    return start_observation.startswith("Line")


def url_is_beercans(daily_url):
    task_url = task_url_from_daily(daily_url)

    mech = Browser()
    mech.set_handle_robots(False)
    page = mech.open(task_url)
    html = page.read()
    soup = BeautifulSoup(html)

    table_rows = soup.findAll("table")[0].findAll("tr")

    for row in range(2, len(table_rows)-2):
        tp_observation = table_rows[row].findAll("td")[3].text
        if tp_observation != "Cylinder R=0.50&nbsp;km":
            return False

    return True


def url_format_correct(url_string):
    print url_string[-5::]
    if url_string[0:26] != "http://www.soaringspot.com":
        return 'URL should start with http://www.soaringspot.com'
    elif url_string[-5::] != 'daily':
        return 'URL does not give daily results'
    elif url_is_aat(url_string):
        return 'AAT not yet implemented'
    elif not url_is_startline(url_string):
        return 'Start circle/sector has not been implemented'
    elif not url_is_beercans(url_string):
        return 'This type of turnpoint has not been implemented (only beercans)'
    else:
        return 'URL correct'


# todo: is this method still used? if not remove, else refactor with return False and return True
def correct_format(st_time_string):
    correct = 1

    if len(st_time_string) != 8:
        correct = 0
        print 'length is not ok'
    elif st_time_string[2:3] != ':' or st_time_string[2:3] != ':' or st_time_string[2:3] != ':':
        correct = 0
        print 'format is not correct'
    elif int(st_time_string[0:2]) < 0 or int(st_time_string[0:2]) >= 24:
        correct = 0
        print 'hours should be between 0 and 24'
    elif int(st_time_string[3:5]) < 0 or int(st_time_string[3:5]) >= 60 or int(st_time_string[6:8]) < 0 or int(
            st_time_string[6:8]) >= 60:
        correct = 0
        print 'minutes and seconds should be between 0 and 60'

    return correct


def start_refinement(competition_day, b_record1, b_record2):

    task_bearing = det_bearing(competition_day.task[2], competition_day.task[3], 'tsk', 'tsk')

    bearing_b_record1 = det_bearing(competition_day.task[2], b_record1, 'tsk', 'pnt')
    bearing_b_record2 = det_bearing(competition_day.task[2], b_record2, 'tsk', 'pnt')

    bearing_difference1 = abs(det_bearing_change(bearing_b_record1, task_bearing))
    bearing_difference2 = abs(det_bearing_change(bearing_b_record2, task_bearing))

    time_difference = det_local_time(b_record2, 0) - det_local_time(b_record1, 0)

    dbearing = (bearing_difference2-bearing_difference1)/time_difference
    for i in range(time_difference-1):
        bearing_difference = bearing_difference1 + (i+1)*dbearing
        if bearing_difference < 90:
            return - time_difference + i + 1

    return 0


def line_crossed(b_record1, b_record2, type_string, competition_day):
    if type_string == 'start':
        midpoint = competition_day.task[2]
        task_bearing = det_bearing(midpoint, competition_day.task[3], 'tsk', 'tsk')
        distance_to_midpoint = determine_distance(midpoint, b_record2, 'tsk', 'pnt')
        line_radius = competition_day.tp_radius[0]
    elif type_string == 'finish':
        midpoint = competition_day.task[-2]
        task_bearing = det_bearing(competition_day.task[-3], midpoint, 'tsk', 'tsk')
        distance_to_midpoint = determine_distance(midpoint, b_record2, 'tsk', 'pnt')
        line_radius = competition_day.tp_radius[-1]

    if distance_to_midpoint > line_radius:
        return False

    bearing_midpoint_record1 = det_bearing(midpoint, b_record1, 'tsk', 'pnt')
    bearing_midpoint_record2 = det_bearing(midpoint, b_record2, 'tsk', 'pnt')

    bearing_difference1 = abs(det_bearing_change(bearing_midpoint_record1, task_bearing))
    bearing_difference2 = abs(det_bearing_change(bearing_midpoint_record2, task_bearing))

    if bearing_difference1 > 90 > bearing_difference2:
        return True
    else:
        return False


def turnpoint_rounded(b_record, leg, competition_day):
    if determine_distance(b_record, competition_day.task[leg+3], 'pnt', 'tsk') < competition_day.tp_radius[leg+1]:
        return True
    else:
        return False


def print_array_debug(text_file, array_name, array):
    text_file.write(array_name + " \n")
    for ii in range(len(array)):
        text_file.write(str(array[ii])+"\n")
    text_file.write("\n")


def open_analysis_file():
    import platform
    import os
    import subprocess

    if platform.system() == "Darwin":
        subprocess.call(["open", settings.file_name])
    elif platform.system() == "Linux":
        subprocess.call(["xdg-open", settings.file_name])
    elif platform.system() == "Windows":
        os.startfile(settings.file_name)


def determine_flown_task_distance(_leg, b_record, competition_day):
    from math import cos, pi

    task_distance = 0
    for leg in range(_leg-1):
        task_distance += competition_day.task_dists[leg]

    previous_tp = competition_day.task[_leg+1]
    next_tp = competition_day.task[_leg+2]

    bearing1 = det_bearing(previous_tp, next_tp, 'tsk', 'tsk')
    bearing2 = det_bearing(previous_tp, b_record, 'tsk', 'pnt')
    angle_task_point = det_bearing_change(bearing1, bearing2) * pi / 180

    temp_distance = determine_distance(previous_tp, b_record, 'tsk', 'pnt')
    return (task_distance + cos(angle_task_point)*temp_distance) / 1000


def used_engine(flight, i):
    if not flight.ENL:
        return False
    else:
        ENL_start_byte = flight.ENL_indices[0]
        ENL_end_byte = flight.ENL_indices[1]

        ENL_value = int(flight.b_records[i][ENL_start_byte-1:ENL_end_byte])
        if ENL_value < settings.ENL_value_threshold:
            return False
        else:
            time_now = det_local_time(flight.b_records[i], 0)
            i -= 1
            time = det_local_time(flight.b_records[i], 0)
            while time_now - time < settings.ENL_time_threshold:

                ENL_value = int(flight.b_records[i][ENL_start_byte-1:ENL_end_byte])
                if ENL_value < settings.ENL_value_threshold:
                    return False

                i -= 1
                time = det_local_time(flight.b_records[i], 0)

            print "ENL land out at i=%s, t=%s" % (i, ss2hhmmss(time))
            print ENL_value
            return True


def determine_engine_start_i(flight, i):

    time_last = det_local_time(flight.b_records[i], 0)
    i -= 1
    time = det_local_time(flight.b_records[i], 0)
    while time_last - time < settings.ENL_time_threshold:
        i -= 1
        time = det_local_time(flight.b_records[i], 0)

    return i


if __name__ == '__main__':
    from main_pysoar import run

    run()
