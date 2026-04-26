import pygame
import os
from env.config import TRAINING_MODE


class Vehicle:

    def __init__(self, x, y, vehicle_type="car", is_emergency=False):

        self.x = x
        self.y = y

        self.vehicle_type = vehicle_type
        self.is_emergency = is_emergency

        # vehicle heading angle (controller updates this)
        self.angle = 0

        # --------------------------------------------------
        # speed hierarchy

        if vehicle_type == "truck":
            self.speed = 0.8
        elif vehicle_type == "car":
            self.speed = 1.1
        else:
            self.speed = 1.5

        # --------------------------------------------------
        # lane awareness

        self.lane_id = None
        self.target_lane = None
        self.lane_change_cooldown = 0

        # --------------------------------------------------
        # NEW: DRL blockage tracking (NO behaviour change)

        self.blocked_time = 0

        # --------------------------------------------------
        # NEW: AV Response message flags

        self.response_sent = False
        self.was_yielding = False

        # --------------------------------------------------
        # Only load images if NOT training

        if not TRAINING_MODE:
            self.load_images()
        else:
            self.frames = [None]
            self.anim_index = 0
            self.last_anim_time = 0

    # --------------------------------------------------

    def load_images(self):

        base_path = "assets/vehicles"

        self.vehicle_width = 60
        self.vehicle_length = 50

        if self.vehicle_type == "car":
            self.vehicle_length = int(50 * 0.7)

        if self.is_emergency:

            folder = "ambulance_anim" if self.vehicle_type == "ambulance" else "police_anim"

            self.frames = []

            for i in range(1, 4):

                img = pygame.image.load(
                    os.path.join(base_path, folder, f"{i}.png")
                ).convert_alpha()

                img = pygame.transform.scale(
                    img,
                    (self.vehicle_width, self.vehicle_length)
                )

                self.frames.append(img)

        else:

            filename = f"{self.vehicle_type}.png"

            img = pygame.image.load(
                os.path.join(base_path, filename)
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                (self.vehicle_width, self.vehicle_length)
            )

            self.frames = [img]

        self.anim_index = 0
        self.last_anim_time = 0

    # --------------------------------------------------

    def get_current_frame(self):

        if TRAINING_MODE:
            return None

        if self.is_emergency:

            current_time = pygame.time.get_ticks()

            if current_time - self.last_anim_time > 120:
                self.anim_index = (self.anim_index + 1) % len(self.frames)
                self.last_anim_time = current_time

        return self.frames[self.anim_index]

    # --------------------------------------------------

    def draw(self, screen):

        if TRAINING_MODE:
            return

        image = self.get_current_frame()

        rotated_image = pygame.transform.rotate(image, self.angle)

        rect = rotated_image.get_rect(center=(self.x, self.y))

        screen.blit(rotated_image, rect)