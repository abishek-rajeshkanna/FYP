class RewardCalculator:

    def __init__(self):

        self.queue_weight = -1.0
        self.speed_weight = 0.3
        self.wait_penalty = -0.5
        self.emergency_bonus = 5.0

        # additional factors for coordination and communication
        self.coord_bonus = 2.0
        self.msg_bonus = 1.5

    # ------------------------------------------------

    def compute_total_queue(self, lane_stats):

        total_queue = 0

        for lane in lane_stats.values():
            total_queue += lane.get("queue", 0)

        return total_queue

    # ------------------------------------------------

    def compute_avg_speed(self, lane_stats):

        total_speed = 0
        total_count = 0

        for lane in lane_stats.values():

            avg_speed = lane.get("avg_speed", 0)
            count = lane.get("count", 0)

            total_speed += avg_speed * count
            total_count += count

        if total_count == 0:
            return 0

        return total_speed / total_count

    # ------------------------------------------------

    def compute_reward(self, prev_stats, current_stats, ev_data, signal=None):

        reward = 0

        # ------------------------------------------------
        # Queue reduction reward
        # ------------------------------------------------

        prev_queue = self.compute_total_queue(prev_stats)
        curr_queue = self.compute_total_queue(current_stats)

        queue_change = prev_queue - curr_queue

        reward += self.queue_weight * curr_queue
        reward += queue_change * 0.5

        # ------------------------------------------------
        # Speed reward
        # ------------------------------------------------

        avg_speed = self.compute_avg_speed(current_stats)
        reward += self.speed_weight * avg_speed

        # ------------------------------------------------
        # Waiting penalty
        # ------------------------------------------------

        waiting_penalty = 0

        for lane in current_stats.values():
            waiting_penalty += lane.get("queue", 0)

        reward += self.wait_penalty * waiting_penalty

        # ------------------------------------------------
        # Emergency vehicle priority
        # ------------------------------------------------

        emergency_count = ev_data.get("ev_count", 0)

        if emergency_count > 0:
            reward += self.emergency_bonus

        # ------------------------------------------------
        # Communication-aware reward
        # ------------------------------------------------

        msg_density = 0
        msg_lanes = 0

        for lane in current_stats.values():
            msg_density += lane.get("msg_queue", 0)
            msg_lanes += 1

        if msg_lanes > 0:
            msg_density = msg_density / msg_lanes

        if msg_density > 0:
            reward += self.msg_bonus * msg_density

        # ------------------------------------------------
        # Emergency message awareness
        # ------------------------------------------------

        if ev_data.get("msg_ev_detected", False):
            reward += 2.0

        # ------------------------------------------------
        # Signal coordination reward (RSU ↔ RSU)
        # ------------------------------------------------

        if signal is not None:

            neighbor_pressure = getattr(signal, "neighbor_pressure", 0)

            # reward smoother coordination across signals
            reward += self.coord_bonus * (1 - abs(neighbor_pressure))

        return reward