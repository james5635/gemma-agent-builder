import pygame
import random

# Initialize pygame
pygame.init()

# Layout Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Calculated Sizes and Offsets
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50
SIDEBAR_X = 390
SIDEBAR_Y = 50
SIDEBAR_WIDTH = 260
SIDEBAR_HEIGHT = 600

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700

# Color Sentinels & Themes (Neon Synthwave Style)
BLACK = (0, 0, 0)                  # Logical sentinel for empty grid cell
BACKGROUND_COLOR = (12, 10, 20)     # Deep dark space blue
GRID_BG_COLOR = (18, 16, 28)        # Slightly lighter container blue
GRID_LINE_COLOR = (28, 25, 45)      # Grid cell divider line
BORDER_COLOR = (74, 56, 117)        # Glowing purple borders
GHOST_COLOR = (50, 45, 75)          # Sleek shadow outline color for the ghost piece
TEXT_PRIMARY = (255, 255, 255)      # Bright white for stats values
TEXT_MUTED = (140, 130, 175)        # Light violet-grey for stat labels

# Premium Glowing Neon Piece Colors
COLORS = [
    (0, 229, 255),    # I - Cyan
    (255, 215, 0),    # O - Gold
    (186, 104, 200),  # T - Purple
    (102, 255, 0),    # S - Green
    (255, 46, 99),     # Z - Red
    (37, 117, 252),   # J - Blue
    (255, 107, 0),    # L - Orange
]

# Tetromino Shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]


class Piece:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape = SHAPES[shape_idx]
        self.color = COLORS[shape_idx]
        self.shape_idx = shape_idx

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


