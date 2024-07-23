import pygame
import sys
from collections import deque
import numpy as np
import time

# Initialize Pygame
pygame.init()

# Define constants
GRID_SIZE = 8
SCREEN_SIZE = 600
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 60
alpha = 0.1
gamma = 0.9
Deaths = 0
CheeseEaten = 0

# Define rewards
gluetrap_reward = -400
cheese_reward = 5000

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ratventure")

# Load and scale images
def load_and_scale_image(path):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

rat_images = {
    'UP': load_and_scale_image("Assets\\rat_up.png"),
    'DOWN': load_and_scale_image("Assets\\rat_down.png"),
    'LEFT': load_and_scale_image("Assets\\rat_left.png"),
    'RIGHT': load_and_scale_image("Assets\\rat_right.png")
}
cheese_image = load_and_scale_image("Assets\\cheese.png")
gluetrap_image = load_and_scale_image("Assets\\gluetrap.png")

# Moveset and Q-table
actions = ["UP", "DOWN", "LEFT", "RIGHT"]
Q = np.zeros((GRID_SIZE, GRID_SIZE, len(actions)))

def is_cheese(x, y):
    return (x * CELL_SIZE, y * CELL_SIZE) == tuple(cheese_position)

def is_gluetrap(x, y):
    return (x * CELL_SIZE, y * CELL_SIZE) in gluetrap_positions

def get_distance(x, y):
    return np.sqrt((cheese_position[0] - x) ** 2 + (cheese_position[1] - y) ** 2)

def is_valid(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

def get_next_position(x, y, action):
    if action == "UP":
        return x, y - 1
    elif action == "DOWN":
        return x, y + 1
    elif action == "LEFT":
        return x - 1, y
    else:
        return x + 1, y

def get_reward(x, y):
    if is_cheese(x, y):
        return cheese_reward
    elif is_gluetrap(x, y):
        return gluetrap_reward
    return 700 - get_distance(x, y)

def update_Q(x, y, action, reward, next_x, next_y):
    current_Q = Q[x, y, actions.index(action)]
    max_next_Q = np.max(Q[next_x, next_y, :])
    new_Q = current_Q + alpha * (reward + gamma * max_next_Q - current_Q)
    Q[x, y, actions.index(action)] = new_Q

rat_position = [4, 3]
cheese_position = [7 * CELL_SIZE, 7 * CELL_SIZE]
gluetrap_positions = [
    (2 * CELL_SIZE, 2 * CELL_SIZE), (3 * CELL_SIZE, 5 * CELL_SIZE), 
    (6 * CELL_SIZE, 4 * CELL_SIZE), (5 * CELL_SIZE, 1 * CELL_SIZE),
    (1 * CELL_SIZE, 0 * CELL_SIZE), (7 * CELL_SIZE, 0 * CELL_SIZE),
    (0 * CELL_SIZE, 6 * CELL_SIZE)
]

direction_queue = deque()
clock = pygame.time.Clock()
current_direction = 'RIGHT'
custom_font = "Assets\\PixeloidSans.ttf"
font = pygame.font.Font(custom_font, 18)

def get_best_action(x, y):
    return np.argmax(Q[x, y, :])

def get_random_action():
    return np.random.choice(actions)

def get_q_learning_action(x, y):
    return actions[get_best_action(x, y)]

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    epsilon = 0.3
    action = get_random_action() if np.random.uniform() < epsilon else get_q_learning_action(rat_position[0], rat_position[1])
    next_x, next_y = get_next_position(rat_position[0], rat_position[1], action)
    current_direction = action

    if is_valid(next_x, next_y):
        reward = get_reward(next_x, next_y)
        update_Q(rat_position[0], rat_position[1], action, reward, next_x, next_y)
        rat_position = [next_x, next_y]

        if is_cheese(rat_position[0], rat_position[1]):
            CheeseEaten += 1
            if CheeseEaten > 3*Deaths:
                np.save("q_table.npy", Q)
                time.sleep(10)
                pygame.quit()
                sys.exit()
            rat_position = [4, 3]

        elif is_gluetrap(rat_position[0], rat_position[1]):
            Deaths += 1
            rat_position = [4, 3]

    screen.fill((255, 255, 255))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pygame.draw.rect(screen, (0, 0, 0), (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            if (row, col) != (7, 7):
                q_value = int(np.max(Q[col, row, :]))
                q_text = font.render(str(q_value), True, (0, 0, 0))
                screen.blit(q_text, (col * CELL_SIZE + 10, row * CELL_SIZE + 10))

    screen.blit(rat_images[current_direction], (rat_position[0] * CELL_SIZE, rat_position[1] * CELL_SIZE))
    screen.blit(cheese_image, tuple(cheese_position))
    for gluetrap_position in gluetrap_positions:
        screen.blit(gluetrap_image, gluetrap_position)

    death_text = font.render(f" Deaths: {Deaths}", True, (230, 0, 38))
    screen.blit(death_text, (10, HEIGHT - 40))
    win_text = font.render(f" CheeseEaten: {CheeseEaten}", True, (255, 179, 25))
    screen.blit(win_text, (10, HEIGHT - 25))

    pygame.display.flip()
    clock.tick(FPS)
