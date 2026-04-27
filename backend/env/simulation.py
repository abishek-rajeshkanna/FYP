import random
import json
import time

from env.vehicle import Vehicle
from env.road import Road
from env.lane_graph import LaneGraph
from env.vehicle_controller import VehicleController
from env.signal import TrafficSignal
from env.config import LANE_MODE

from network.channel import Channel

import pygame

class Simulation:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.road = Road(width, height)
        self.graph = LaneGraph(width // 2, height // 2, width, height)
        self.signal = TrafficSignal()

        self.vehicles = []

        # Message Channel
        self.channel = Channel()
        self.message_timer = 0   # for test messages

        # EMV broadcast zone blink control
        self.blink_timer = 0
        self.blink_state = True

        # --------------------------------------------------
        # MESSAGE VISIBILITY TOGGLE
        # --------------------------------------------------
        self.show_messages = True

        self.show_circles = True

        # RSU phase-change broadcast guard
        self.rsu_message_sent = False
        self.prev_phase = self.signal.phase

        # Pause flag
        self.paused = False

        # EMV PREEMPTION STATE
        self.emv_active = False
        self.emv_direction = None
        self.emv_extend_time = 0
        self.emv_extend_done = False

        # SIMULATION CONSTANTS
        self.PIXEL_TO_METER = 0.25
        self.FPS = 60

        # METRIC TRACKING
        self.metrics = {
            "horizontal": {"time": [], "speed": []},
            "vertical": {"time": [], "speed": []}
        }

        self.spawn_time = {}

        self.metric_timer = 0
        self.metric_interval = 10 * self.FPS

        # BASELINE METRICS
        self.baseline_metrics = {
            "horizontal": {"speed": 0, "time": 0},
            "vertical": {"speed": 0, "time": 0}
        }

        import time

        self.last_qos_update = time.time()
        self.qos_display = {
            "R": 0,
            "sigma": 0,
            "lambda": 0,
            "Wc": 0
        }

        # VEHICLE SPAWN
        vehicle_types = (
            ["truck"] * 9 +
            ["car"] * 9 +
            ["police"] * 3 +
            ["ambulance"] * 3
        )

        random.shuffle(vehicle_types)

        for vtype in vehicle_types:

            is_emergency = vtype in ["police", "ambulance"]

            lane = self.graph.random_lane()

            vehicle = Vehicle(
                lane.start[0],
                lane.start[1],
                vehicle_type=vtype,
                is_emergency=is_emergency
            )

            controller = VehicleController(vehicle, lane, self.graph, self)

            self.spawn_time[vehicle] = time.time()

            self.vehicles.append((vehicle, controller))

    # --------------------------------------------------
    # UPDATE QoS METRICS
    # --------------------------------------------------
    def update_qos_metrics(self):

        import time

        current_time = time.time()

        if current_time - self.last_qos_update >= 5:

            self.last_qos_update = current_time

            m = self.channel.metrics

            # Calculate average range
            if m.total_received > 0:
                R = m.total_distance / m.total_received
                Wc = m.total_delay / m.total_received
            else:
                R = 0
                Wc = 0
            
            # Calculate channel utilization
            if m.total_steps > 0:
                sigma = m.busy_steps / m.total_steps
            else:
                sigma = 0
 
            # Calculate packet rate
            lambda_rate = m.total_sent / 5.0

            self.qos_display = {
                "R": round(R, 2),
                "sigma": round(sigma, 2),
                "lambda": round(lambda_rate, 2),
                "Wc": round(Wc, 2)
            }

            m.reset_interval()

    # --------------------------------------------------
    # EMV DETECTION
    # --------------------------------------------------

    def check_emergency_preemption(self):

        if self.emv_active:
            return

        cx = self.road.cx
        cy = self.road.cy

        left_safe = cx - self.road.SAFE_LEFT_OFFSET
        right_safe = cx + self.road.SAFE_RIGHT_OFFSET
        top_safe = cy - self.road.SAFE_TOP_OFFSET
        bottom_safe = cy + self.road.SAFE_BOTTOM_OFFSET

        for vehicle, controller in self.vehicles:

            if not vehicle.is_emergency:
                continue

            x = vehicle.x
            y = vehicle.y
            speed = controller.current_speed
            lane = controller.lane.lane_id

            if lane in ["W0", "W1"] and x > left_safe:
                self.trigger_emv(vehicle, speed, abs(cx - x), "WEST")

            elif lane in ["E0", "E1"] and x < right_safe:
                self.trigger_emv(vehicle, speed, abs(x - cx), "EAST")

            elif lane in ["N0", "N1"] and y > top_safe:
                self.trigger_emv(vehicle, speed, abs(cy - y), "NORTH")

            elif lane in ["S0", "S1"] and y < bottom_safe:
                self.trigger_emv(vehicle, speed, abs(y - cy), "SOUTH")

    # --------------------------------------------------

    def trigger_emv(self, vehicle, speed, dist_pixels, direction):

        dist_m = dist_pixels * self.PIXEL_TO_METER

        time_frames = dist_pixels / max(speed, 0.1)
        time_seconds = round(time_frames / self.FPS, 2)

        if not self.paused:
            print("\n🚑 EMV detected from", direction)
            print("Distance:", round(dist_m, 2), "meters")
            print("Time to intersection:", time_seconds, "seconds")

        self.emv_active = True
        self.emv_direction = direction
        self.emv_extend_time = int(time_seconds) + 1

        msg = f"EMV ({vehicle.vehicle_type}) approaching — extending {self.emv_extend_time}s"
        self.road.set_emv_message(direction, msg)

    # --------------------------------------------------

    def apply_emv_preemption(self):

        if not self.emv_active:
            return

        if self.emv_direction in ["WEST", "EAST"]:

            if self.signal.is_horizontal_green() and not self.emv_extend_done:

                if not self.paused:
                    print("🚦 Extending HORIZONTAL GREEN")

                self.signal.timer += self.emv_extend_time
                self.emv_extend_done = True

        else:

            if self.signal.is_vertical_green() and not self.emv_extend_done:

                if not self.paused:
                    print("🚦 Extending VERTICAL GREEN")

                self.signal.timer += self.emv_extend_time
                self.emv_extend_done = True

    # --------------------------------------------------

    def compute_metrics(self):

        cx = self.road.cx
        cy = self.road.cy

        left_entry = cx - self.road.SAFE_LEFT_OFFSET
        right_entry = cx + self.road.SAFE_RIGHT_OFFSET
        top_entry = cy - self.road.SAFE_TOP_OFFSET
        bottom_entry = cy + self.road.SAFE_BOTTOM_OFFSET

        for vehicle, controller in self.vehicles:

            if not vehicle.is_emergency:
                continue

            x = vehicle.x
            y = vehicle.y

            if vehicle not in self.spawn_time:
                continue

            start = self.spawn_time[vehicle]

            if x < 0 or x > self.width:

                travel_time = time.time() - start
                if travel_time < 5:
                    continue

                distance_pixels = self.width
                distance_m = distance_pixels * self.PIXEL_TO_METER
                speed_kmh = (distance_m / travel_time) * 3.6

                self.metrics["horizontal"]["time"].append(round(travel_time, 2))
                self.metrics["horizontal"]["speed"].append(round(speed_kmh, 2))

                del self.spawn_time[vehicle]

            elif y < 0 or y > self.height:

                travel_time = time.time() - start
                if travel_time < 5:
                    continue

                distance_pixels = self.height
                distance_m = distance_pixels * self.PIXEL_TO_METER
                speed_kmh = (distance_m / travel_time) * 3.6

                self.metrics["vertical"]["time"].append(round(travel_time, 2))
                self.metrics["vertical"]["speed"].append(round(speed_kmh, 2))

                del self.spawn_time[vehicle]

    # --------------------------------------------------

    def get_lane_statistics(self):

        stats = {}

        lane_ids = ["W0","W1","E0","E1","N0","N1","S0","S1"]

        for lid in lane_ids:
            stats[lid] = {
                "cars":0,
                "trucks":0,
                "police":0,
                "ambulance":0,
                "queue":0,
                "speed_sum":0,
                "count":0
            }

        for vehicle, controller in self.vehicles:

            lane = controller.lane.lane_id

            if lane not in stats:
                continue

            stats[lane]["count"] += 1
            stats[lane]["speed_sum"] += controller.current_speed

            if vehicle.vehicle_type == "car":
                stats[lane]["cars"] += 1
            elif vehicle.vehicle_type == "truck":
                stats[lane]["trucks"] += 1
            elif vehicle.vehicle_type == "police":
                stats[lane]["police"] += 1
            elif vehicle.vehicle_type == "ambulance":
                stats[lane]["ambulance"] += 1

            if controller.stopped:
                stats[lane]["queue"] += 1

        return stats

    # --------------------------------------------------

    def update(self):

        self.signal.update()

        current_phase = self.signal.phase

        # --------------------------------------------------
        # TRIGGER ON ANY PHASE CHANGE
        # --------------------------------------------------
        if current_phase != self.prev_phase and not self.rsu_message_sent:

            cx = self.road.cx
            cy = self.road.cy
            offset = 100  # distance to signal heads

            rsu_nodes = {
                "WEST":  (cx - offset, cy),
                "EAST":  (cx + offset, cy),
                "NORTH": (cx, cy - offset),
                "SOUTH": (cx, cy + offset)
            }

            # --------------------------------------------------
            # RSU → RSU (TARGETED, NOT RANDOM)
            # --------------------------------------------------
            for name, (sx, sy) in rsu_nodes.items():

                for target_name, (tx, ty) in rsu_nodes.items():

                    if name == target_name:
                        continue

                    sender = type("RSU", (), {"x": sx, "y": sy})()

                    self.channel.broadcast(
                        sender,
                        tx,
                        ty,
                        msg_type="RSU_TO_RSU",
                        vehicles=None,
                        radius=120
                    )

            # --------------------------------------------------
            # RSU → VEHICLES (ZONE-BASED)
            # --------------------------------------------------
            from network.message import Message

            for name, (sx, sy) in rsu_nodes.items():

                sender = type("RSU", (), {"x": sx, "y": sy})()

                for vehicle, controller in self.vehicles:

                    lane_id = controller.lane.lane_id

                    if (
                        (name == "WEST" and lane_id.startswith("W")) or
                        (name == "EAST" and lane_id.startswith("E")) or
                        (name == "NORTH" and lane_id.startswith("N")) or
                        (name == "SOUTH" and lane_id.startswith("S"))
                    ):

                        if controller.vehicle.in_safe_zone:

                            msg = Message(
                                sender.x,
                                sender.y,
                                vehicle.x,
                                vehicle.y,
                                msg_type="RSU_BROADCAST"
                            )

                            msg.target_vehicle = vehicle
                            self.channel.messages.append(msg)

            print("🚦 RSU GLOBAL COMMUNICATION TRIGGERED")
            self.rsu_message_sent = True

        # --------------------------------------------------
        # RESET FLAG AFTER STABLE STATE
        # --------------------------------------------------
        if current_phase == self.prev_phase:
            self.rsu_message_sent = False

        self.prev_phase = current_phase

        for vehicle, controller in self.vehicles:
            controller.update(self.signal, self.vehicles)          # lane change

        self.check_emergency_preemption()
        self.apply_emv_preemption()

        self.compute_metrics()

        # Update message system
        self.channel.update()

        # Update QoS metrics
        self.update_qos_metrics()

        # --------------------------------------------------
        # BLINK CONTROL FOR EMV ZONE
        # --------------------------------------------------
        self.blink_timer += 1

        if self.blink_timer > 20:   # adjust speed of blinking
            self.blink_timer = 0
            self.blink_state = not self.blink_state

        # TEMP TEST: send EMV messages
        # Removed, EMV broadcast is now handled in vehicle_controller.py

        # BASELINE METRIC FETCH
        self.metric_timer += 1

        if self.metric_timer >= self.metric_interval:

            self.metric_timer = 0

            try:
                with open("/home/vinith/Desktop/SEM-8/demo/MARL5/MARL4/MARL/baseline_metrics.json") as f:
                    self.baseline_metrics = json.load(f)
            except:
                pass

    # --------------------------------------------------

    def detect_ev_lanes(self):

        data = {
            "NORTH": False,
            "SOUTH": False,
            "EAST": False,
            "WEST": False,
            "ev_count": 0,
            "total": len(self.vehicles)
        }

        for vehicle, controller in self.vehicles:
            if vehicle.is_emergency:
                data["ev_count"] += 1

        return data

    # --------------------------------------------------
    # GET ACTIVE LANES (NOT DIRECTIONS)
    # --------------------------------------------------
    def get_active_lanes(self):

        cx = self.road.cx
        cy = self.road.cy

        left_bound = cx - self.road.SAFE_LEFT_OFFSET
        right_bound = cx + self.road.SAFE_RIGHT_OFFSET
        top_bound = cy - self.road.SAFE_TOP_OFFSET
        bottom_bound = cy + self.road.SAFE_BOTTOM_OFFSET

        # stop line positions (same as draw logic)
        road_half = self.road.road_width // 2

        west_stop_x  = cx - road_half
        east_stop_x  = cx + road_half
        north_stop_y = cy - road_half
        south_stop_y = cy + road_half

        active_lanes = set()

        for vehicle, controller in self.vehicles:

            x = vehicle.x
            y = vehicle.y
            lane_id = controller.lane.lane_id

            # WEST → EAST lanes
            if lane_id.startswith("W"):
                if left_bound < x < west_stop_x:
                    active_lanes.add(lane_id)

            # EAST → WEST lanes
            elif lane_id.startswith("E"):
                if east_stop_x < x < right_bound:
                    active_lanes.add(lane_id)

            # NORTH → SOUTH lanes
            elif lane_id.startswith("N"):
                if top_bound < y < north_stop_y:
                    active_lanes.add(lane_id)

            # SOUTH → NORTH lanes
            elif lane_id.startswith("S"):
                if south_stop_y < y < bottom_bound:
                    active_lanes.add(lane_id)

        return active_lanes

    # --------------------------------------------------

    def get_state(self):
        return {
            "vehicles": [(v.x, v.y, ctrl.t) for v, ctrl in self.vehicles],
            "messages": [(m.x, m.y, m.tx, m.ty, m.msg_type, m.msg_id, m.hop_count, m.trail, m.status, m.delay_timer, m.loss_timer, m.active, m.speed) for m in self.channel.messages]
        }

    # --------------------------------------------------

    def set_state(self, state):

        for (v, ctrl), data in zip(self.vehicles, state["vehicles"]):
            v.x, v.y, ctrl.t = data

        # rebuild messages
        self.channel.messages.clear()

        from network.message import Message

        for data in state["messages"]:
            x, y, tx, ty, msg_type, msg_id, hop_count, trail, status, delay_timer, loss_timer, active, speed = data
            msg = Message(x, y, tx, ty, msg_type, msg_id=msg_id)
            msg.hop_count = hop_count
            msg.trail = trail
            msg.status = status
            msg.delay_timer = delay_timer
            msg.loss_timer = loss_timer
            msg.active = active
            msg.speed = speed
            self.channel.messages.append(msg)

    # --------------------------------------------------

    def draw(self, screen):

        ev_data = self.detect_ev_lanes()

        lane_stats = self.get_lane_statistics()

        ev_data["signal_phase"] = self.signal.phase
        ev_data["signal_timer"] = self.signal.timer

        ev_data["marl_metrics"] = self.metrics
        ev_data["baseline_metrics"] = self.baseline_metrics
        ev_data["qos_display"] = self.qos_display

        self.road.draw(screen, ev_data, lane_stats)

        # --------------------------------------------------
        # DRAW LANE-SPECIFIC ZONES
        # --------------------------------------------------
        if self.show_messages:

            active_lanes = self.get_active_lanes()

            if self.blink_state:

                cx = self.road.cx
                cy = self.road.cy
                lane_w = self.road.lane_width
                road_half = self.road.road_width // 2

                # --------------------------------------------------
                # EXACT STOP LINE POSITIONS (MATCH VEHICLE STOP)
                # --------------------------------------------------
                west_stop_x  = cx - road_half
                east_stop_x  = cx + road_half
                north_stop_y = cy - road_half
                south_stop_y = cy + road_half

                left = cx - self.road.SAFE_LEFT_OFFSET
                right = cx + self.road.SAFE_RIGHT_OFFSET
                top = cy - self.road.SAFE_TOP_OFFSET
                bottom = cy + self.road.SAFE_BOTTOM_OFFSET

                GREEN = (0, 255, 0)

                for vehicle, controller in self.vehicles:

                    lane = controller.lane
                    lane_id = lane.lane_id

                    if lane_id not in active_lanes:
                        continue

                    x1, y1 = lane.start
                    x2, y2 = lane.end

                    # horizontal lane
                    if abs(x1 - x2) > abs(y1 - y2):
                        y = int(y1)

                        if lane_id.startswith("W"):
                            pygame.draw.rect(
                                screen,
                                GREEN,
                                (left, y - lane_w // 2, west_stop_x - left, lane_w),
                                0
                            )

                        elif lane_id.startswith("E"):
                            pygame.draw.rect(
                                screen,
                                GREEN,
                                (east_stop_x, y - lane_w // 2, right - east_stop_x, lane_w),
                                0
                            )

                    # vertical lane
                    else:
                        x = int(x1)

                        if lane_id.startswith("N"):
                            pygame.draw.rect(
                                screen,
                                GREEN,
                                (x - lane_w // 2, top, lane_w, north_stop_y - top),
                                0
                            )

                        elif lane_id.startswith("S"):
                            pygame.draw.rect(
                                screen,
                                GREEN,
                                (x - lane_w // 2, south_stop_y, lane_w, bottom - south_stop_y),
                                0
                            )

        for vehicle, controller in self.vehicles:
            vehicle.draw(screen)

        # --------------------------------------------------
        # DRAW EMV BROADCAST ZONE (TOGGLE CONTROL)
        # --------------------------------------------------
        if self.show_messages and self.show_circles:
            for vehicle, controller in self.vehicles:

                if not vehicle.is_emergency:
                    continue

                # blinking effect
                if not self.blink_state:
                    continue

                adaptive_radius = controller.get_adaptive_radius(self.vehicles)

                # draw circle
                pygame.draw.circle(
                    screen,
                    (255, 50, 50),   # red
                    (int(vehicle.x), int(vehicle.y)),
                    int(adaptive_radius),
                    2
                )

                # OPTIONAL: count nearby vehicles
                count = self.channel.count_nearby(vehicle, self.vehicles)

                label = self.channel.font.render(
                    f"{count}",
                    True,
                    (255, 255, 255)
                )

                screen.blit(label, (vehicle.x + 10, vehicle.y - 10))

        #  Draw messages
        if self.show_messages:
            self.channel.draw(screen)

        # --------------------------------------------------
        #  MESSAGE TOGGLE BUTTON UI
        # --------------------------------------------------
        button_x = self.width - 180
        button_y = 150

        color = (0, 200, 0) if self.show_messages else (200, 0, 0)
        text = "MSG: ON" if self.show_messages else "MSG: OFF"

        pygame.draw.rect(screen, (0, 0, 0), (button_x, button_y, 120, 40))
        pygame.draw.rect(screen, color, (button_x, button_y, 120, 40), 2)

        label = self.road.font.render(text, True, color)
        screen.blit(label, (button_x + 10, button_y + 10))

        # --------------------------------------------------
        # CIRCLE STATUS UI
        # --------------------------------------------------
        circle_text = self.road.font.render(f"Circles: {'ON' if self.show_circles else 'OFF'}", True, (255, 255, 255))
        screen.blit(circle_text, (20, 20))

    def set_phase(self, phase):
        self.phase = phase
        self.timer = self.default_green_time