class Tetris:
    def __init__(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.hold_piece = None
        self.can_hold = True

    def new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        piece = Piece(GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2, 0, shape_idx)
        return piece

    def check_collision(self, dx=0, dy=0, piece=None):
        if piece is None:
            piece = self.current_piece

        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    nx, ny = piece.x + x + dx, piece.y + y + dy

                    # Boundary and Wall Collisions
                    if nx < 0 or nx >= GRID_WIDTH or ny >= GRID_HEIGHT:
                        return True

                    # Grid Occupancy (only if ny is within valid range)
                    if ny >= 0 and self.grid[ny][nx] != BLACK:
                        return True
        return False

    def freeze(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if self.current_piece.y + y < 0:
                        self.game_over = True
                        return
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = (
                        self.current_piece.color
                    )

        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.can_hold = True
        if self.check_collision():
            self.game_over = True

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell != BLACK for cell in self.grid[y]):
                lines_cleared += 1
                del self.grid[y]
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
            else:
                y -= 1

        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            score_map = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += score_map.get(lines_cleared, 0) * self.level
            self.level = (self.lines_cleared // 10) + 1

    def move(self, dx, dy):
        if not self.check_collision(dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        elif dy > 0:
            self.freeze()
        return False

    def hard_drop(self):
        while not self.check_collision(0, 1):
            self.current_piece.y += 1
        self.freeze()

    def rotate(self):
        old_shape = self.current_piece.shape
        old_x = self.current_piece.x
        old_y = self.current_piece.y
        self.current_piece.rotate()

        # Multi-kick offset list [dx, dy] testing standard wall kicks & floor kicks
        kicks = [
            [0, 0],    # No kick
            [-1, 0],   # Kick left 1
            [1, 0],    # Kick right 1
            [0, -1],   # Kick up 1 (floor kick)
            [-2, 0],   # Kick left 2 (for horizontal I piece near wall)
            [2, 0],    # Kick right 2
            [0, -2],   # Kick up 2 (floor kick for vertical pieces)
        ]

        for dx, dy in kicks:
            if not self.check_collision(dx, dy):
                self.current_piece.x += dx
                self.current_piece.y += dy
                return

        # If all kicks fail, revert to previous state
        self.current_piece.shape = old_shape
        self.current_piece.x = old_x
        self.current_piece.y = old_y

    def hold(self):
        if not self.can_hold:
            return False

        if self.hold_piece is None:
            self.hold_piece = Piece(
                0, 0, self.current_piece.shape_idx
            )  # Just store shape/color
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
        else:
            temp = self.hold_piece
            self.hold_piece = Piece(0, 0, self.current_piece.shape_idx)
            self.current_piece = Piece(
                GRID_WIDTH // 2 - len(SHAPES[temp.shape_idx][0]) // 2, 0, temp.shape_idx
            )

        self.can_hold = False
        # Check if new piece collides immediately
        if self.check_collision():
            self.game_over = True
        return True

    def get_ghost_position(self):
        ghost_y = self.current_piece.y
        while not self.check_collision(0, (ghost_y + 1) - self.current_piece.y):
            ghost_y += 1
        return ghost_y


def draw_block(screen, x, y, color):
    """Draws a beautiful block with 3D bevels and a sleek dark separator line."""
    # Main block body
    pygame.draw.rect(screen, color, (x, y, BLOCK_SIZE, BLOCK_SIZE))

    # Highlight (top and left edges)
    highlight_color = tuple(min(255, c + 50) for c in color)
    pygame.draw.line(screen, highlight_color, (x, y), (x + BLOCK_SIZE - 1, y), 2)
    pygame.draw.line(screen, highlight_color, (x, y), (x, y + BLOCK_SIZE - 1), 2)

    # Shadow (bottom and right edges)
    shadow_color = tuple(max(0, c - 50) for c in color)
    pygame.draw.line(screen, shadow_color, (x, y + BLOCK_SIZE - 1), (x + BLOCK_SIZE - 1, y + BLOCK_SIZE - 1), 2)
    pygame.draw.line(screen, shadow_color, (x + BLOCK_SIZE - 1, y), (x + BLOCK_SIZE - 1, y + BLOCK_SIZE - 1), 2)

    # Sleek dark inner border to separate blocks cleanly
    pygame.draw.rect(screen, (8, 6, 15), (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)


def draw_piece_centered(screen, piece, box_x, box_y, box_w, box_h):
    """Centers and draws a piece shape inside a bounding box."""
    if not piece:
        return
    shape = piece.shape
    rows = len(shape)
    cols = len(shape[0])

    start_x = box_x + (box_w - cols * BLOCK_SIZE) // 2
    start_y = box_y + (box_h - rows * BLOCK_SIZE) // 2

    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                draw_block(screen, start_x + x * BLOCK_SIZE, start_y + y * BLOCK_SIZE, piece.color)


def draw_text_centered(screen, text_surface, center_x, y):
    """Draws a rendered text surface centered on a specific X coordinate."""
    rect = text_surface.get_rect(center=(center_x, y))
    screen.blit(text_surface, rect)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris - Premium Neon Edition")
    clock = pygame.time.Clock()
    game = Tetris()

    # Enable smooth keyboard repeats for responsive gameplay
    pygame.key.set_repeat(200, 50)

    # Load clean fonts with safe fallbacks
    pygame.font.init()
    try:
        font_large = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 34, bold=True)
        font_medium = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 22, bold=True)
        font_small = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 14, bold=True)
    except Exception:
        font_large = pygame.font.Font(None, 40)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 18)

    fall_time = 0
    running = True

    while running:
        # Limits framerate to 60 FPS and captures elapsed milliseconds
        dt = clock.tick(60)

        if not game.paused and not game.game_over:
            fall_time += dt
            # Dynamic fall speed based on current level
            current_fall_speed = max(100, 500 - (game.level - 1) * 50)
            if fall_time > current_fall_speed:
                game.move(0, 1)
                fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game.paused = not game.paused

                if game.game_over and event.key == pygame.K_r:
                    game = Tetris()

                if not game.game_over and not game.paused:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    if event.key == pygame.K_DOWN:
                        game.move(0, 1)
                    if event.key == pygame.K_UP:
                        game.rotate()
                    if event.key == pygame.K_SPACE:
                        game.hard_drop()
                    if event.key == pygame.K_c:
                        game.hold()

        # Render Phase
        screen.fill(BACKGROUND_COLOR)

        # 1. Draw Grid Outer Border
        pygame.draw.rect(
            screen,
            BORDER_COLOR,
            (
                GRID_X_OFFSET - 2,
                GRID_Y_OFFSET - 2,
                GRID_WIDTH * BLOCK_SIZE + 4,
                GRID_HEIGHT * BLOCK_SIZE + 4,
            ),
            2,
        )

        # Draw Cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_rect = (
                    x * BLOCK_SIZE + GRID_X_OFFSET,
                    y * BLOCK_SIZE + GRID_Y_OFFSET,
                    BLOCK_SIZE,
                    BLOCK_SIZE,
                )
                if game.grid[y][x] == BLACK:
                    # Draw a nice clean empty cell background
                    pygame.draw.rect(screen, GRID_BG_COLOR, cell_rect)
                    pygame.draw.rect(screen, GRID_LINE_COLOR, cell_rect, 1)
                else:
                    draw_block(screen, cell_rect[0], cell_rect[1], game.grid[y][x])

        # 2. Draw Active Piece & Ghost Shadow
        if not game.game_over:
            # Draw Ghost Piece Outline (Only if not directly overlapping active piece)
            ghost_y = game.get_ghost_position()
            if ghost_y > game.current_piece.y:
                for y, row in enumerate(game.current_piece.shape):
                    for x, cell in enumerate(row):
                        if cell:
                            pygame.draw.rect(
                                screen,
                                GHOST_COLOR,
                                (
                                    (game.current_piece.x + x) * BLOCK_SIZE + GRID_X_OFFSET,
                                    (ghost_y + y) * BLOCK_SIZE + GRID_Y_OFFSET,
                                    BLOCK_SIZE - 1,
                                    BLOCK_SIZE - 1,
                                ),
                                2,  # Outline border width
                            )

            # Draw Current Active Piece
            for y, row in enumerate(game.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        draw_block(
                            screen,
                            (game.current_piece.x + x) * BLOCK_SIZE + GRID_X_OFFSET,
                            (game.current_piece.y + y) * BLOCK_SIZE + GRID_Y_OFFSET,
                            game.current_piece.color,
                        )

        # 3. Draw Sidebar Panel Card
        pygame.draw.rect(
            screen,
            GRID_BG_COLOR,
            (SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT),
        )
        pygame.draw.rect(
            screen,
            BORDER_COLOR,
            (SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT),
            2,
        )

        # Display beautiful label-value stat items
        def draw_stat(lbl_text, val_text, start_y):
            lbl_surf = font_small.render(lbl_text, True, TEXT_MUTED)
            val_surf = font_large.render(val_text, True, TEXT_PRIMARY)
            screen.blit(lbl_surf, (SIDEBAR_X + 25, start_y))
            screen.blit(val_surf, (SIDEBAR_X + 25, start_y + 18))

        draw_stat("SCORE", f"{game.score}", SIDEBAR_Y + 20)
        draw_stat("LEVEL", f"{game.level}", SIDEBAR_Y + 85)
        draw_stat("LINES CLEARED", f"{game.lines_cleared}", SIDEBAR_Y + 150)

        # 4. Next Piece Preview Panel
        next_lbl = font_small.render("NEXT PIECE", True, TEXT_MUTED)
        screen.blit(next_lbl, (SIDEBAR_X + 25, SIDEBAR_Y + 225))

        next_box_x = SIDEBAR_X + 25
        next_box_y = SIDEBAR_Y + 248
        next_box_size = 110
        pygame.draw.rect(screen, BACKGROUND_COLOR, (next_box_x, next_box_y, next_box_size, next_box_size))
        pygame.draw.rect(screen, BORDER_COLOR, (next_box_x, next_box_y, next_box_size, next_box_size), 1)
        if not game.game_over:
            draw_piece_centered(screen, game.next_piece, next_box_x, next_box_y, next_box_size, next_box_size)

        # 5. Hold Piece Preview Panel
        hold_lbl = font_small.render("HOLD PIECE", True, TEXT_MUTED)
        screen.blit(hold_lbl, (SIDEBAR_X + 25, SIDEBAR_Y + 380))

        hold_box_x = SIDEBAR_X + 25
        hold_box_y = SIDEBAR_Y + 403
        hold_box_size = 110
        pygame.draw.rect(screen, BACKGROUND_COLOR, (hold_box_x, hold_box_y, hold_box_size, hold_box_size))
        pygame.draw.rect(screen, BORDER_COLOR, (hold_box_x, hold_box_y, hold_box_size, hold_box_size), 1)
        if not game.game_over and game.hold_piece:
            draw_piece_centered(screen, game.hold_piece, hold_box_x, hold_box_y, hold_box_size, hold_box_size)

        # Keyboard Controls Legend
        instructions = [
            "← / → : Move Left / Right",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "↑ : Rotate Piece",
            "C : Hold Piece",
            "P : Pause / Resume",
        ]
        inst_y = SIDEBAR_Y + 520
        for inst in instructions:
            inst_surf = font_small.render(inst, True, TEXT_MUTED)
            screen.blit(inst_surf, (SIDEBAR_X + 20, inst_y))
            inst_y += 18

        # 6. Overlay Screen (Paused or Game Over)
        if game.game_over or game.paused:
            # Draw dark semi-transparent screen over grid play area only
            overlay = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
            overlay.set_alpha(200)
            overlay.fill(BACKGROUND_COLOR)
            screen.blit(overlay, (GRID_X_OFFSET, GRID_Y_OFFSET))

            grid_center_x = GRID_X_OFFSET + (GRID_WIDTH * BLOCK_SIZE) // 2

            if game.game_over:
                over_surf = font_large.render("GAME OVER", True, (255, 46, 99))
                score_final_surf = font_medium.render(f"Final Score: {game.score}", True, TEXT_PRIMARY)
                restart_surf = font_medium.render("Press 'R' to Restart", True, TEXT_MUTED)

                draw_text_centered(screen, over_surf, grid_center_x, GRID_Y_OFFSET + 220)
                draw_text_centered(screen, score_final_surf, grid_center_x, GRID_Y_OFFSET + 280)
                draw_text_centered(screen, restart_surf, grid_center_x, GRID_Y_OFFSET + 340)

            elif game.paused:
                pause_surf = font_large.render("PAUSED", True, (0, 229, 255))
                resume_surf = font_medium.render("Press 'P' to Resume", True, TEXT_PRIMARY)

                draw_text_centered(screen, pause_surf, grid_center_x, GRID_Y_OFFSET + 260)
                draw_text_centered(screen, resume_surf, grid_center_x, GRID_Y_OFFSET + 320)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
