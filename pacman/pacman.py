import pygame
import random
import copy

# Constants
TILE_SIZE = 30
GRID_WIDTH = 19
GRID_HEIGHT = 21
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 10

# Colors (Palenight)
BLACK = (36, 39, 58)
YELLOW = (252, 233, 79)
BLUE = (130, 170, 255)
WHITE = (234, 239, 242)
RED = (255, 85, 114)
GHOST_COLORS = [(255, 85, 114), (199, 146, 234), (137, 221, 255), (255, 184, 108)]
TEXT_COLOR = (234, 239, 242)

# Original Maze for resetting
ORIGINAL_MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,1,1,2,1,2,1,1,1,0,1,1,1,1],
    [2,2,2,1,0,1,2,2,2,2,2,2,2,1,0,1,2,2,2],
    [1,1,1,1,0,1,2,1,1,2,1,1,2,1,0,1,1,1,1],
    [2,2,2,2,0,2,2,1,2,2,2,1,2,2,0,2,2,2,2],
    [1,1,1,1,0,1,2,1,1,1,1,1,2,1,0,1,1,1,1],
    [2,2,2,1,0,1,2,2,2,2,2,2,2,1,0,1,2,2,2],
    [1,1,1,1,0,1,2,1,1,1,1,1,2,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,1,0,0,0,0,0,2,0,0,0,0,0,1,0,0,1],
    [1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

MAZE = copy.deepcopy(ORIGINAL_MAZE)

class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.score = 0
        
        # Load Pacman image from local file
        try:
            self.image = pygame.image.load("assets/pacman.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            print(f"Error loading Pacman image: {e}")
            self.image = None

    def move(self):
        new_x = self.x + self.vel_x
        new_y = self.y + self.vel_y
        if 0 <= new_y < GRID_HEIGHT and 0 <= new_x < GRID_WIDTH and MAZE[new_y][new_x] != 1:
            self.x = new_x
            self.y = new_y
            if MAZE[self.y][self.x] == 0:
                MAZE[self.y][self.x] = 2
                self.score += 10

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE))
        else:
            # Fallback to circle
            center = (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.circle(screen, YELLOW, center, TILE_SIZE // 2 - 2)

class Ghost:
    def __init__(self, x, y, color, ghost_index=0):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        
        # Load Ghost image from local file
        try:
            image_path = f"assets/ghost_{ghost_index % 4}.png"
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            print(f"Error loading Ghost image {ghost_index}: {e}")
            self.image = None

    def move(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and MAZE[new_y][new_x] != 1:
                self.x = new_x
                self.y = new_y
                break

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE))
        else:
            pygame.draw.rect(screen, self.color, (self.x * TILE_SIZE + 2, self.y * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4), border_radius=5)

def main():
    global MAZE
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pacman - Palenight")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 32)

    pacman = Pacman(9, 15)
    ghosts = [Ghost(9, 9, GHOST_COLORS[i], i) for i in range(4)]
    
    game_over = False
    running = True

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_UP:
                        pacman.vel_x, pacman.vel_y = 0, -1
                    elif event.key == pygame.K_DOWN:
                        pacman.vel_x, pacman.vel_y = 0, 1
                    elif event.key == pygame.K_LEFT:
                        pacman.vel_x, pacman.vel_y = -1, 0
                    elif event.key == pygame.K_RIGHT:
                        pacman.vel_x, pacman.vel_y = 1, 0
                else:
                    if event.key == pygame.K_r:
                        # Reset Game
                        MAZE = copy.deepcopy(ORIGINAL_MAZE)
                        pacman = Pacman(9, 15)
                        ghosts = [Ghost(9, 9, GHOST_COLORS[i], i) for i in range(4)]
                        game_over = False

        if not game_over:
            pacman.move()

            for ghost in ghosts:
                ghost.move()
                if ghost.x == pacman.x and ghost.y == pacman.y:
                    game_over = True

            # Draw Maze
            for r in range(GRID_HEIGHT):
                for c in range(GRID_WIDTH):
                    if MAZE[r][c] == 1:
                        pygame.draw.rect(screen, BLUE, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    elif MAZE[r][c] == 0:
                        pygame.draw.circle(screen, WHITE, (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2), 2)

            pacman.draw(screen)
            for ghost in ghosts:
                ghost.draw(screen)
        else:
            # Game Over Screen
            msg = font.render(f"Game Over! Score: {pacman.score}", True, RED)
            restart_msg = font.render("Press 'R' to Restart", True, WHITE)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(restart_msg, (SCREEN_WIDTH // 2 - restart_msg.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        # Draw Score
        score_text = font.render(f"Score: {pacman.score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
