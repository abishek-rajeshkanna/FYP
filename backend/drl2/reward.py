import math


class RewardFunction:

    def compute(self, vehicle, prev_pos, action):

        prev_x, prev_y = prev_pos

        dx = vehicle.x - prev_x
        dy = vehicle.y - prev_y

        progress = math.sqrt(dx * dx + dy * dy)

        reward = 0

        # --------------------------------
        # MOVEMENT
        # --------------------------------

        reward += progress * 8
        reward += vehicle.speed * 0.5

        # --------------------------------
        # EMERGENCY PRIORITY
        # --------------------------------

        if vehicle.is_emergency:
            reward += progress * 8

        # --------------------------------
        # BLOCKING PENALTY
        # --------------------------------

        reward -= vehicle.blocked_time * 0.1

        if vehicle.blocked_time > 20:
            reward -= 3

        if vehicle.blocked_time > 40:
            reward -= 8

        # --------------------------------
        # LANE CHANGE
        # --------------------------------

        if action == 1:
            reward += 3

            if vehicle.blocked_time > 5:
                reward += 5

        # --------------------------------
        # OVERTAKE (EMV)
        # --------------------------------

        if vehicle.is_emergency:

            if vehicle.blocked_time > 5 and vehicle.speed > 1.2:
                reward += 6

        # --------------------------------
        # BRAKING
        # --------------------------------

        if action == 2:
            reward -= 1

        # --------------------------------
        # NON-EMV COOPERATION
        # --------------------------------

        if not vehicle.is_emergency:

            if vehicle.blocked_time == 0:
                reward += 2

        # --------------------------------
        # COMMUNICATION EFFECTS
        # --------------------------------

        received_emv = getattr(vehicle, "received_emv", False)
        hop_count = getattr(vehicle, "emv_hop_count", 0)
        in_safe_zone = getattr(vehicle, "in_safe_zone", False)

        # EMV awareness
        if received_emv:

            if not vehicle.is_emergency and vehicle.speed > 0.8:
                reward += 2.0

            if vehicle.blocked_time < 5:
                reward += 1.5

        # Multihop influence
        if hop_count > 0:
            reward += min(hop_count * 0.3, 1.5)

        # RSU zone behavior
        if in_safe_zone:

            if vehicle.speed < 1.0:
                reward += 0.8

            if vehicle.speed > 1.5:
                reward -= 0.5

        # Communication quality effect
        if received_emv and hop_count > 2:
            reward += 0.5

        if received_emv and vehicle.blocked_time > 10:
            reward -= 1.0

        return reward