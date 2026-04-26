from env.lane import Lane
import random


class LaneGraph:

    def __init__(self, cx, cy, width, height):

        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height

        self.lanes = []

        self.build_graph()

    def build_graph(self):

        cx = self.cx
        cy = self.cy

        half_w = self.width // 2
        half_h = self.height // 2
        spawn_offset = 100  # ensures vehicles spawn outside screen

        lane_w = 65

        # lane centers
        outer = 97
        inner = 32

        # SOUTH → NORTH
        s0 = Lane((cx-outer, cy + half_h + spawn_offset), (cx-outer, cy - half_h - spawn_offset), "S0")
        s1 = Lane((cx-inner, cy + half_h + spawn_offset), (cx-inner, cy - half_h - spawn_offset), "S1")

        # NORTH → SOUTH
        n0 = Lane((cx+outer, cy - half_h - spawn_offset), (cx+outer, cy + half_h + spawn_offset), "N0")
        n1 = Lane((cx+inner, cy - half_h - spawn_offset), (cx+inner, cy + half_h + spawn_offset), "N1")

        # WEST → EAST
        w0 = Lane((cx - half_w - spawn_offset, cy - outer), (cx + half_w + spawn_offset, cy - outer), "W0")
        w1 = Lane((cx - half_w - spawn_offset, cy - inner), (cx + half_w + spawn_offset, cy - inner), "W1")

        # EAST → WEST
        e0 = Lane((cx + half_w + spawn_offset, cy + outer), (cx - half_w - spawn_offset, cy + outer), "E0")
        e1 = Lane((cx + half_w + spawn_offset, cy + inner), (cx - half_w - spawn_offset, cy + inner), "E1")

        self.lanes = [s0,s1,n0,n1,w0,w1,e0,e1]

        # connect lanes
        s0.connect(w0)
        s0.connect(n0)
        s0.connect(e0)

        s1.connect(w1)
        s1.connect(n1)
        s1.connect(e1)

        n0.connect(e0)
        n0.connect(s0)
        n0.connect(w0)

        n1.connect(e1)
        n1.connect(s1)
        n1.connect(w1)

        w0.connect(n0)
        w0.connect(e0)
        w0.connect(s0)

        w1.connect(n1)
        w1.connect(e1)
        w1.connect(s1)

        e0.connect(s0)
        e0.connect(w0)
        e0.connect(n0)

        e1.connect(s1)
        e1.connect(w1)
        e1.connect(n1)

    def random_lane(self):
        return random.choice(self.lanes)