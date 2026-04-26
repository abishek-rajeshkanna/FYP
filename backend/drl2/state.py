import numpy as np


class StateEncoder:

    def encode(self, controller, vehicles):

        vehicle = controller.vehicle

        front_dist = 9999
        rear_dist = 9999

        vehicles_ahead = 0
        vehicles_behind = 0

        lane_density = 0
        emv_distance = 9999

        slow_vehicle_ahead = 0
        adjacent_lane_free = 1

        front_vehicle_type = 0  # 0 none, 1 car, 2 truck

        current_lane = controller.lane
        adj_lane = controller.get_adjacent_lane()

        # --------------------------------
        # TRAFFIC ANALYSIS
        # --------------------------------

        for v, c in vehicles:

            if v == vehicle:
                continue

            dist = abs(v.x - vehicle.x) + abs(v.y - vehicle.y)

            if c.lane == current_lane:

                lane_density += 1

                if c.t > controller.t:

                    vehicles_ahead += 1

                    if dist < front_dist:
                        front_dist = dist

                        if c.current_speed < controller.current_speed:
                            slow_vehicle_ahead = 1

                        if v.vehicle_type == "truck":
                            front_vehicle_type = 2
                        elif v.vehicle_type == "car":
                            front_vehicle_type = 1

                elif c.t < controller.t:

                    vehicles_behind += 1

                    if dist < rear_dist:
                        rear_dist = dist

            if adj_lane and c.lane.lane_id == adj_lane:

                lane_gap = abs((c.t - controller.t) * current_lane.length)

                if lane_gap < controller.safe_distance:
                    adjacent_lane_free = 0

            if v.is_emergency:
                emv_distance = min(emv_distance, dist)

        # --------------------------------
        # COMMUNICATION-AWARE ADJUSTMENTS
        # --------------------------------

        received_emv = getattr(vehicle, "received_emv", False)
        hop_count = getattr(vehicle, "emv_hop_count", 0)
        in_safe_zone = getattr(vehicle, "in_safe_zone", False)

        # EMV influence
        if received_emv:
            lane_density += 1
            vehicles_ahead += 0.5
            adjacent_lane_free = max(0, adjacent_lane_free - 0.2)
            slow_vehicle_ahead = max(slow_vehicle_ahead, 1)

        # Multihop propagation effect
        if hop_count > 0:
            vehicles_behind += min(hop_count * 0.2, 1)

        # RSU zone awareness (indirect communication effect)
        if in_safe_zone:
            slow_vehicle_ahead = max(slow_vehicle_ahead, 0.6)

        # --------------------------------
        # NORMALIZATION
        # --------------------------------

        front_dist = min(front_dist / 500, 1)
        rear_dist = min(rear_dist / 500, 1)

        vehicles_ahead = min(vehicles_ahead / 5, 1)
        vehicles_behind = min(vehicles_behind / 5, 1)

        lane_density = min(lane_density / 10, 1)

        blocked = min(vehicle.blocked_time / 60, 1)

        speed = min(controller.current_speed / 2, 1)

        front_vehicle_type = front_vehicle_type / 2

        adjacent_lane_free = max(0, min(adjacent_lane_free, 1))
        slow_vehicle_ahead = min(slow_vehicle_ahead, 1)

        # --------------------------------
        # FINAL STATE
        # --------------------------------

        state = np.array([
            front_dist,
            rear_dist,
            vehicles_ahead,
            vehicles_behind,
            lane_density,
            blocked,
            speed,
            slow_vehicle_ahead,
            adjacent_lane_free,
            front_vehicle_type
        ], dtype=np.float32)

        return state