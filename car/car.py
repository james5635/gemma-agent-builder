import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Window Setup
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
FPS = 60

# Colors (Neon Synthwave Theme)
BG_COLOR = (10, 8, 22)
ROAD_COLOR = (20, 15, 35)
LINE_COLOR = (0, 229, 255)  # Neon Cyan
PLAYER_COLOR = (255, 46, 99)  # Neon Magenta
ENEMY_COLOR = (255, 215, 0)   # Gold
TEXT_COLOR = (255, 255, 255)

# Game Constants
CAR_WIDTH = 50
CAR_HEIGHT = 90
PLAYER_START_X = (SCREEN_WIDTH // 2) - (CAR_WIDTH // 2)
PLAYER_START_Y = SCREEN_HEIGHT - 120
LANE_WIDTH = SCREEN_WIDTH // 4

class Car:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT)
        self.color = color
        self.speed = 0

    def draw(self, screen):
        # Draw car body
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        # Draw windshield
        windshield_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 15, CAR_WIDTH - 10, 20)
        pygame.draw.rect(screen, (50, 50, 80), windshield_rect, border_radius=4)
        # Draw headlights
        pygame.draw.circle(screen, (255, 255, 200), (self.rect.x + 10, self.rect.y + 5), 5)
        pygame.draw.circle(screen, (255, 255, 200), (self.rect.x + CAR_WIDTH - 10, self.rect.y + 5), 5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NEON RACER")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.reset()

    def reset(self):
        self.player = Car(PLAYER_START_X, PLAYER_START_Y, PLAYER_COLOR)
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.lane_offset = 0
        self.enemy_spawn_timer = 0
        self.game_speed = 5
        self.current_speed = 5

    def spawn_enemy(self):
        # Try to find a lane that is clear enough
        available_lanes = [0, 1, 2, 3]
        random.shuffle(available_lanes)
        
        for lane in available_lanes:
            x = lane * LANE_WIDTH + (LANE_WIDTH - CAR_WIDTH) // 2
            too_close = False
            for enemy in self.enemies:
                if enemy.rect.x == x and enemy.rect.bottom < 300:
                    too_close = True
                    break
            
            if not too_close:
                enemy = Car(x, -CAR_HEIGHT, ENEMY_COLOR)
                # Difficulty scaling: increase speed variance as score grows
                variance = 1 + (self.score // 10) * 0.5
                enemy.speed = random.uniform(-variance, variance)
                self.enemies.append(enemy)
                return

    def update(self):
        if self.game_over:
            return

        # Player movement
        keys = pygame.key.get_pressed()
        
        # Forward boost
        self.current_speed = self.game_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.current_speed += 5  # Boost speed when pressing up

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.player.rect.left > 0:
            self.player.rect.x -= 7
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.player.rect.right < SCREEN_WIDTH:
            self.player.rect.x += 7

        # Road scrolling
        self.lane_offset += self.current_speed
        if self.lane_offset >= 100:
            self.lane_offset = 0

        # Enemy spawning
        # Difficulty scaling: spawn cars more frequently as score increases
        spawn_interval = max(30, 60 - (self.score // 2))
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > spawn_interval:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.rect.y += self.current_speed + enemy.speed
            if enemy.rect.top > SCREEN_HEIGHT:
                self.enemies.remove(enemy)
                self.score += 1
                # Increase speed more aggressively every 5 points
                if self.score % 5 == 0:
                    self.game_speed += 0.5

            # Collision detection
            if self.player.rect.colliderect(enemy.rect):
                self.game_over = True

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Draw Road
        pygame.draw.rect(self.screen, ROAD_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Draw Lane Markers
        for i in range(1, 4):
            x = i * LANE_WIDTH
            for y in range(-100, SCREEN_HEIGHT, 100):
                pygame.draw.line(self.screen, LINE_COLOR, (x, y + self.lane_offset), (x, y + 50 + self.lane_offset), 3)

        # Draw Cars
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw Score
        score_text = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        speed_text = self.font.render(f"SPEED: {int(self.current_speed)}", True, LINE_COLOR)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(speed_text, (20, 50))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            go_text = self.font.render("GAME OVER", True, PLAYER_COLOR)
            restart_text = self.font.render("Press 'R' to Restart", True, TEXT_COLOR)
            
            self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset()

            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    Game().run()
