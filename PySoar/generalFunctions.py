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


def determine_distance(location_record1, location_record2, type1, type2):
    from math import sin, cos, asin, sqrt

    latitude1, longitude1 = det_lat_long(location_record1, type1)
    latitude2, longitude2 = det_lat_long(location_record2, type2)

    dist = 2 * asin(
        sqrt((sin((latitude1 - latitude2) / 2)) ** 2
             + cos(latitude1) * cos(latitude2) * (sin((longitude1 - longitude2) / 2)) ** 2
             )
    ) * settings.earth_radius * 1000

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
        return difference - 60


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
    if determine_distance(b_record, competition_day.task[leg+2], 'pnt', 'tsk') < competition_day.tp_radius[leg]:
        return True
    else:
        return False


if __name__ == '__main__':
    from main import run

    run()
