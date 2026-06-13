import pygame
import random
import sys

# Monokai color palette (RGB)
MONOKAI = {
    'background': (30, 30, 30),
    'grid_line': (70, 70, 70),
    'grid_fill': (20, 20, 20),
    'pieces': {
        0: (0, 255, 120),  # I - green
        1: (255, 160, 0),   # O - orange
        2: (255, 0, 0),      # T - red
        3: (0, 0, 255),      # S - blue
        4: (255, 255, 0),    # Z - yellow
        5: (255, 0, 255),    # J - magenta
        6: (0, 255, 255),    # L - cyan,
    }
}

CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WINDOW_WIDTH = (CELL_SIZE * GRID_WIDTH) + 150  # Extra space for UI
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 60

# Define tetromino shapes
SHAPES = [
    [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],  # I
    [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],  # O
    [[0, 0, 0, 0], [0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0]],  # T
    [[0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]],  # S
    [[0, 0, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]],  # Z
    [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 1, 1, 0]],  # J
    [[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0]],  # L
]

# Precompute rotations
ROTA_SHAPES = []
for shape in SHAPES:
    rotations = []
    for _ in range(4):
        rotations.append(shape)
        shape = [[shape[3 - y][x] for y in range(4)] for x in range(4)]
    ROTA_SHAPES.append(rotations)

class Piece:
    def __init__(self, shape_id):
        self.shape_id = shape_id
        self.rotation = 0
        self.shape = ROTA_SHAPES[shape_id][0]
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4
        self.shape = ROTA_SHAPES[self.shape_id][self.rotation]

    def get_cells(self):
        cells = []
        for y, row in enumerate(self.shape):
            for x, val in enumerate(row):
                if val:
                    cells.append((self.x + x, self.y + y))
        return cells

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.reset_game()

    def reset_game(self):
        self.grid = [[0]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.drop_time = 0
        self.drop_interval = 500
        self.game_over = False
        self.score = 0
        self.level = 1
        self.paused = False

    def new_piece(self):
        return Piece(random.randint(0, len(SHAPES)-1))

    def collision(self, piece):
        for x, y in piece.get_cells():
            if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
                return True
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                if self.grid[y][x]:
                    return True
        return False

    def lock_piece(self, piece):
        for x, y in piece.get_cells():
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.grid[y][x] = piece.shape_id + 1
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if self.collision(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        new_grid = []
        cleared = 0
        for row in self.grid:
            if all(row):
                cleared += 1
            else:
                new_grid.append(row)
        while len(new_grid) < GRID_HEIGHT:
            new_grid.insert(0, [0]*GRID_WIDTH)

        self.grid = new_grid
        if cleared:
            # Standard Tetris scoring
            scoring = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += scoring.get(cleared, 0) * self.level
            self.level = self.score // 1000 + 1
            self.drop_interval = max(100, 500 - (self.level - 1) * 50)

    def move_piece(self, dx):
        self.current_piece.x += dx
        if self.collision(self.current_piece):
            self.current_piece.x -= dx

    def move_down(self):
        self.current_piece.y += 1
        if self.collision(self.current_piece):
            self.current_piece.y -= 1
            self.lock_piece(self.current_piece)

    def hard_drop(self):
        if self.collision(self.current_piece):
            return
        while not self.collision(self.current_piece):
            self.current_piece.y += 1
        self.current_piece.y -= 1
        self.lock_piece(self.current_piece)

    def rotate_piece(self):
        old_rotation = self.current_piece.rotation
        old_shape = self.current_piece.shape
        self.current_piece.rotate()
        if self.collision(self.current_piece):
            self.current_piece.rotation = old_rotation
            self.current_piece.shape = old_shape

    def draw(self):
        self.screen.fill(MONOKAI['background'])

        # Draw Grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[y][x]:
                    color = MONOKAI['pieces'][self.grid[y][x]-1]
                else:
                    color = MONOKAI['grid_fill']
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, MONOKAI['grid_line'], rect, 1)

        # Draw Current Piece
        for x, y in self.current_piece.get_cells():
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, MONOKAI['pieces'][self.current_piece.shape_id], rect)
                pygame.draw.rect(self.screen, MONOKAI['grid_line'], rect, 1)

        # Draw UI (Score, Level, Next Piece)
        ui_x = GRID_WIDTH * CELL_SIZE + 20
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        level_text = self.font.render(f'Level: {self.level}', True, (255, 255, 255))
        next_label = self.font.render('Next:', True, (255, 255, 255))

        self.screen.blit(score_text, (ui_x, 20))
        self.screen.blit(level_text, (ui_x, 60))
        self.screen.blit(next_label, (ui_x, 150))

        # Draw Next Piece Preview
        for y, row in enumerate(self.next_piece.shape):
            for x, val in enumerate(row):
                if val:
                    rect = pygame.Rect(ui_x + x*20, 190 + y*20, 20, 20)
                    pygame.draw.rect(self.screen, MONOKAI['pieces'][self.next_piece.shape_id], rect)

        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            over_text = self.font.render('GAME OVER', True, (255, 0, 0))
            restart_text = self.font.render('Press R to Restart', True, (255, 255, 255))
            self.screen.blit(over_text, (WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT//2 - 20))
            self.screen.blit(restart_text, (WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2 + 20))

        pygame.display.update()

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                    else:
                        if event.key == pygame.K_LEFT: self.move_piece(-1)
                        elif event.key == pygame.K_RIGHT: self.move_piece(1)
                        elif event.key == pygame.K_DOWN: self.move_down()
                        elif event.key == pygame.K_UP: self.rotate_piece()
                        elif event.key == pygame.K_SPACE: self.hard_drop()
                        elif event.key == pygame.K_p: self.paused = not self.paused
                        elif event.key == pygame.K_r: self.reset_game()

            if not self.game_over and not self.paused:
                now = pygame.time.get_ticks()
                if now - self.drop_time > self.drop_interval:
                    self.move_down()
                    self.drop_time = now

            self.draw()

if __name__ == '__main__':
    game = TetrisGame()
    game.run()
