
import pygame


class TrafficSignal:

    def __init__(self):

        self.phase = "HORIZONTAL_GREEN"

        self.green_duration = 60
        self.yellow_duration = 6

        self.timer = self.green_duration

        self.last_tick = pygame.time.get_ticks()

        # --------------------------------------------------
        # NEW: signal stability constraints
        # --------------------------------------------------

        self.MIN_GREEN = 8          # minimum green before switching allowed
        self.green_elapsed = 0      # time spent in current green phase
        self.switch_cooldown = 0    # prevents rapid switching

    # --------------------------------------------------

    def update(self):

        now = pygame.time.get_ticks()

        if now - self.last_tick >= 1000:

            self.timer -= 1
            self.last_tick = now

            # track green duration
            if self.phase in ["HORIZONTAL_GREEN", "VERTICAL_GREEN"]:
                self.green_elapsed += 1

            # reduce cooldown timer
            if self.switch_cooldown > 0:
                self.switch_cooldown -= 1

            if self.timer <= 0:

                if self.phase == "HORIZONTAL_GREEN":
                    self.phase = "HORIZONTAL_YELLOW"
                    self.timer = self.yellow_duration

                elif self.phase == "HORIZONTAL_YELLOW":
                    self.phase = "VERTICAL_GREEN"
                    self.timer = self.green_duration
                    self.green_elapsed = 0

                elif self.phase == "VERTICAL_GREEN":
                    self.phase = "VERTICAL_YELLOW"
                    self.timer = self.yellow_duration

                elif self.phase == "VERTICAL_YELLOW":
                    self.phase = "HORIZONTAL_GREEN"
                    self.timer = self.green_duration
                    self.green_elapsed = 0

    # --------------------------------------------------

    def switch_phase(self):

        # --------------------------------------------------
        # Constraint 1: prevent switching during yellow
        # --------------------------------------------------

        if self.phase in ["HORIZONTAL_YELLOW", "VERTICAL_YELLOW"]:
            return

        # --------------------------------------------------
        # Constraint 2: enforce minimum green time
        # --------------------------------------------------

        if self.green_elapsed < self.MIN_GREEN:
            return

        # --------------------------------------------------
        # Constraint 3: cooldown between switches
        # --------------------------------------------------

        if self.switch_cooldown > 0:
            return

        if self.phase == "HORIZONTAL_GREEN":
            self.phase = "HORIZONTAL_YELLOW"
            self.timer = self.yellow_duration

        elif self.phase == "VERTICAL_GREEN":
            self.phase = "VERTICAL_YELLOW"
            self.timer = self.yellow_duration

        # reset cooldown
        self.switch_cooldown = 5

    # --------------------------------------------------

    def extend_green(self):

        if self.phase in ["HORIZONTAL_GREEN", "VERTICAL_GREEN"]:
            self.timer += 5

    # --------------------------------------------------

    def is_horizontal_green(self):
        return self.phase == "HORIZONTAL_GREEN"

    def is_vertical_green(self):
        return self.phase == "VERTICAL_GREEN"

    def is_horizontal_yellow(self):
        return self.phase == "HORIZONTAL_YELLOW"

    def is_vertical_yellow(self):
        return self.phase == "VERTICAL_YELLOW"

