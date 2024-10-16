import pygame
import random

pygame.init()

# Game settings
WIDTH, HEIGHT = 400, 800
BLOCK_SIZE = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (50, 50, 50)
DARKER_GRAY = (20, 20, 20)

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

COLORS = [CYAN, YELLOW, MAGENTA, RED, GREEN, BLUE, ORANGE]

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()

# Game grid
COLUMNS = WIDTH // BLOCK_SIZE
ROWS = HEIGHT // BLOCK_SIZE
grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]

# Score
score = 0
font = pygame.font.SysFont("Arial", 30)

# Tetromino class
class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        new_shape = [list(row) for row in zip(*self.shape[::-1])]
        if self.can_move(0, 0, new_shape):
            self.shape = new_shape

    def can_move(self, dx, dy, shape=None):
        if shape is None:
            shape = self.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.x + x + dx
                    new_y = self.y + y + dy
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS or (new_y >= 0 and grid[new_y][new_x] != BLACK):
                        return False
        return True

    def move(self, dx, dy):
        if self.can_move(dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False

def draw_grid():
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(screen, LIGHT_GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pygame.draw.rect(screen, DARKER_GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
            if grid[y][x] != BLACK:
                draw_block_3d(x, y, grid[y][x])

def draw_block_3d(x, y, color):
    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.line(screen, WHITE, rect.topleft, rect.topright, 3)
    pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomleft, 3)
    pygame.draw.line(screen, DARKER_GRAY, rect.bottomleft, rect.bottomright, 3)
    pygame.draw.line(screen, DARKER_GRAY, rect.topright, rect.bottomright, 3)

def clear_lines():
    global grid, score
    new_grid = [row for row in grid if any(cell == BLACK for cell in row)]
    lines_cleared = ROWS - len(new_grid)
    for _ in range(lines_cleared):
        new_grid.insert(0, [BLACK for _ in range(COLUMNS)])
    grid = new_grid
    score += lines_cleared * 100
    return lines_cleared

def draw_shadow(tetromino):
    shadow_y = tetromino.y
    while tetromino.can_move(0, 1):
        tetromino.y += 1
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell and tetromino.y + y >= 0:
                pygame.draw.rect(screen, (100, 100, 100), ((tetromino.x + x) * BLOCK_SIZE, (tetromino.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    tetromino.y = shadow_y

def draw_tetromino(tetromino):
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell and tetromino.y + y >= 0:
                draw_block_3d(tetromino.x + x, tetromino.y + y, tetromino.color)

def smooth_fall(tetromino, fall_speed, elapsed_time):
    global score
    if elapsed_time > fall_speed:
        if tetromino.can_move(0, 1):
            tetromino.move(0, 1)
            score += 1
        return 0
    return elapsed_time

def accelerated_fall(tetromino):
    global score
    while tetromino.can_move(0, 1):
        tetromino.y += 1
        score += 1
        screen.fill(DARK_GRAY)
        draw_grid()
        draw_shadow(tetromino)
        draw_tetromino(tetromino)
        draw_score()
        pygame.display.flip()
        clock.tick(120)

def draw_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def main():
    global score
    running = True
    current_tetromino = Tetromino(random.choice(SHAPES), random.choice(COLORS))
    fall_time = 0
    fall_speed = 500  # Speed in milliseconds
    move_sideways_time = 0
    move_sideways_speed = 100  # Speed in milliseconds
    move_direction = None
    lock_delay = 200  # Delay in milliseconds before locking the tetromino
    lock_time = 0
    soft_drop_speed = 50  # Speed when pressing down arrow

    while running:
        screen.fill(DARK_GRAY)  # Dark background for a nicer UI
        draw_grid()
        draw_shadow(current_tetromino)
        draw_tetromino(current_tetromino)
        draw_score()

        pygame.display.flip()

        elapsed_time = clock.tick(60)
        fall_time += elapsed_time
        if move_direction is not None:
            move_sideways_time += elapsed_time

        if lock_time > 0:
            lock_time += elapsed_time
            if lock_time >= lock_delay:
                lock_time = 0
                for y, row in enumerate(current_tetromino.shape):
                    for x, cell in enumerate(row):
                        if cell and current_tetromino.y + y >= 0:
                            grid[current_tetromino.y + y][current_tetromino.x + x] = current_tetromino.color
                current_tetromino = Tetromino(random.choice(SHAPES), random.choice(COLORS))
                if not current_tetromino.can_move(0, 0):
                    running = False
                clear_lines()

        if fall_time >= fall_speed:
            if current_tetromino.can_move(0, 1):
                current_tetromino.move(0, 1)
                score += 1
            else:
                lock_time = 1  # Start lock delay
            fall_time = 0

        if move_direction is not None and move_sideways_time > move_sideways_speed:
            current_tetromino.move(move_direction, 0)
            move_sideways_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    move_direction = -1
                    move_sideways_time = 0  # Start moving immediately
                    current_tetromino.move(-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    move_direction = 1
                    move_sideways_time = 0  # Start moving immediately
                    current_tetromino.move(1, 0)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    fall_time = smooth_fall(current_tetromino, soft_drop_speed, fall_time)
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    current_tetromino.rotate()
                elif event.key == pygame.K_SPACE:
                    accelerated_fall(current_tetromino)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if move_direction == -1:
                        move_direction = None
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if move_direction == 1:
                        move_direction = None

    pygame.quit()

if __name__ == "__main__":
    main()