import random
import math

from env.config import LANE_MODE
from drl2.policy import DRLPolicy
from drl2.state import StateEncoder


class VehicleController:

    def __init__(self, vehicle, lane, graph, simulation):

        self.vehicle = vehicle
        self.lane = lane
        self.graph = graph
        self.simulation = simulation   # ✅ NEW
        self.t = 0

        self.stopped = False

        self.desired_speed = vehicle.speed 
        self.current_speed = vehicle.speed

        self.lane_changing = False
        self.target_lane = None
        self.lane_change_progress = 0
        self.lane_change_speed = 0.035

        if vehicle.vehicle_type == "truck":
            self.safe_distance = 45   # reduced hesitation → quicker response
        elif vehicle.vehicle_type == "car":
            self.safe_distance = 45
        else:
            self.safe_distance = 45

        self.vehicle.lane_change_cooldown = 0

        self.front_vehicle = None
        self.front_distance = None

        self.drl_policy = None
        self.drl_encoder = None

        # logging throttles
        self.log_timer = 0
        self.detect_timer = 0

        # ✅ NEW
        self.msg_timer = 0

        # ✅ NEW: message cooldown counter
        self.msg_cooldown_counter = 0

        # ✅ NEW: message inbox
        self.inbox = []

        self.seen_message_ids = set()
        self.vehicle_id = id(self.vehicle)

        # ✅ QoS TRACKING (EMERGENCY VEHICLES ONLY)
        self.qos_log = []
        self.qos_active = False
        self.qos_timer = 0
        self.qos_started = False

    # --------------------------------------------------
    # TERMINAL LOGGING
    # --------------------------------------------------

    def print_emv_detection(self):

        if not self.vehicle.is_emergency:
            return

        self.detect_timer += 1

        if self.detect_timer < 30:
            return

        self.detect_timer = 0

        distance_pixels = (1 - self.t) * self.lane.length
        distance = distance_pixels * 0.25
        speed = max(self.current_speed, 0.1)
        fps = 60
        eta = (distance / speed) / fps

        if not self.simulation.paused:
            print("\n================================================")
            print("             EMERGENCY VEHICLE DETECTED")
            print("------------------------------------------------")
            print(f"Agent                | {self.vehicle.vehicle_type.upper()}")
            print(f"Lane                 | {self.lane.lane_id}")
            print(f"Distance to Junction | {round(distance,2)} m")
            print(f"Estimated Arrival    | {round(eta,2)} sec")
            print("================================================\n")

    # --------------------------------------------------

    def print_emv_decision(self, state, action):

        action_map = {
            0: "KEEP LANE",
            1: "CHANGE LANE",
            2: "BRAKE",
            3: "ACCELERATE"
        }

        if not self.simulation.paused:
            print("\n================================================")
            print("        EMERGENCY VEHICLE AGENT DECISION")
            print("------------------------------------------------")
            print(f"Agent                | {self.vehicle.vehicle_type.upper()}")
            print(f"Current Lane         | {self.lane.lane_id}")
            print(f"Speed                | {round(self.current_speed,2)} m/s")
            print(f"Action ID            | {action}")
            print(f"Action Meaning       | {action_map.get(action,'UNKNOWN')}")
            print("================================================")

            print("\nSTATE VECTOR DESCRIPTION")
            print("[front_dist, rear_dist, vehicles_ahead, vehicles_behind, lane_density, blocked_time, speed, slow_vehicle_ahead, adjacent_lane_free, front_vehicle_type]")

            print("\nSTATE VECTOR VALUES")
            print(state)
            print("\n")

    # --------------------------------------------------

    def vehicle_priority(self, v):

        if v.vehicle_type == "truck":
            return 1
        if v.vehicle_type == "car":
            return 2
        if v.vehicle_type == "police":
            return 10
        if v.vehicle_type == "ambulance":
            return 12

        return 1

    # --------------------------------------------------

    def lane_weight(self, lane_id, vehicles):

        weight = 0

        for v, c in vehicles:

            if c.lane.lane_id == lane_id:
                weight += self.vehicle_priority(v)

        return weight

    # --------------------------------------------------

    def get_lane_by_id(self, lane_id):

        for lane in self.graph.lanes:
            if lane.lane_id == lane_id:
                return lane

        return None

    # --------------------------------------------------

    def get_adjacent_lane(self):

        lane_id = self.lane.lane_id

        if lane_id.endswith("0"):
            return lane_id[:-1] + "1"

        if lane_id.endswith("1"):
            return lane_id[:-1] + "0"

        return None

    # --------------------------------------------------

    def start_lane_change(self, target_lane):

        if self.lane_changing:
            return

        self.lane_changing = True
        self.target_lane = target_lane
        self.lane_change_progress = 0

    # --------------------------------------------------

    def apply_lane_change(self):

        self.lane_change_progress += self.lane_change_speed

        if self.lane_change_progress >= 1:

            self.lane = self.target_lane
            self.lane_changing = False
            self.target_lane = None
            self.lane_change_progress = 0
            return

        x1, y1 = self.lane.interpolate(self.t)
        x2, y2 = self.target_lane.interpolate(self.t)

        p = self.lane_change_progress

        self.vehicle.x = (1 - p) * x1 + p * x2
        self.vehicle.y = (1 - p) * y1 + p * y2

    # --------------------------------------------------

    def drl_lane_decision(self, vehicles):

        if self.drl_policy is None:
            self.drl_policy = DRLPolicy()
            self.drl_encoder = StateEncoder()

        state = self.drl_encoder.encode(self, vehicles)
        action = self.drl_policy.act(state)

        self.log_timer += 1
        if self.log_timer >= 20:
            self.print_emv_decision(state, action)
            self.log_timer = 0

        if self.front_vehicle and self.front_distance:

            if self.front_distance < 100:

                if self.front_vehicle.vehicle_type in ["car", "truck"]:

                    if self.adjacent_lane_safe(vehicles):

                        if self.vehicle.lane_change_cooldown == 0:

                            target_lane = self.get_lane_by_id(
                                self.get_adjacent_lane()
                            )

                            if target_lane:

                                self.start_lane_change(target_lane)
                                self.vehicle.lane_change_cooldown = 120
                                return

        if action == 1:

            if self.front_vehicle is None:
                return

            if self.front_distance is None:
                return

            if self.front_distance > 120:
                return

            if self.vehicle.lane_change_cooldown > 0:
                return

            if self.adjacent_lane_safe(vehicles):

                target_lane = self.get_lane_by_id(
                    self.get_adjacent_lane()
                )

                if target_lane:
                    self.start_lane_change(target_lane)
                    self.vehicle.lane_change_cooldown = 120

        elif action == 2:
            self.current_speed *= 0.7

        elif action == 3:
            # Increased acceleration for faster gap creation
            self.current_speed = min(
                self.current_speed * 1.3,#1.3   # faster boost
                self.desired_speed * 2.0 #2.0   # higher speed cap
            )

    # --------------------------------------------------

    def vehicle_ahead(self, vehicles):

        nearest = None
        nearest_vehicle = None

        for v, c in vehicles:

            if c is self:
                continue

            if c.lane == self.lane and c.t > self.t:

                d = (c.t - self.t) * self.lane.length

                if nearest is None or d < nearest:
                    nearest = d
                    nearest_vehicle = v

        self.front_vehicle = nearest_vehicle
        self.front_distance = nearest

        return nearest

    # --------------------------------------------------

    def adjacent_lane_safe(self, vehicles):

        target_lane_id = self.get_adjacent_lane()

        if target_lane_id is None:
            return False

        for v, c in vehicles:

            if c is self:
                continue

            if c.lane.lane_id != target_lane_id:
                continue

            d = abs((c.t - self.t) * self.lane.length)

            if d < self.safe_distance:
                return False

        return True

    # --------------------------------------------------

    def emergency_vehicle_behind(self, vehicles):

        for v, c in vehicles:

            if c is self:
                continue

            if not (v.is_emergency or v.vehicle_type == "police"):
                continue

            if c.lane.lane_id[0] != self.lane.lane_id[0]:
                continue

            if c.t < self.t:

                d = (self.t - c.t) * self.lane.length

                if d < 250:
                    return True

        return False

    # --------------------------------------------------
    # GET NEAREST EMV BEHIND
    # --------------------------------------------------
    def get_nearest_emv_behind(self, vehicles):
        nearest = None
        nearest_dist = float("inf")

        for v, c in vehicles:
            if c is self:
                continue

            if not v.is_emergency:
                continue

            if c.lane.lane_id[0] != self.lane.lane_id[0]:
                continue

            if c.t < self.t:
                d = (self.t - c.t) * self.lane.length

                if d < nearest_dist:
                    nearest_dist = d
                    nearest = v

        return nearest

    # --------------------------------------------------

    # --------------------------------------------------
    #  PROCESS INCOMING MESSAGES
    # --------------------------------------------------
    def process_messages(self):

        if not self.inbox:
            return

        for msg in self.inbox:

            msg_id = msg.get("msg_id")

            if msg_id in self.seen_message_ids:
                continue

            self.seen_message_ids.add(msg_id)

            if len(self.seen_message_ids) > 200:
                self.seen_message_ids.clear()

            sender = msg.get("sender", None)
            msg_type = msg.get("msg_type", "")
            distance = msg.get("distance", 0)

            # 🔥 For now ONLY LOG (no behavior change)
            if msg_type in ["EMV", "EMV_HOP"]:
                self.vehicle.received_emv = True
                self.vehicle.emv_hop_count = msg.get("hop_count", 0)

        # clear after processing
        self.inbox.clear()

    # --------------------------------------------------
    # DENSITY-BASED MESSAGE FREQUENCY
    # --------------------------------------------------
    def get_local_density(self, vehicles):
        """
        Count nearby vehicles within local radius (120m)
        Higher density = more congested area
        """
        count = 0
        for v, ctrl in vehicles:
            if v == self.vehicle:
                continue

            dx = v.x - self.vehicle.x
            dy = v.y - self.vehicle.y
            dist = (dx*dx + dy*dy) ** 0.5

            if dist <= 120:
                count += 1

        return count

    # --------------------------------------------------
    #  ADAPTIVE BROADCAST RADIUS
    # --------------------------------------------------
    def get_adaptive_radius(self, vehicles):
        density = self.get_local_density(vehicles)

        if density > 8:
            return 80   # high density (was too small before)
        elif density > 4:
            return 100  # medium density
        else:
            return 120  # low density

    # --------------------------------------------------

    def is_in_safe_zone(self, vehicle):
        cx = self.simulation.road.cx
        cy = self.simulation.road.cy

        left = cx - self.simulation.road.SAFE_LEFT_OFFSET
        right = cx + self.simulation.road.SAFE_RIGHT_OFFSET
        top = cy - self.simulation.road.SAFE_TOP_OFFSET
        bottom = cy + self.simulation.road.SAFE_BOTTOM_OFFSET

        # STOP LINES (IMPORTANT)
        west_stop_x = cx - 60
        east_stop_x = cx + 60
        north_stop_y = cy - 60
        south_stop_y = cy + 60

        x = vehicle.x
        y = vehicle.y
        lane = self.lane.lane_id

        if lane.startswith("W"):
            return left <= x <= west_stop_x

        elif lane.startswith("E"):
            return east_stop_x <= x <= right

        elif lane.startswith("N"):
            return top <= y <= north_stop_y

        elif lane.startswith("S"):
            return south_stop_y <= y <= bottom

        return False

    # --------------------------------------------------

    def is_inside_emv_range(self, vehicle, emv):
        dx = vehicle.x - emv.x
        dy = vehicle.y - emv.y
        distance = (dx * dx + dy * dy) ** 0.5

        EMV_RADIUS = 120   # adjust if needed
        return distance <= EMV_RADIUS

    # --------------------------------------------------

    def get_signal_target(self):
        cx = self.simulation.road.cx
        cy = self.simulation.road.cy

        road_half = self.simulation.road.road_width // 2
        lane_w = self.simulation.road.lane_width

        # small adjustment to reach signal center
        SIGNAL_SHIFT = lane_w // 2 - 80

        lane = self.lane.lane_id

        # WEST signal
        if lane.startswith("W"):
            return cx - road_half - SIGNAL_SHIFT, cy

        # EAST signal
        elif lane.startswith("E"):
            return cx + road_half + SIGNAL_SHIFT, cy

        # NORTH signal
        elif lane.startswith("N"):
            return cx, cy - road_half - SIGNAL_SHIFT

        # SOUTH signal
        elif lane.startswith("S"):
            return cx, cy + road_half + SIGNAL_SHIFT

        return cx, cy

    # --------------------------------------------------

    def is_before_stop_line(self, vehicle):
        cx = self.simulation.road.cx
        cy = self.simulation.road.cy

        west_stop_x = cx - 60
        east_stop_x = cx + 60
        north_stop_y = cy - 60
        south_stop_y = cy + 60

        x = vehicle.x
        y = vehicle.y
        lane = self.lane.lane_id

        if lane.startswith("W"):
            return x <= west_stop_x
        elif lane.startswith("E"):
            return x >= east_stop_x
        elif lane.startswith("N"):
            return y <= north_stop_y
        elif lane.startswith("S"):
            return y >= south_stop_y

        return False

    # --------------------------------------------------

    def cooperative_yield(self, vehicles):

        if not self.emergency_vehicle_behind(vehicles):
            return

        adj = self.get_adjacent_lane()

        if adj is None:
            return

        w1 = self.lane_weight(self.lane.lane_id, vehicles)
        w2 = self.lane_weight(adj, vehicles)

        if w1 < w2:
            # current lane lighter → slow down
            self.current_speed *= 0.6

        elif w1 > w2:
            # current lane heavier → speed up
            self.current_speed = min(
                self.current_speed * 1.4,
                self.desired_speed * 1.5
            )

        else:
            # tie case → decide based on position (t value)

            # vehicle closer to intersection should speed up
            if self.t > 0.5:
                self.current_speed = min(
                    self.current_speed * 1.3,
                    self.desired_speed * 1.5
                )
            else:
                self.current_speed *= 0.6

    # --------------------------------------------------

    def find_best_forward_vehicle(self, vehicles):

        cx = self.simulation.road.cx
        cy = self.simulation.road.cy

        # COUNT NEARBY VEHICLES (DENSITY)
        nearby_count = 0

        for v, ctrl in vehicles:

            if v == self.vehicle:
                continue

            dx = v.x - self.vehicle.x
            dy = v.y - self.vehicle.y
            dist = (dx*dx + dy*dy) ** 0.5

            if dist <= 120:
                nearby_count += 1

        # CLASSIFY DENSITY
        HIGH_DENSITY_THRESHOLD = 5

        is_high_density = nearby_count > HIGH_DENSITY_THRESHOLD

        # Initialize best_score based on density
        if is_high_density:
            best_score = float("inf")
        else:
            best_score = -1

        best_vehicle = None

        for v, ctrl in vehicles:

            if v == self.vehicle:
                continue

            dx = v.x - self.vehicle.x
            dy = v.y - self.vehicle.y
            dist = (dx*dx + dy*dy) ** 0.5

            if dist > 120:
                continue

            if ctrl.t <= self.t:
                continue

            # DENSITY-BASED SELECTION
            if is_high_density:
                # HIGH DENSITY → choose nearest vehicle
                if dist < best_score:
                    best_score = dist
                    best_vehicle = v
            else:
                # LOW DENSITY → choose farthest forward vehicle
                if dist > best_score:
                    best_score = dist
                    best_vehicle = v

        return best_vehicle

    # --------------------------------------------------

    def update(self, signal=None, vehicles=None):

        prev_x = self.vehicle.x
        prev_y = self.vehicle.y

        if self.vehicle.lane_change_cooldown > 0:
            self.vehicle.lane_change_cooldown -= 1

        self.print_emv_detection()

        # --------------------------------------------------
        # PROCESS RECEIVED MESSAGES FIRST (BEFORE LOGIC)
        # --------------------------------------------------
        self.process_messages()

        # --------------------------------------------------
        # USE DYNAMIC CENTER FROM ROAD
        # --------------------------------------------------
        cx = self.simulation.road.cx
        cy = self.simulation.road.cy

        # --------------------------------------------------
        #  UPDATED STOP POINTS (ALIGNED WITH CROSSWALK)
        # --------------------------------------------------
        STOP_LEFT   = cx - 150
        STOP_RIGHT  = cx + 150
        STOP_TOP    = cy - 150
        STOP_BOTTOM = cy + 150

        lane_id = self.lane.lane_id

        horizontal = ["W0", "W1", "E0", "E1"]
        vertical = ["N0", "N1", "S0", "S1"]

        x = self.vehicle.x
        y = self.vehicle.y

        self.vehicle.in_safe_zone = self.is_in_safe_zone(self.vehicle)

        if signal:

            if lane_id in ["W0","W1"] and not signal.is_horizontal_green():
                if x < STOP_LEFT and (x + self.current_speed) >= STOP_LEFT:
                    self.current_speed = 0
                    self.stopped = True
                    return

            if lane_id in ["E0","E1"] and not signal.is_horizontal_green():
                if x > STOP_RIGHT and (x - self.current_speed) <= STOP_RIGHT:
                    self.current_speed = 0
                    self.stopped = True
                    return

            if lane_id in ["N0","N1"] and not signal.is_vertical_green():
                if y < STOP_TOP and (y + self.current_speed) >= STOP_TOP:
                    self.current_speed = 0
                    self.stopped = True
                    return

            if lane_id in ["S0","S1"] and not signal.is_vertical_green():
                if y > STOP_BOTTOM and (y - self.current_speed) <= STOP_BOTTOM:
                    self.current_speed = 0
                    self.stopped = True
                    return

        if self.stopped:

            if lane_id in horizontal and signal.is_horizontal_green():
                self.stopped = False
            elif lane_id in vertical and signal.is_vertical_green():
                self.stopped = False
            else:
                return

        if vehicles:

            d = self.vehicle_ahead(vehicles)

            if d:

                #  HARD STOP (prevents overlap)
                if d < self.safe_distance * 0.6:
                    self.current_speed = 0
                    return

                elif d < self.safe_distance:
                    self.current_speed *= 0.8

            if d and d < self.safe_distance:

                self.current_speed *= 0.7

                if self.vehicle.is_emergency:
                    self.vehicle.blocked_time += 1

            else:

                self.current_speed = self.desired_speed
                self.vehicle.blocked_time = 0

        if vehicles and self.vehicle.is_emergency and LANE_MODE == "DRL":

            if not self.lane_changing:

                if self.vehicle.blocked_time > 12:

                    if self.adjacent_lane_safe(vehicles):

                        target_lane = self.get_lane_by_id(
                            self.get_adjacent_lane()
                        )

                        if target_lane:

                            self.start_lane_change(target_lane)
                            self.vehicle.blocked_time = 0

                else:

                    self.drl_lane_decision(vehicles)

        # --------------------------------------------------
        # COOPERATIVE YIELD + RESPONSE MESSAGE (FINAL)
        # --------------------------------------------------
        if vehicles and not self.vehicle.is_emergency:

            # Apply existing behavior (DO NOT MODIFY)
            self.cooperative_yield(vehicles)

            # --------------------------------------------------
            # DETECT COOPERATIVE YIELD STATE

            is_emv_near = self.emergency_vehicle_behind(vehicles)

            is_yielding_now = (
                is_emv_near and 
                self.current_speed < self.desired_speed
            )

            # --------------------------------------------------
            # SEND RESPONSE ONLY ON STATE CHANGE
            # --------------------------------------------------

            if (
                hasattr(self.vehicle, "received_emv") and self.vehicle.received_emv
                and is_yielding_now
                and not self.vehicle.was_yielding
                and not self.vehicle.response_sent
            ):

                target_emv = self.get_nearest_emv_behind(vehicles)

                if target_emv:

                    self.simulation.channel.broadcast(
                        self.vehicle,
                        target_emv.x,
                        target_emv.y,
                        msg_type="AV_RESPONSE",
                        vehicles=None,
                        radius=80
                    )

                    print(f"🔥 AV {self.vehicle_id} responding via cooperative yield")

                    self.vehicle.response_sent = True

            # --------------------------------------------------
            # UPDATE STATE TRACKING
            # --------------------------------------------------

            self.vehicle.was_yielding = is_yielding_now

            # --------------------------------------------------
            # RESET WHEN EVENT ENDS
            # --------------------------------------------------

            if not is_emv_near:
                self.vehicle.response_sent = False

        safe_lane_zone = 0.15 < self.t < 0.85

        if vehicles and not self.vehicle.is_emergency and safe_lane_zone:

            if not self.lane_changing and self.vehicle.lane_change_cooldown == 0:

                if self.front_vehicle and self.front_distance < 120:

                    if self.front_distance < self.safe_distance * 2:

                        if self.adjacent_lane_safe(vehicles):

                            target_lane = self.get_lane_by_id(
                                self.get_adjacent_lane()
                            )

                            if target_lane:

                                self.start_lane_change(target_lane)
                                self.vehicle.lane_change_cooldown = 120

        self.t += self.current_speed / self.lane.length

        # --------------------------------------------------
        # QoS TRACKING START (LANE ENTRY DETECTION)
        # --------------------------------------------------
        if self.vehicle.is_emergency and not self.qos_started:
            if self.t < 0.05:
                self.qos_active = True
                self.qos_started = True

        # --------------------------------------------------
        # QoS DATA COLLECTION (5 SAMPLES)
        # --------------------------------------------------
        if self.vehicle.is_emergency and self.qos_active:
            self.qos_timer += 1

            # sample every fixed interval
            if self.qos_timer % 40 == 0 and len(self.qos_log) < 5:
                # -------------------------------
                # RANGE (adaptive)
                # -------------------------------
                radius_px = self.get_adaptive_radius(vehicles) if vehicles else 120
                range_m = radius_px * 0.25

                # -------------------------------
                # PACKET RATE
                # -------------------------------
                total_sent = getattr(self.simulation.channel.metrics, "total_sent", 0)
                packet_rate = total_sent / 5.0 if total_sent > 0 else 0

                # -------------------------------
                # DENSITY (vehicles in range)
                # -------------------------------
                density = self.get_local_density(vehicles) if vehicles else 0

                # -------------------------------
                # CONTENTION WINDOW (ms)
                # -------------------------------
                # Based on channel cooldown (represents waiting time)
                contention_window = self.msg_cooldown_counter * 16

                # -------------------------------
                # STORE SAMPLE
                # -------------------------------
                self.qos_log.append({
                    "range": round(range_m, 2),
                    "packet_rate": round(packet_rate, 2),
                    "density": density,
                    "contention": round(contention_window, 2)
                })

        if self.t >= 1:

            # --------------------------------------------------
            #  QoS TRACKING STOP + PRINT RESULTS
            # --------------------------------------------------
            if self.vehicle.is_emergency and self.qos_active:

                if len(self.qos_log) > 0:  # Print if we have at least 1 sample

                    sample_count = len(self.qos_log)
                    print("\n------------------------------------------------------------")
                    print(f"Vehicle  : {self.vehicle.vehicle_type.upper()}")
                    print(f"Location : {self.lane.lane_id}")
                    print(f"Samples  : {sample_count}")
                    print("------------------------------------------------------------")

                    header_slots = " | ".join([f"T{i+1}" for i in range(sample_count)])
                    print(f"Metrics         | {header_slots}")
                    print("------------------------------------------------------------")

                    ranges = [str(x["range"]) for x in self.qos_log]
                    packets = [str(x["packet_rate"]) for x in self.qos_log]
                    densities = [str(x["density"]) for x in self.qos_log]
                    contentions = [str(x["contention"]) for x in self.qos_log]

                    print(f"Range (m)       | {' | '.join(ranges)}")
                    print(f"Packet Rate     | {' | '.join(packets)}")
                    print(f"Density         | {' | '.join(densities)}")
                    print(f"Contention (ms) | {' | '.join(contentions)}")

                    print("------------------------------------------------------------\n")

                # reset after printing
                self.qos_log.clear()
                self.qos_active = False
                self.qos_timer = 0
                self.qos_started = False

            # existing logic continues
            if self.lane.next_lanes:
                self.lane = random.choice(self.lane.next_lanes)

            self.t = 0.02

        if self.lane_changing:
            self.apply_lane_change()
        else:
            x, y = self.lane.interpolate(self.t)
            self.vehicle.x = x
            self.vehicle.y = y

        dx = self.vehicle.x - prev_x
        dy = self.vehicle.y - prev_y

        if abs(dx) > 0.001 or abs(dy) > 0.001:
            self.vehicle.angle = math.degrees(math.atan2(-dx, -dy))

        # --------------------------------------------------
        # MESSAGE SENDING (NEW - SAFE ADD)
        # --------------------------------------------------

        self.msg_timer += 1

        if vehicles:

            if self.vehicle.is_emergency:
                interval = 40
                msg_type = "EMV"
            else:
                interval = 80
                msg_type = "AV"

            if self.msg_timer > interval:
                self.msg_timer = 0

                # COOLDOWN CHECK (density-based)
                if self.msg_cooldown_counter > 0:
                    self.msg_cooldown_counter -= 1
                    return

                lane_id = self.lane.lane_id

                def is_before_stop_line(vehicle):
                    cx = self.simulation.road.cx
                    cy = self.simulation.road.cy

                    west_stop_x = cx - 60
                    east_stop_x = cx + 60
                    north_stop_y = cy - 60
                    south_stop_y = cy + 60

                    x = vehicle.x
                    y = vehicle.y
                    lane = self.lane.lane_id

                    if lane.startswith("W"):
                        return x <= west_stop_x
                    elif lane.startswith("E"):
                        return x >= east_stop_x
                    elif lane.startswith("N"):
                        return y <= north_stop_y
                    elif lane.startswith("S"):
                        return y >= south_stop_y
                    return False

                if self.vehicle.is_emergency:

                    # � DENSITY-BASED RATE LIMITING
                    density = self.get_local_density(vehicles)
                    if density > 6:
                        cooldown = 6   # high density → slower
                    elif density > 3:
                        cooldown = 3   # medium density
                    else:
                        cooldown = 1   # low density → fast

                    # �EMV BROADCAST TO NEARBY VEHICLES
                    for v, ctrl in vehicles:

                        if v == self.vehicle:
                            continue

                        dx = v.x - self.vehicle.x
                        dy = v.y - self.vehicle.y
                        dist = (dx*dx + dy*dy) ** 0.5

                        EMV_RADIUS = 120   # same as channel

                        if dist <= EMV_RADIUS:

                            adaptive_radius = self.get_adaptive_radius(vehicles)
                            self.simulation.channel.broadcast(
                                self.vehicle,
                                v.x,
                                v.y,
                                msg_type="EMV",
                                vehicles=vehicles,
                                radius=adaptive_radius
                            )

                    # send to signal ONLY when in zone
                    if self.vehicle.in_safe_zone and self.is_before_stop_line(self.vehicle):

                        tx, ty = self.get_signal_target()

                        adaptive_radius = self.get_adaptive_radius(vehicles)
                        self.simulation.channel.broadcast(
                            self.vehicle,
                            tx,
                            ty,
                            msg_type="EMV",
                            radius=adaptive_radius
                        )

                    elif self.is_before_stop_line(self.vehicle):

                        best = self.find_best_forward_vehicle(self.simulation.vehicles)

                        if best:

                            if not hasattr(self.vehicle, "hop_msg_id"):
                                from network.message import Message
                                self.vehicle.hop_msg_id = Message._id_counter + 1

                            adaptive_radius = self.get_adaptive_radius(vehicles)
                            self.simulation.channel.broadcast(
                                self.vehicle,
                                best.x,
                                best.y,
                                msg_type="EMV_HOP",
                                msg_id=self.vehicle.hop_msg_id,
                                radius=adaptive_radius
                            )

                    #  SET COOLDOWN AFTER EMV BROADCASTS
                    self.msg_cooldown_counter = cooldown

                else:
                    if self.vehicle.in_safe_zone:
                        tx, ty = self.get_signal_target()
                        adaptive_radius = self.get_adaptive_radius(vehicles)
                        self.simulation.channel.broadcast(
                            self.vehicle,
                            tx,
                            ty,
                            msg_type=msg_type,
                            vehicles=vehicles,
                            radius=adaptive_radius
                        )

        if hasattr(self.vehicle, "received_emv") and self.vehicle.received_emv:

            #  STOP AFTER CROSSING INTERSECTION
            if not self.is_before_stop_line(self.vehicle):
                self.vehicle.received_emv = False
                return

            #  LIMIT HOPS
            if hasattr(self.vehicle, "emv_hop_count") and self.vehicle.emv_hop_count > 5:
                self.vehicle.received_emv = False
                return

            #  COOLDOWN CHECK (for relay)
            if self.msg_cooldown_counter > 0:
                self.msg_cooldown_counter -= 1
                self.vehicle.received_emv = False
                return

            #  DENSITY-BASED RATE LIMITING (for relay)
            density = self.get_local_density(self.simulation.vehicles)
            if density > 6:
                cooldown = 6   # high density → slower
            elif density > 3:
                cooldown = 3   # medium density
            else:
                cooldown = 1   # low density → fast

            best = self.find_best_forward_vehicle(self.simulation.vehicles)

            if best:
                adaptive_radius = self.get_adaptive_radius(self.simulation.vehicles)
                self.simulation.channel.broadcast(
                    self.vehicle,
                    best.x,
                    best.y,
                    msg_type="EMV_HOP",
                    msg_id=getattr(self.vehicle, "hop_msg_id", None),
                    radius=adaptive_radius
                )
                #  SET COOLDOWN AFTER RELAY
                self.msg_cooldown_counter = cooldown
            else:
                # fallback → send to signal
                tx, ty = self.get_signal_target()

                adaptive_radius = self.get_adaptive_radius(self.simulation.vehicles)
                self.simulation.channel.broadcast(
                    self.vehicle,
                    tx,
                    ty,
                    msg_type="EMV_HOP",
                    msg_id=getattr(self.vehicle, "hop_msg_id", None),
                    radius=adaptive_radius
                )
                #  SET COOLDOWN AFTER RELAY
                self.msg_cooldown_counter = cooldown

            self.vehicle.received_emv = False

        #  (moved to beginning of update)