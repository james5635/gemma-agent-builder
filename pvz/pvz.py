import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Window Setup
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Synthwave / Neon Color Palette
COLOR_BG_TOP = (20, 10, 40)
COLOR_BG_BOT = (50, 20, 80)
COLOR_GRID = (0, 255, 255)  # Neon Cyan
COLOR_SUN = (255, 255, 0)   # Neon Yellow
COLOR_ZOMBIE = (255, 0, 255) # Neon Magenta
COLOR_PEASHOOTER = (0, 255, 150) # Neon Green
COLOR_SUNFLOWER = (255, 150, 0)  # Neon Orange
COLOR_PROJECTILE = (0, 255, 255) # Neon Cyan
COLOR_TEXT = (255, 255, 255)
COLOR_UI_BG = (30, 10, 60)
COLOR_UI_BORDER = (200, 0, 255)

# Game Constants
GRID_ROWS = 5
GRID_COLS = 9
CELL_WIDTH = 80
CELL_HEIGHT = 100
OFFSET_X = 160
OFFSET_Y = 100

def load_asset(path, width, height):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (width, height))
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

class Sun:
    def __init__(self, x, y, is_natural=True):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.is_natural = is_natural
        self.life = 500
        self.y_vel = random.uniform(0.5, 1.5) if is_natural else 0
        try:
            self.image = pygame.image.load("sun.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
        except:
            self.image = None

    def update(self):
        if self.is_natural:
            self.rect.y += self.y_vel
            if self.rect.y > SCREEN_HEIGHT - 60:
                self.rect.y = SCREEN_HEIGHT - 60
                self.is_natural = False # Stop moving once hit ground
        self.life -= 1

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # Fallback glow effect
            for r in range(25, 15, -5):
                alpha = 100 - (r * 4)
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*COLOR_SUN, alpha), (r, r), r)
                screen.blit(s, (self.rect.centerx - r, self.rect.centery - r))
            pygame.draw.circle(screen, COLOR_SUN, self.rect.center, 12)

class Projectile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 15, 15)
        self.speed = 12 # Increased speed from 7 to 12


    def update(self):
        self.rect.x += self.speed

    def draw(self, screen):
        # Neon glow bullet
        pygame.draw.circle(screen, (200, 255, 255), self.rect.center, 8)
        pygame.draw.circle(screen, COLOR_PROJECTILE, self.rect.center, 5)

