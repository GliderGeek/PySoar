class Performance(object):
    def __init__(self, competition_day, flight):
        if competition_day.aat:
            print 'AAT nog yet implemented'
        else:
            self.determine_task_times(competition_day, flight)

    def determine_task_times(self, competition_day, flight):
        pass

if __name__ == '__main__':
    from main import run

    run()
