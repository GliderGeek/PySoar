class Trip(object):

    def __init__(self, task, trace, trace_settings):
        self.distances = []
        self.fixes = []
        self.start_fixes = []

        self.enl_fix = None
        self.outlanding_fix = None

        task.apply_rules(trace, self, trace_settings)

    def outlanding_leg(self):
        return len(self.fixes) - 1

    def outlanded(self):
        return self.outlanding_fix is not None
