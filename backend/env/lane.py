class Lane:

    def __init__(self, start, end, lane_id):

        self.start = start
        self.end = end
        self.lane_id = lane_id

        self.length = ((end[0]-start[0])**2 + (end[1]-start[1])**2)**0.5

        self.next_lanes = []

    def connect(self, lane):
        self.next_lanes.append(lane)

    def interpolate(self, t):

        x = self.start[0] + (self.end[0]-self.start[0]) * t
        y = self.start[1] + (self.end[1]-self.start[1]) * t

        return x, y