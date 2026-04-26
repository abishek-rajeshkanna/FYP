import pygame

from env.simulation import Simulation
from rl.signal_policy import SignalPolicy
from rl.state_encoder import StateEncoder


pygame.init()

WIDTH = 1250
HEIGHT = 670

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DRL PPO LANE CHANGE AND MAPPO TRAFFIC SIGNAL SIMULATION")

clock = pygame.time.Clock()

sim = Simulation(WIDTH, HEIGHT)

policy = SignalPolicy()
encoder = StateEncoder()

decision_interval = 300   # RL decision every 5 seconds
frame_count = 0

# Pause and replay variables
paused = False
history = []
HISTORY_LIMIT = 200
REPLAY_STEPS = 30   # ~2–3 seconds

# Helper: compute traffic pressure

def horizontal_queue(stats):
    return (
        stats["W0"]["queue"] +
        stats["W1"]["queue"] +
        stats["E0"]["queue"] +
        stats["E1"]["queue"]
    )


def vertical_queue(stats):
    return (
        stats["N0"]["queue"] +
        stats["N1"]["queue"] +
        stats["S0"]["queue"] +
        stats["S1"]["queue"]
    )


running = True

while running:

    clock.tick(40)
    frame_count += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                sim.show_messages = not sim.show_messages
            # B → toggle broadcast circles
            if event.key == pygame.K_b:
                sim.show_circles = not sim.show_circles
                print("Show Circles:", sim.show_circles)
            # SPACE → pause/resume
            if event.key == pygame.K_SPACE:
                paused = not paused
            # LEFT → go back few seconds
            if event.key == pygame.K_LEFT:
                steps = min(REPLAY_STEPS, len(history))
                for _ in range(steps):
                    if history:
                        state = history.pop()
                if history:  # if there's still history after popping
                    state = history[-1]  # get the last state
                    sim.set_state(state)

    # ------------------------------------------------
    # RL Decision Block
    # ------------------------------------------------

    if frame_count % decision_interval == 0:

        lane_stats = sim.get_lane_statistics()
        ev_data = sim.detect_ev_lanes()

        state = encoder.encode(lane_stats, ev_data, sim.signal)

        action = policy.act(state)

        hq = horizontal_queue(lane_stats)
        vq = vertical_queue(lane_stats)

        horizontal_green = sim.signal.is_horizontal_green()
        vertical_green = sim.signal.is_vertical_green()

        # ------------------------------------------------
        # DEBUG INFO
        # ------------------------------------------------

        if not paused:
            print("\n============================")
            print("STATE:", state)
            print("RL ACTION:", action)
            print("Horizontal Queue:", hq)
            print("Vertical Queue:", vq)
            print("Current Phase:", sim.signal.phase)
            print("Timer:", sim.signal.timer)
            print("============================")

        # ------------------------------------------------
        # TRAFFIC PRESSURE OVERRIDE
        # ------------------------------------------------

        if horizontal_green and vq > hq + 1:

            if not paused:
                print("OVERRIDE: SWITCH TO VERTICAL")
            sim.signal.switch_phase()

        elif vertical_green and hq > vq + 1:

            if not paused:
                print("OVERRIDE: SWITCH TO HORIZONTAL")
            sim.signal.switch_phase()

        else:

            # --------------------------------------------
            # RL decisions
            # --------------------------------------------

            if action == 1:

                if not paused:
                    print("RL DECISION: SWITCH PHASE")
                sim.signal.switch_phase()

            elif action == 2:

                if not paused:
                    print("RL DECISION: EXTEND GREEN")
                sim.signal.extend_green()

    # ------------------------------------------------
    # Update simulation
    # ------------------------------------------------

    sim.paused = paused

    if not paused:
        sim.update()

        # Store state after update
        history.append(sim.get_state())
        if len(history) > HISTORY_LIMIT:
            history.pop(0)

    screen.fill((30, 30, 30))

    sim.draw(screen)

    # Optional UI text
    if paused:
        font = pygame.font.SysFont(None, 48)
        text = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 24))

    pygame.display.flip()


pygame.quit()