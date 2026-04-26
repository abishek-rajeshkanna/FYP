import pygame
import math
from network.message import Message


def get_msg_category(sender, msg_type):
    """Classify message type for logging"""
    if msg_type in ["EMV", "EMV_HOP"]:
        return "EMV"
    if msg_type == "AV_RESPONSE":
        return "AV_RESPONSE"
    if hasattr(sender, "vehicle_type"):
        return "AV"
    return "RSU"


def format_entity(entity, lane=None):
    """Format entity string for logs"""
    if hasattr(entity, "vehicle_type"):
        vtype = entity.vehicle_type.upper()
        lane_id = lane if lane else getattr(entity, "lane", None)
        if getattr(entity, "is_emergency", False):
            return f"EMV[{vtype}|{lane_id}]"
        else:
            return f"AV[{vtype}|{lane_id}]"
    return "RSU"


def get_rsu_name(x, y, simulation):
    """Identify RSU by location"""
    cx, cy = simulation.road.cx, simulation.road.cy
    if x < cx:
        return "RSU[WEST]"
    elif x > cx:
        return "RSU[EAST]"
    elif y < cy:
        return "RSU[NORTH]"
    else:
        return "RSU[SOUTH]"


def log_message(msg_id, msg_type, sender, receiver, status, desc):
    print(
        f"MSG_ID: {msg_id} | TYPE: {msg_type} | FROM: {sender} | TO: {receiver} | STATUS: {status} | DESC: {desc}"
    )


def draw_dashed_line(screen, color, start_pos, end_pos, width=2, dash_length=5):
    x1, y1 = start_pos
    x2, y2 = end_pos

    dx = x2 - x1
    dy = y2 - y1
    dist = (dx*dx + dy*dy) ** 0.5

    if dist == 0:
        return

    dx /= dist
    dy /= dist

    step = dash_length * 2
    for i in range(0, int(dist), step):
        start_x = int(x1 + dx * i)
        start_y = int(y1 + dy * i)
        end_x = int(x1 + dx * (i + dash_length))
        end_y = int(y1 + dy * (i + dash_length))

        if (dx >= 0 and end_x > x2) or (dx < 0 and end_x < x2):
            end_x = int(x2)
        if (dy >= 0 and end_y > y2) or (dy < 0 and end_y < y2):
            end_y = int(y2)

        pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), width)


class QoSMetrics:

    def __init__(self):
        self.total_sent = 0
        self.total_received = 0
        self.total_lost = 0
        self.total_delay = 0
        self.total_distance = 0

        self.busy_steps = 0
        self.total_steps = 0

    def reset_interval(self):
        self.total_sent = 0
        self.total_received = 0
        self.total_delay = 0
        self.total_distance = 0


