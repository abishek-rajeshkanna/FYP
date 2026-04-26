import math
import random

class Message:
    _id_counter = 0

    def __init__(self, x, y, target_x, target_y, msg_type="EMV", msg_id=None):

        if msg_id is not None:
            self.msg_id = msg_id
        else:
            Message._id_counter += 1
            self.msg_id = Message._id_counter

        self.x = x
        self.y = y

        self.tx = target_x
        self.ty = target_y

        self.base_speed = 3
        self.speed = self.base_speed

        dx = self.tx - self.x
        dy = self.ty - self.y

        dist = math.sqrt(dx * dx + dy * dy) + 1e-6

        self.vx = dx / dist
        self.vy = dy / dist

        self.msg_type = msg_type
        self.active = True
        self.target_vehicle = None

        # hop count for multi-hop
        self.hop_count = 0

        # -------------------------------
        # EXISTING TRAIL
        # -------------------------------
        self.trail = []

        # -------------------------------
        # 🚀 QoS PARAMETERS
        # -------------------------------
        self.status = "normal"   # normal / delayed / losing
        self.delay_timer = 0
        self.loss_timer = 0

        # PRIORITY
        if msg_type == "EMV":
            self.priority = 3
        else:
            self.priority = 1

        # assign QoS behavior
        self.assign_qos()

    # --------------------------------------------------

    def assign_qos(self):

        r = random.random()

        if self.priority == 3:
            # EMV → safer
            if r < 0.15:
                self.status = "delayed"
                self.delay_timer = random.randint(10, 25)
            elif r < 0.30:
                self.status = "losing"
                self.loss_timer = 12
        else:
            # normal → more unstable
            if r < 0.25:
                self.status = "delayed"
                self.delay_timer = random.randint(15, 30)
            elif r < 0.60:
                self.status = "losing"
                self.loss_timer = 12

    # --------------------------------------------------

    def update(self):

        # --------------------------------------------------
        # 🚀 FOLLOW MOVING TARGET (NEW)
        # --------------------------------------------------
        if self.target_vehicle is not None:

            self.tx = self.target_vehicle.x
            self.ty = self.target_vehicle.y

            dx = self.tx - self.x
            dy = self.ty - self.y

            dist = math.sqrt(dx * dx + dy * dy) + 1e-6

            self.vx = dx / dist
            self.vy = dy / dist

        # store trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:
            self.trail.pop(0)

        # -------------------------------
        # DELAY HANDLING
        # -------------------------------
        if self.status == "delayed" and self.delay_timer > 0:
            self.delay_timer -= 1
            self.speed = self.base_speed * 0.4
        else:
            self.speed = self.base_speed

        # -------------------------------
        # LOSS HANDLING
        # -------------------------------
        if self.status == "losing":
            self.loss_timer -= 1

            if self.loss_timer <= 0:
                self.active = False

                # mark as lost (safe hook)
                if hasattr(self, "channel_ref"):
                    self.channel_ref.metrics.total_lost += 1

                return

        # move
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed

        # reached destination
        if abs(self.x - self.tx) < 5 and abs(self.y - self.ty) < 5:
            self.active = False