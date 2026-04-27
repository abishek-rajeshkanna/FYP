import numpy as np


class dstEncoder:

    def encode(self, controller, vehicles):

        state = []

        ego = controller.vehicle

        # collect nearby vehicles (same road context)
        nearby = []

        for v, ctrl in vehicles:

            if ctrl is controller:
                continue

            rel_dist = (ctrl.t - controller.t) * controller.lane.length

            nearby.append((v, ctrl, rel_dist))

        # sort by nearest
        nearby.sort(key=lambda x: abs(x[2]))

        # take up to 6 vehicles
        nearby = nearby[:6]

        # -----------------------------
        # 24 features (6 × 4)
        # -----------------------------
        for v, ctrl, rel_dist in nearby:

            lane_index = int(ctrl.lane.lane_id[-1])   # W0 → 0, W1 → 1
            speed = ctrl.current_speed

            acceleration = (
                ctrl.current_speed - ctrl.desired_speed
            )

            state.extend([
                lane_index,
                speed,
                acceleration,
                rel_dist
            ])

        # pad if fewer than 6 vehicles
        while len(state) < 24:
            state.extend([0, 0, 0, 0])

        # -----------------------------
        # Ego vehicle (5 features)
        # -----------------------------
        ego_lane_index = int(controller.lane.lane_id[-1])

        ego_speed = controller.current_speed

        ego_acceleration = (
            controller.current_speed - controller.desired_speed
        )

        ego_relative_distance = 0

        ego_position = controller.t * controller.lane.length

        state.extend([
            ego_lane_index,
            ego_speed,
            ego_acceleration,
            ego_relative_distance,
            ego_position
        ])

        return np.array(state, dtype=np.float32)
    

class dsEncoder:

    def encode():
        north_queue = (
            lane_stats["N0"]["queue"] +
            lane_stats["N1"]["queue"]
        )

        south_queue = (
            lane_stats["S0"]["queue"] +
            lane_stats["S1"]["queue"]
        )

        east_queue = (
            lane_stats["E0"]["queue"] +
            lane_stats["E1"]["queue"]
        )

        west_queue = (
            lane_stats["W0"]["queue"] +
            lane_stats["W1"]["queue"]
        )
        # ----------------------------------------
        # Intersection context (3 features)
        # ----------------------------------------

        signal_phase = sim.signal.phase

        # Placeholder neighbor queues
        # Replace with actual neighboring intersections if available
        neighbor_queue_1 = east_queue + west_queue
        neighbor_queue_2 = north_queue + south_queue

        # ----------------------------------------
        # Emergency vehicle distance (1 feature)
        # ----------------------------------------

        ev_distance = -1

        for vehicle, controller in sim.vehicles:

            if vehicle.is_emergency:

                remaining_pixels = (
                    (1 - controller.t) *
                    controller.lane.length
                )

                ev_distance = round(
                    remaining_pixels * sim.PIXEL_TO_METER,
                    2
                )

                break

        # ----------------------------------------
        # Final MAPPO state vector
        # Total = 8 features
        # ----------------------------------------

        m_state = [
            north_queue,
            south_queue,
            east_queue,
            west_queue,
            signal_phase,
            neighbor_queue_1,
            neighbor_queue_2,
            ev_distance
        ]

        return m_state