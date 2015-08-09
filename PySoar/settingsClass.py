class Settings(object):

    def __init__(self, version, stand_alone_build):
        import platform

        self.version = version
        self.file_name = 'Analysis_PySoar.xls'
        if platform.system() == 'Darwin' and stand_alone_build:
            self.file_name = '../../../Analysis_PySoar.xls'

    turn_threshold_bearingRate = 6
    turn_threshold_bearingTot = 200

    glide_threshold_dist = 400
    glide_threshold_bearingRateAvg = 2
    glide_threshold_bearingRate = 6

    earth_radius = 6371

if __name__ == '__main__':
    from main import run
    run()
