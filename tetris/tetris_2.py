import pygame
import random
from typing import List, Any, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 15
GRID_HEIGHT = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (30, 30, 60)
PANEL_COLOR = (45, 45, 80)
GRAY = (100, 100, 130)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
COLORS = [
    (0, 255, 255), (255, 255, 0), (128, 0, 128),
    (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0)
]

DIFFICULTIES = {
    "Easy": {"speed": 1200, "dec": 50, "color": GREEN},
    "Medium": {"speed": 800, "dec": 100, "color": YELLOW},
    "Hard": {"speed": 400, "dec": 150, "color": RED}
}


# Tetrominoes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]

class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(w: int, h: int) -> List[List[Any]]:
    return [[None for _ in range(w)] for _ in range(h)]

def check_collision(grid, piece, x, y):
    for r, row in enumerate(piece.shape):
        for c, val in enumerate(row):
            if val:
                if (x + c < 0 or x + c >= GRID_WIDTH or
                    y + r < 0 or y + r >= GRID_HEIGHT or
                    grid[y + r][x + c] is not None):
                    return True
    return False

def clear_lines(grid):
    lines_to_clear = []
    for y, row in enumerate(grid):
        if all(cell is not None for cell in row):
            lines_to_clear.append(y)
    
    score_increment = 0
    if len(lines_to_clear) > 0:
        # Standard scoring: 100, 300, 500, 800 for 1, 2, 3, 4 lines
        score_increment = [0, 100, 300, 500, 800][len(lines_to_clear)]
    
    for y in sorted(lines_to_clear, reverse=True):
        del grid[y]
        grid.insert(0, [None for _ in range(GRID_WIDTH)])
    return grid, score_increment

def draw_text(screen, text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

def show_menu(screen, font):
    selected = 0
    options = list(DIFFICULTIES.keys())
    
    while True:
        screen.fill(BG_COLOR)
        draw_text(screen, "TETRIS PRO", font, WHITE, SCREEN_WIDTH // 2, 150, True)
        draw_text(screen, "Select Difficulty:", font, WHITE, SCREEN_WIDTH // 2, 220, True)
        
        for i, option in enumerate(options):
            color = DIFFICULTIES[option]["color"] if i == selected else WHITE
            draw_text(screen, option, font, color, SCREEN_WIDTH // 2, 280 + i * 50, True)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected]

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Pro")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 30)
    
    running = True
    while running:
        difficulty_name = show_menu(screen, font)
        if difficulty_name is None:
            break
        
        difficulty = DIFFICULTIES[difficulty_name]
        grid: List[List[Any]] = create_grid(GRID_WIDTH, GRID_HEIGHT)
        current_piece = Piece()
        next_piece = Piece()
        score = 0
        level = 1
        fall_speed = difficulty["speed"]
        fall_time = 0
        game_over = False
        game_loop_running = True

        while game_loop_running:
            dt = clock.tick(60)
            fall_time += dt
            screen.fill(BG_COLOR)


            if not game_over:
                if fall_time > fall_speed:
                    if not check_collision(grid, current_piece, current_piece.x, current_piece.y + 1):
                        current_piece.y += 1
                    else:
                        for r, row in enumerate(current_piece.shape):
                            for c, val in enumerate(row):
                                if val:
                                    grid[current_piece.y + r][current_piece.x + c] = current_piece.color
                        
                        grid, points = clear_lines(grid)
                        score += points
                        
                        if score > level * 1000:
                            level += 1
                            fall_speed = max(100, fall_speed - difficulty["dec"])
                        
                        current_piece = next_piece
                        next_piece = Piece()
                        
                        if check_collision(grid, current_piece, current_piece.x, current_piece.y):
                            game_over = True
                    fall_time = 0

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        game_loop_running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            game_loop_running = False
                        if not game_over:
                            if event.key == pygame.K_LEFT:
                                if not check_collision(grid, current_piece, current_piece.x - 1, current_piece.y):
                                    current_piece.x -= 1
                            if event.key == pygame.K_RIGHT:
                                if not check_collision(grid, current_piece, current_piece.x + 1, current_piece.y):
                                    current_piece.x += 1
                            if event.key == pygame.K_UP:
                                prev_shape = current_piece.shape
                                current_piece.rotate()
                                if check_collision(grid, current_piece, current_piece.x, current_piece.y):
                                    current_piece.shape = prev_shape
                            if event.key == pygame.K_DOWN:
                                if not check_collision(grid, current_piece, current_piece.x, current_piece.y + 1):
                                    current_piece.y += 1
                            if event.key == pygame.K_SPACE:
                                while not check_collision(grid, current_piece, current_piece.x, current_piece.y + 1):
                                    current_piece.y += 1
                                
                                for r, row in enumerate(current_piece.shape):
                                    for c, val in enumerate(row):
                                        if val:
                                            grid[current_piece.y + r][current_piece.x + c] = current_piece.color
                                
                                grid, points = clear_lines(grid)
                                score += points
                                
                                if score > level * 1000:
                                    level += 1
                                    fall_speed = max(100, fall_speed - difficulty["dec"])
                                
                                current_piece = next_piece
                                next_piece = Piece()
                                
                                if check_collision(grid, current_piece, current_piece.x, current_piece.y):
                                    game_over = True
                                fall_time = 0

            # Draw Grid
            for y, row in enumerate(grid):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, cell, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

            # Draw current piece
            if not game_over:
                for r, row in enumerate(current_piece.shape):
                    for c, val in enumerate(row):
                        if val:
                            pygame.draw.rect(screen, current_piece.color, 
                                              ((current_piece.x + c) * BLOCK_SIZE, 
                                               (current_piece.y + r) * BLOCK_SIZE, 
                                               BLOCK_SIZE - 1, BLOCK_SIZE - 1))

            # Draw Right Panel
            pygame.draw.rect(screen, PANEL_COLOR, (450, 0, 150, SCREEN_HEIGHT))
            
            # UI
            draw_text(screen, f"Score: {score}", font, WHITE, 470, 40)
            draw_text(screen, f"Level: {level}", font, WHITE, 470, 80)
            draw_text(screen, f"Diff: {difficulty_name}", font, difficulty["color"], 470, 120)
            
            preview_x, preview_y = 460, 200
            pygame.draw.rect(screen, GRAY, (preview_x, preview_y, 130, 160), 2)
            pygame.draw.rect(screen, WHITE, (preview_x, preview_y, 130, 20), 1)
            draw_text(screen, "Next:", font, WHITE, preview_x, 170)
            
            piece_w = len(next_piece.shape[0]) * BLOCK_SIZE
            piece_h = len(next_piece.shape) * BLOCK_SIZE
            offset_x = (130 - piece_w) // 2
            offset_y = (140 - piece_h) // 2 + 20
            
            for r, row in enumerate(next_piece.shape):
                for c, val in enumerate(row):
                    if val:
                        pygame.draw.rect(screen, next_piece.color, 
                                          (preview_x + c * BLOCK_SIZE + offset_x, 
                                           preview_y + r * BLOCK_SIZE + offset_y, 
                                           BLOCK_SIZE - 1, BLOCK_SIZE - 1))

            if game_over:
                draw_text(screen, "GAME OVER", font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, True)
                draw_text(screen, "Press any key to return to menu", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, True)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        game_loop_running = False
                    if event.type == pygame.KEYDOWN:
                        game_loop_running = False

            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