class Plant:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, CELL_WIDTH - 20, CELL_HEIGHT - 20)
        self.type = type
        self.health = 100
        self.timer = 0
        self.image = load_asset(f"{type}.png", CELL_WIDTH - 20, CELL_HEIGHT - 20)

    def update(self, game):
        self.timer += 1
        if self.type == "sunflower" and self.timer >= 150: # Fast production: 150 frames (~2.5s)
            game.suns.append(Sun(self.rect.centerx + random.randint(-30, 30), 
                                 self.rect.centery + random.randint(-30, 30), False))
            self.timer = 0
        elif self.type == "peashooter" and self.timer >= 60: # Fast attack: 60 frames (1s)
            if any(z.rect.y // CELL_HEIGHT == self.rect.y // CELL_HEIGHT for z in game.zombies):
                game.projectiles.append(Projectile(self.rect.right, self.rect.centery))
                self.timer = 0
        elif self.type == "peashooter" and self.timer >= 120:
            if any(z.rect.y // CELL_HEIGHT == self.rect.y // CELL_HEIGHT for z in game.zombies):
                game.projectiles.append(Projectile(self.rect.right, self.rect.centery))
                self.timer = 0

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            color = COLOR_PEASHOOTER if self.type == "peashooter" else COLOR_SUNFLOWER
            pygame.draw.circle(screen, color, self.rect.center, 25, 3)
            pygame.draw.circle(screen, color, self.rect.center, 15)
        
        # Health bar neon
        pygame.draw.rect(screen, (50, 0, 50), (self.rect.x, self.rect.y - 10, 60, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 10, 60 * (self.health / 100), 5))

class Zombie:
    def __init__(self, row):
        self.rect = pygame.Rect(SCREEN_WIDTH, row * CELL_HEIGHT + OFFSET_Y + 10, 50, 80)
        self.speed = 0.6  # Reduced speed for better balance
        self.health = 100
        self.attack_cooldown = 0
        self.image = load_asset("zombie.png", 50, 80)

    def update(self, plants):
        collision = False
        for plant in plants:
            if self.rect.colliderect(plant.rect):
                collision = True
                self.attack_cooldown += 1
                if self.attack_cooldown >= 60:
                    plant.health -= 20
                    self.attack_cooldown = 0
                break
        if not collision:
            self.rect.x -= self.speed
            self.attack_cooldown = 0

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # Neon Zombie (Hologram style)
            pygame.draw.rect(screen, COLOR_ZOMBIE, self.rect, 3, border_radius=10)
            pygame.draw.circle(screen, COLOR_ZOMBIE, (self.rect.centerx, self.rect.y + 20), 12, 2)
            # Glowing eyes
            pygame.draw.circle(screen, (255, 255, 255), (self.rect.centerx - 5, self.rect.y + 18), 3)
            pygame.draw.circle(screen, (255, 255, 255), (self.rect.centerx + 5, self.rect.y + 18), 3)
        
        # Health bar
        pygame.draw.rect(screen, (50, 0, 50), (self.rect.x + 5, self.rect.y - 20, 40, 5))
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x + 5, self.rect.y - 20, 40 * (self.health / 100), 5))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NEON PLANTS VS ZOMBIES")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 20, bold=True)
        self.button_font = pygame.font.SysFont("Courier New", 14, bold=True)
        self.frame_count = 0
        self.reset()

    def reset(self):
        self.sun_score = 100
        self.plants = []
        self.zombies = []
        self.suns = []
        self.projectiles = []
        self.selected_plant = None
        self.game_over = False
        self.frame_count = 0

    def spawn_sun(self):
        # Spawn above the screen and let them drop
        self.suns.append(Sun(random.randint(OFFSET_X, SCREEN_WIDTH - 50), 
                             random.randint(-100, 0)))

    def update(self):
        if self.game_over: return
        self.frame_count += 1
        
        # Difficulty scaling: zombie spawn rate starts slow and increases
        zombie_spawn_chance = min(0.06, 0.003 + (self.frame_count / 15000) * 0.057)
        if random.random() < zombie_spawn_chance:
            # Cluster size increases over time: at 1 min (3600 frames), min cluster is 10
            min_cluster = int(1 + (self.frame_count / 3600) * 9)
            max_cluster = min_cluster + random.randint(0, 5)
            for _ in range(random.randint(min_cluster, max_cluster)):
                self.zombies.append(Zombie(random.randint(0, GRID_ROWS - 1)))
            
        # Natural suns spawn at a steady rate
        if random.random() < 0.01:
            self.spawn_sun()

        for s in self.suns[:]:
            s.update()
            if s.life <= 0: self.suns.remove(s)
        for p in self.plants[:]:
            p.update(self)
            if p.health <= 0: self.plants.remove(p)
        for z in self.zombies[:]:
            z.update(self.plants)
            if z.rect.x < OFFSET_X: self.game_over = True
            if z.health <= 0: self.zombies.remove(z)
        for pr in self.projectiles[:]:
            pr.update()
            for z in self.zombies[:]:
                if pr.rect.colliderect(z.rect):
                    z.health -= 20
                    if pr in self.projectiles: self.projectiles.remove(pr)
                    break
            if pr.rect.x > SCREEN_WIDTH:
                if pr in self.projectiles: self.projectiles.remove(pr)

    def draw_bg(self):
        # Synthwave gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (
                int(COLOR_BG_TOP[0] * (1 - ratio) + COLOR_BG_BOT[0] * ratio),
                int(COLOR_BG_TOP[1] * (1 - ratio) + COLOR_BG_BOT[1] * ratio),
                int(COLOR_BG_TOP[2] * (1 - ratio) + COLOR_BG_BOT[2] * ratio)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def draw(self):
        self.draw_bg()
        
        # Neon Grid
        for r in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, COLOR_GRID, (OFFSET_X, OFFSET_Y + r * CELL_HEIGHT), 
                             (SCREEN_WIDTH, OFFSET_Y + r * CELL_HEIGHT), 2)
        for c in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, COLOR_GRID, (OFFSET_X + c * CELL_WIDTH, OFFSET_Y), 
                             (OFFSET_X + c * CELL_WIDTH, OFFSET_Y + GRID_ROWS * CELL_HEIGHT), 2)

        # UI Panel
        pygame.draw.rect(self.screen, COLOR_UI_BG, (0, 0, 140, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (140, 0), (140, SCREEN_HEIGHT), 3)
        
        sun_text = self.font.render(f"SUN: {self.sun_score}", True, COLOR_TEXT)
        self.screen.blit(sun_text, (20, 30))
        
        # Duration Timer
        time_seconds = self.frame_count // 60
        hours = time_seconds // 3600
        minutes = (time_seconds % 3600) // 60
        seconds = time_seconds % 60
        time_text = self.font.render(f"TIME: {hours:02d}:{minutes:02d}:{seconds:02d}", True, COLOR_TEXT)
        self.screen.blit(time_text, (20, 60))

        self.draw_button("SUNFLOWER", 0, 100, COLOR_SUNFLOWER, 50)
        self.draw_button("PEA-SHOT", 1, 100, COLOR_PEASHOOTER, 100)

        for s in self.suns: s.draw(self.screen)
        for p in self.plants: p.draw(self.screen)
        for z in self.zombies: z.draw(self.screen)
        for pr in self.projectiles: pr.draw(self.screen)

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            go_text = self.font.render("SYSTEM FAILURE: BRAINS CONSUMED", True, (255, 0, 0))
            restart_text = self.font.render("PRESS 'R' TO REBOOT SYSTEM", True, (255, 255, 255))
            self.screen.blit(go_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()

    def draw_button(self, name, index, y, color, cost):
        rect = pygame.Rect(15, y + (index * 80), 110, 60)
        pygame.draw.rect(self.screen, (20, 0, 40), rect, border_radius=5)
        pygame.draw.rect(self.screen, color, rect, 2, border_radius=5)
        
        # Icon
        plant_type = "sunflower" if "SUNFLOWER" in name else "peashooter"
        try:
            icon_img = pygame.image.load(f"{plant_type}.png").convert_alpha()
            icon_img = pygame.transform.scale(icon_img, (30, 30))
            self.screen.blit(icon_img, (rect.x + 5, rect.y + 15))
        except:
            pass

        # Use smaller button_font and adjust positions to fit boundaries
        txt = self.button_font.render(f"{name}", True, color)
        cost_txt = self.button_font.render(f"{cost} S", True, COLOR_TEXT)
        self.screen.blit(txt, (rect.x + 40, rect.y + 12))
        self.screen.blit(cost_txt, (rect.x + 40, rect.y + 32))

    def handle_click(self, pos):
        for s in self.suns[:]:
            if s.rect.collidepoint(pos):
                self.sun_score += 25
                self.suns.remove(s)
                return
        if pos[0] < 140:
            if 100 < pos[1] < 160: self.selected_plant = "sunflower"
            elif 170 < pos[1] < 230: self.selected_plant = "peashooter"
            return
        if self.selected_plant:
            cost = 50 if self.selected_plant == "sunflower" else 100
            if self.sun_score >= cost:
                col = (pos[0] - OFFSET_X) // CELL_WIDTH
                row = (pos[1] - OFFSET_Y) // CELL_HEIGHT
                if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                    if not any(p.rect.collidepoint(pos) for p in self.plants):
                        self.plants.append(Plant(OFFSET_X + col * CELL_WIDTH + 10, 
                                               OFFSET_Y + row * CELL_HEIGHT + 10, 
                                               self.selected_plant))
                        self.sun_score -= cost
                        self.selected_plant = None
            else:
                self.selected_plant = None

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