class Channel:

    def __init__(self):
        self.messages = []
        self.font = pygame.font.SysFont("Arial", 14)

        # ✅ communication radius (tunable)
        self.broadcast_radius = 120

        self.metrics = QoSMetrics()

    # --------------------------------------------------
    # 🚀 MAIN BROADCAST (VISUAL + LOGICAL)
    # --------------------------------------------------
    def broadcast(self, sender_vehicle, target_x, target_y, msg_type="EMV", vehicles=None, msg_id=None, radius=None):

        # Debug: Log AV_RESPONSE messages
        if msg_type == "AV_RESPONSE":
            print(f"📡 Channel.broadcast() called with AV_RESPONSE from {id(sender_vehicle)} "
                  f"to ({target_x}, {target_y}), radius={radius}")

        # -------------------------------
        # ✅ EXISTING VISUAL MESSAGE (DO NOT REMOVE)
        # -------------------------------
        msg = Message(
            sender_vehicle.x,
            sender_vehicle.y,
            target_x,
            target_y,
            msg_type,
            msg_id=msg_id
        )

        # increment hop count for multi-hop messages
        if msg_type == "EMV_HOP":
            msg.hop_count += 1

        self.messages.append(msg)
        
        self.metrics.total_sent += 1

        msg.channel_ref = self
        
        if msg_type == "AV_RESPONSE":
            print(f"✅ AV_RESPONSE message added to channel. Total messages: {len(self.messages)}")

        # --------------------------------------------------
        # 🚀 LOG SENT MESSAGE (ALL TYPES - BEFORE VEHICLES CHECK)
        # --------------------------------------------------
        sender_lane = "UNKNOWN"
        
        # Get sender info if available
        if vehicles is not None:
            for v, c in vehicles:
                if v == sender_vehicle:
                    sender_lane = c.lane.lane_id
                    break
        
        # Format sender string
        if hasattr(sender_vehicle, "vehicle_type"):
            # It's a vehicle
            sender_str = format_entity(sender_vehicle, sender_lane)
        else:
            # It's an RSU - just identify as RSU[location approximation]
            sender_str = "RSU"

        desc_map = {
            "EMV": "Broadcasting emergency presence",
            "EMV_HOP": "Emergency multi-hop propagation",
            "AV_RESPONSE": "Cooperative yielding response",
            "RSU_BROADCAST": "Signal transition broadcast",
            "RSU_TO_RSU": "Signal coordination",
        }
        desc = desc_map.get(msg_type, "Message transmission")
        msg_category = get_msg_category(sender_vehicle, msg_type)

        # Determine receiver string based on message type
        if msg_category == "AV":
            receiver_str = "RSU"
        else:
            receiver_str = "MULTIPLE"

        print(
            f"MSG_ID: {msg.msg_id} | TYPE: {msg_category} | "
            f"FROM: {sender_str} | TO: {receiver_str} | "
            f"STATUS: SENT | DESC: {desc}"
        )

        # -------------------------------
        # ✅ LOGICAL DELIVERY (INBOX SYSTEM)
        # -------------------------------
        if vehicles is None:
            return

        sender_x = sender_vehicle.x
        sender_y = sender_vehicle.y

        # -------------------------------
        # ✅ FIND SENDER CONTROLLER
        # -------------------------------
        sender_controller = None

        for v, c in vehicles:
            if v == sender_vehicle:
                sender_controller = c
                break

        if sender_controller is None:
            return

        sender_lane = sender_controller.lane.lane_id
        sender_t = sender_controller.t

        # -------------------------------
        # ✅ LOOP THROUGH VEHICLES
        # -------------------------------
        for vehicle, controller in vehicles:

            # ❌ skip self
            if vehicle == sender_vehicle:
                continue

            # -------------------------------
            # ✅ SAME ROAD FILTER (W/E/N/S)
            # -------------------------------
            receiver_lane = controller.lane.lane_id

            if sender_lane[0] != receiver_lane[0]:
                continue

            # -------------------------------
            # ✅ DISTANCE CHECK
            # -------------------------------
            dx = vehicle.x - sender_x
            dy = vehicle.y - sender_y
            distance = math.sqrt(dx * dx + dy * dy)

            if radius is None:
                effective_radius = self.broadcast_radius
            else:
                effective_radius = radius

            if distance > effective_radius:
                continue

            # -------------------------------
            # ✅ FORWARD-ONLY FILTER
            # -------------------------------
            receiver_t = controller.t

            if receiver_t <= sender_t:
                continue

            # ❌ skip self-receive logs
            if vehicle == sender_vehicle:
                continue

            # Format RECEIVED log
            receiver_lane = controller.lane.lane_id
            msg_category = get_msg_category(sender_vehicle, msg_type)
            from_str = format_entity(sender_vehicle, sender_lane)
            to_str = format_entity(vehicle, receiver_lane)

            # Handle AV → RSU case (check if message targets signal location)
            if msg_type == "RSU_BROADCAST" or (target_x, target_y) != (vehicle.x, vehicle.y):
                if hasattr(self, "simulation"):
                    to_str = get_rsu_name(target_x, target_y, self.simulation)

            print(
                f"MSG_ID: {msg.msg_id} | TYPE: {msg_category} | "
                f"FROM: {from_str} | TO: {to_str} | "
                f"STATUS: RECEIVED | DESC: Message delivered successfully"
            )

            self.metrics.total_received += 1
            self.metrics.total_distance += distance

            # simple delay approximation (based on hop + QoS state)
            delay = 1
            if msg.status == "delayed":
                delay = 2
            elif msg.status == "losing":
                delay = 3

            self.metrics.total_delay += delay

            controller.inbox.append({
                "sender": sender_vehicle,
                "msg_type": msg_type,
                "distance": round(distance, 2),
                "msg_id": msg.msg_id,
                "hop_count": msg.hop_count
            })

    # --------------------------------------------------
    # 🚀 COUNT VEHICLES IN RANGE (FOR UI)
    # --------------------------------------------------
    def count_nearby(self, sender_vehicle, vehicles):

        count = 0

        sender_controller = None
        for v, c in vehicles:
            if v == sender_vehicle:
                sender_controller = c
                break

        if sender_controller is None:
            return 0

        sx, sy = sender_vehicle.x, sender_vehicle.y
        sender_lane = sender_controller.lane.lane_id
        sender_t = sender_controller.t

        for vehicle, controller in vehicles:

            if vehicle == sender_vehicle:
                continue

            if sender_lane[0] != controller.lane.lane_id[0]:
                continue

            dx = vehicle.x - sx
            dy = vehicle.y - sy

            if math.sqrt(dx * dx + dy * dy) <= self.broadcast_radius:
                if controller.t > sender_t:
                    count += 1

        return count

    # --------------------------------------------------
    def update(self):
        self.metrics.total_steps += 1

        if len(self.messages) > 20:   # threshold
            self.metrics.busy_steps += 1

        for msg in self.messages:
            msg.update()

        self.messages = [m for m in self.messages if m.active]

    # --------------------------------------------------
    # 🚀 COLOR LOGIC (QoS VISUALIZATION)
    # --------------------------------------------------
    def get_color(self, msg):

        if msg.msg_type == "EMV_HOP":
            return (255, 255, 255)

        if msg.msg_type == "AV_RESPONSE":
            return (255, 140, 0)   # orange fire color

        elif msg.msg_type == "RSU_BROADCAST":
            return (80, 80, 80)   # dark grey

        elif msg.msg_type == "RSU_TO_RSU":
            return (60, 60, 60)   # slightly darker grey

        if msg.msg_type == "EMV":
            base = (150, 0, 0)
        else:
            base = (0, 200, 0)

        if msg.status == "delayed":
            return (255, 255, 0)

        if msg.status == "losing":
            if msg.loss_timer > 5:
                return (255, 0, 255)
            else:
                return (255, 0, 0)

        return base

    # --------------------------------------------------
    def draw(self, screen):

        for msg in self.messages:

            color = self.get_color(msg)

            # -------------------------------
            # DRAW TRAIL (disabled)
            # -------------------------------
            # if len(msg.trail) > 1:
            #     pygame.draw.lines(
            #         screen,
            #         color,
            #         False,
            #         [(int(x), int(y)) for x, y in msg.trail],
            #         1
            #     )

            # -------------------------------
            # DRAW DASHED DIRECTION LINE
            # -------------------------------
            end_x = int(msg.x + msg.vx * 10)
            end_y = int(msg.y + msg.vy * 10)
            draw_dashed_line(
                screen,
                color,
                (int(msg.x), int(msg.y)),
                (end_x, end_y),
                2,
                4
            )

            # -------------------------------
            # DRAW DOT
            # -------------------------------
            radius = 4
            if msg.msg_type in ["RSU_BROADCAST", "RSU_TO_RSU"]:
                radius = 6   # slightly larger for RSU messages

            pygame.draw.circle(
                screen,
                color,
                (int(msg.x), int(msg.y)),
                radius
            )

            # -------------------------------
            # DRAW GLOW FOR AV_RESPONSE (FIREBALL EFFECT)
            # -------------------------------
            if msg.msg_type == "AV_RESPONSE":
                glow_radius = 10 + (msg.msg_id % 3) * 2
                pygame.draw.circle(screen, (255, 80, 0), (int(msg.x), int(msg.y)), glow_radius, 2)

            # -------------------------------
            # DRAW ID
            # -------------------------------
            label = self.font.render(str(msg.msg_id), True, (255, 255, 255))
            screen.blit(label, (msg.x + 6, msg.y - 4))