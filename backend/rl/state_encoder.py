class StateEncoder:

    def __init__(self):
        pass

    def encode(self, lane_stats, ev_data, signal):

        state = []

        # ------------------------------------------------
        # Lane order must always stay consistent
        # ------------------------------------------------

        lane_ids = ["W0","W1","E0","E1","N0","N1","S0","S1"]

        total_speed = 0
        total_count = 0

        msg_density = 0
        msg_count = 0

        for lid in lane_ids:

            lane = lane_stats.get(lid, {})

            queue = lane.get("queue", 0)
            avg_speed = lane.get("avg_speed", 0)
            count = lane.get("count", 0)

            # --------------------------------------------
            # Communication-aware adjustment
            # --------------------------------------------

            msg_queue = lane.get("msg_queue", 0)
            msg_density += msg_queue
            msg_count += 1

            # Blend direct observation with communicated data
            queue = 0.7 * queue + 0.3 * msg_queue

            state.append(queue)

            total_speed += avg_speed * count
            total_count += count

        # ------------------------------------------------
        # Average speed of intersection
        # ------------------------------------------------

        if total_count > 0:
            intersection_speed = total_speed / total_count
        else:
            intersection_speed = 0

        # ------------------------------------------------
        # Emergency vehicle awareness
        # ------------------------------------------------

        ev_count = ev_data.get("ev_count", 0)

        # amplify importance if communication indicates urgency
        if ev_data.get("msg_ev_detected", False):
            ev_count += 1

        state.append(ev_count)

        # ------------------------------------------------
        # Communication density indicator
        # ------------------------------------------------

        if msg_count > 0:
            avg_msg_density = msg_density / msg_count
        else:
            avg_msg_density = 0

        state.append(intersection_speed)
        state.append(avg_msg_density)

        # ------------------------------------------------
        # Neighbor signal coordination (RSU ↔ RSU)
        # ------------------------------------------------

        neighbor_pressure = getattr(signal, "neighbor_pressure", 0)
        state.append(neighbor_pressure)

        # ------------------------------------------------
        # Encode signal phase
        # ------------------------------------------------

        phase_map = {
            "HORIZONTAL_GREEN": 0,
            "HORIZONTAL_YELLOW": 1,
            "VERTICAL_GREEN": 2,
            "VERTICAL_YELLOW": 3
        }

        state.append(phase_map.get(signal.phase, 0))

        # ------------------------------------------------
        # Signal timer
        # ------------------------------------------------

        state.append(signal.timer)

        return state