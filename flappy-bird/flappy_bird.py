import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
FPS = 60

# Neon Synthwave Color Palette
BACKGROUND_COLOR_TOP = (10, 8, 24)    # Sunset twilight deep purple
BACKGROUND_COLOR_BOT = (35, 12, 50)    # Sunset twilight violet
CITY_COLOR_1 = (18, 14, 38)            # Far city layer silhouette
CITY_COLOR_2 = (26, 18, 48)            # Near city layer silhouette
GROUND_BG_COLOR = (12, 10, 22)         # Deep space dark ground
GROUND_GRID_COLOR = (74, 56, 117)      # Glowing grid lines
PIPE_COLOR = (0, 229, 255)             # Neon Cyan pipe glow
TEXT_PRIMARY = (255, 255, 255)         # Pure white
TEXT_MUTED = (160, 140, 190)           # Light purple-grey
TEXT_ACCENT = (255, 46, 99)            # Electric Neon Red
GOLD = (255, 215, 0)                   # Metallic Gold

# States
STATE_START = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2


class Particle:
    """Represents a particle emitted behind the bird or in an explosion."""
    def __init__(self, x, y, burst=False):
        self.x = x
        self.y = y
        if burst:
            # Emit in any direction
            self.dx = random.uniform(-4, 4)
            self.dy = random.uniform(-4, 4)
            self.color = random.choice([GOLD, (255, 107, 0), TEXT_PRIMARY])
        else:
            # Flight trail drifting backwards
            self.dx = random.uniform(-2, -0.5)
            self.dy = random.uniform(-0.5, 0.5)
            self.color = (255, 107, 0)
        self.size = random.uniform(3, 6)
        self.life = 1.0  # Percentage of life left (1.0 -> 0.0)
        self.decay = random.uniform(0.03, 0.06)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= self.decay
        self.size = max(0, self.size - 0.15)

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


class Bird:
    """Represents the player-controlled neon bird with physics & flap animation."""
    def __init__(self):
        self.x = 120
        self.y = SCREEN_HEIGHT // 2
        self.radius = 14
        self.velocity = 0.0
        self.gravity = 0.35
        self.jump_strength = -7.5
        self.flap_tick = 0

    def jump(self, particles):
        self.velocity = self.jump_strength
        # Flap tail burst
        for _ in range(8):
            particles.append(Particle(self.x - 12, self.y, burst=True))

    def update(self, particles):
        self.velocity += self.gravity
        # Clamp falling speed
        if self.velocity > 10:
            self.velocity = 10
        self.y += self.velocity
        self.flap_tick += 1

        # Emit normal flight trail particle
        if random.random() > 0.3:
            particles.append(Particle(self.x - 12, self.y, burst=False))

    def get_mask(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, screen):
        # Calculate tilt based on current vertical velocity
        angle = -self.velocity * 4.5
        angle = max(-45, min(30, angle))  # Clamp tilt to look organic
        rad = math.radians(angle)

        # 1. Draw Tail (glowing orange triangle)
        tail_points = [
            (-10, -2),
            (-17, -6),
            (-14, 4)
        ]
        rotated_tail = []
        for px, py in tail_points:
            rx = px * math.cos(rad) - py * math.sin(rad)
            ry = px * math.sin(rad) + py * math.cos(rad)
            rotated_tail.append((self.x + rx, self.y + ry))
        pygame.draw.polygon(screen, GOLD, rotated_tail)
        pygame.draw.polygon(screen, (255, 107, 0), rotated_tail, 1)

        # 2. Draw Beak (Neon Orange triangle pointing forward)
        beak_points = [
            (10, -4),
            (20, 1),
            (10, 6)
        ]
        rotated_beak = []
        for px, py in beak_points:
            rx = px * math.cos(rad) - py * math.sin(rad)
            ry = px * math.sin(rad) + py * math.cos(rad)
            rotated_beak.append((self.x + rx, self.y + ry))
        pygame.draw.polygon(screen, (255, 107, 0), rotated_beak)
        pygame.draw.polygon(screen, TEXT_PRIMARY, rotated_beak, 1)

        # 3. Draw Round Fat Body (Gold Core with Neon Orange Glow Outline)
        pygame.draw.circle(screen, (255, 107, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), self.radius - 2)

        # 4. Draw Big Round Eye & Pupil
        eye_offset_x, eye_offset_y = 5, -4
        ex = eye_offset_x * math.cos(rad) - eye_offset_y * math.sin(rad)
        ey = eye_offset_x * math.sin(rad) + eye_offset_y * math.cos(rad)
        # White eye ball
        pygame.draw.circle(screen, TEXT_PRIMARY, (int(self.x + ex), int(self.y + ey)), 5)
        # Black pupil
        pupil_offset_x, pupil_offset_y = 6.5, -4
        px = pupil_offset_x * math.cos(rad) - pupil_offset_y * math.sin(rad)
        py = pupil_offset_x * math.sin(rad) + pupil_offset_y * math.cos(rad)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + px), int(self.y + py)), 2)

        # 5. Draw Flapping Round Wing
        wing_flap = math.sin(self.flap_tick * 0.45) * 6
        wing_points = [
            (-2, 2),
            (-9, -5 + wing_flap),
            (-13, 0 + wing_flap),
            (-6, 5)
        ]
        rotated_wing = []
        for px, py in wing_points:
            rx = px * math.cos(rad) - py * math.sin(rad)
            ry = px * math.sin(rad) + py * math.cos(rad)
            rotated_wing.append((self.x + rx, self.y + ry))
        pygame.draw.polygon(screen, TEXT_PRIMARY, rotated_wing)
        pygame.draw.polygon(screen, GOLD, rotated_wing, 1)


class CityscapeLayer:
    """Seamlessly looping cityscape background layer for parallax scrolling."""
    def __init__(self, layer_id, color, speed, width=60):
        self.layer_id = layer_id
        self.color = color
        self.speed = speed
        self.width = width
        self.buildings = []
        self.scroll = 0.0

        # Pre-fill buildings
        num_buildings = (SCREEN_WIDTH // self.width) + 3
        for _ in range(num_buildings):
            h = random.randint(120, 270) if layer_id == 1 else random.randint(60, 160)
            windows = []
            if layer_id == 2:  # Glowing cyber windows on the closer layer
                for wx in [12, 30, 48]:
                    for wy in range(20, h - 20, 30):
                        if random.random() > 0.45:
                            windows.append((wx, wy))
            self.buildings.append((h, windows))

    def update(self, delta):
        self.scroll += self.speed * delta
        if self.scroll >= self.width:
            self.scroll -= self.width
            # Rotate buildings loop
            first = self.buildings.pop(0)
            self.buildings.append(first)

    def draw(self, screen, ground_y):
        for i, (h, windows) in enumerate(self.buildings):
            bx = i * self.width - int(self.scroll)
            by = ground_y - h
            rect = (bx, by, self.width - 2, h)
            pygame.draw.rect(screen, self.color, rect)

            # Draw pre-compiled window pixels
            for wx, wy in windows:
                win_x = bx + wx
                win_y = by + wy
                if win_x < SCREEN_WIDTH:
                    pygame.draw.rect(screen, GOLD, (win_x, win_y, 4, 6))


class Pipe:
    """Obstacles that spawn and scroll horizontally."""
    def __init__(self, x, score):
        self.x = x
        self.width = 80
        # Slowly shrink pipe gap as score increases to scale up difficulty
        self.gap = max(145, 175 - (score // 5) * 5)
        self.gap_y = random.randint(180, SCREEN_HEIGHT - 240)
        self.passed = False

    def get_rects(self):
        top_h = self.gap_y - self.gap // 2
        bot_y = self.gap_y + self.gap // 2
        bot_h = SCREEN_HEIGHT - bot_y - 60  # Subtract ground level
        
        top_rect = pygame.Rect(self.x, 0, self.width, top_h)
        bottom_rect = pygame.Rect(self.x, bot_y, self.width, bot_h)
        return top_rect, bottom_rect

    def update(self, speed):
        self.x -= speed

    def draw(self, screen):
        top_rect, bottom_rect = self.get_rects()
        cap_h = 24
        cap_w = self.width + 8

        # Render Top Pipe with bright neon-cyan outline
        pygame.draw.rect(screen, (16, 12, 32), top_rect)
        pygame.draw.rect(screen, PIPE_COLOR, top_rect, 2)
        top_cap = pygame.Rect(self.x - 4, top_rect.bottom - cap_h, cap_w, cap_h)
        pygame.draw.rect(screen, (16, 12, 32), top_cap)
        pygame.draw.rect(screen, PIPE_COLOR, top_cap, 2)

        # Render Bottom Pipe
        pygame.draw.rect(screen, (16, 12, 32), bottom_rect)
        pygame.draw.rect(screen, PIPE_COLOR, bottom_rect, 2)
        bot_cap = pygame.Rect(self.x - 4, bottom_rect.top, cap_w, cap_h)
        pygame.draw.rect(screen, (16, 12, 32), bot_cap)
        pygame.draw.rect(screen, PIPE_COLOR, bot_cap, 2)


class Ground:
    """Horizon perspective grid matching retro-synthwave themes."""
    def __init__(self, speed):
        self.height = 60
        self.y = SCREEN_HEIGHT - self.height
        self.speed = speed
        self.scroll = 0.0

    def update(self, delta):
        self.scroll += self.speed * delta
        if self.scroll >= 30:  # Loop width of grid cell
            self.scroll -= 30

    def draw(self, screen):
        # Ground block
        pygame.draw.rect(screen, GROUND_BG_COLOR, (0, self.y, SCREEN_WIDTH, self.height))
        # Top glowing boundary line
        pygame.draw.line(screen, GROUND_GRID_COLOR, (0, self.y), (SCREEN_WIDTH, self.y), 3)

        # Perspective grid dividers scrolling towards the left
        for x in range(-30, SCREEN_WIDTH + 30, 30):
            gx = x - int(self.scroll)
            # Perspective slope lines
            pygame.draw.line(screen, GROUND_GRID_COLOR, (gx, self.y), (gx - 15, SCREEN_HEIGHT), 1)


def draw_sky_gradient(screen):
    """Draws a beautiful synthetic twilight skyline sunset color gradient."""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        color = tuple(
            int(BACKGROUND_COLOR_TOP[c] * (1.0 - ratio) + BACKGROUND_COLOR_BOT[c] * ratio)
            for c in range(3)
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))


def load_high_score():
    """Reads high score from the filesystem."""
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def save_high_score(score):
    """Saves high score to the filesystem."""
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    except Exception:
        pass


def draw_text_centered(screen, font, text, center_x, y, color):
    """Utility rendering text centered on a specific X coordinate."""
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(center_x, y))
    screen.blit(surf, rect)


def check_collision(bird, pipes, ground_y):
    """Verifies standard colliderects using a forgiving inner bird mask hitbox."""
    if bird.y - bird.radius < 0:  # Ceiling hit
        return True
    if bird.y + bird.radius > ground_y:  # Ground hit
        return True

    bird_rect = bird.get_mask()
    # Inflated/Forgiving bird rect (2-pixel margin on all sides) for smoother playability
    forgiving_bird = bird_rect.inflate(-4, -4)

    for pipe in pipes:
        top_rect, bottom_rect = pipe.get_rects()
        if forgiving_bird.colliderect(top_rect) or forgiving_bird.colliderect(bottom_rect):
            return True
    return False


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Neon Flappy - Synthwave Edition")
    clock = pygame.time.Clock()

    # Load Typography
    pygame.font.init()
    try:
        font_large = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 38, bold=True)
        font_medium = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 22, bold=True)
        font_small = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 14, bold=True)
    except Exception:
        font_large = pygame.font.Font(None, 44)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 18)

    # Initialize Assets & Layers
    high_score = load_high_score()
    game_state = STATE_START

    bird = Bird()
    pipes = []
    particles = []

    # Parallax Speeds relative to full horizontal speed (3.5 px/frame)
    city_far = CityscapeLayer(layer_id=1, color=CITY_COLOR_1, speed=0.5, width=60)
    city_near = CityscapeLayer(layer_id=2, color=CITY_COLOR_2, speed=1.2, width=75)
    ground = Ground(speed=3.5)

    score = 0
    spawn_timer = 0
    running = True

    while running:
        # Limit framerate to 60 FPS and lock frame speed increments
        dt = clock.tick(FPS)
        # Convert dt to a pixel delta factor (assuming 60 FPS base)
        delta_factor = dt / (1000.0 / 60.0)

        # ---------------------
        # EVENT ROUTING
        # ---------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if game_state == STATE_START:
                        game_state = STATE_PLAYING
                        bird.jump(particles)
                    elif game_state == STATE_PLAYING:
                        bird.jump(particles)

                if event.key == pygame.K_r:
                    if game_state == STATE_GAMEOVER:
                        # Reset game elements
                        bird = Bird()
                        pipes = []
                        particles = []
                        score = 0
                        spawn_timer = 0
                        game_state = STATE_PLAYING
                        bird.jump(particles)

        # ---------------------
        # PHYSICS & SCROLL UPDATES
        # ---------------------
        if game_state == STATE_PLAYING:
            # 1. Update Parallax Backgrounds
            city_far.update(delta_factor)
            city_near.update(delta_factor)
            ground.update(delta_factor)

            # 2. Update Bird Physics
            bird.update(particles)

            # 3. Spawning & Updating Obstacles
            spawn_timer += 1 * delta_factor
            if len(pipes) == 0 or spawn_timer > 95:  # Spawn interval in frames
                pipes.append(Pipe(SCREEN_WIDTH + 50, score))
                spawn_timer = 0

            for pipe in pipes[:]:
                pipe.update(3.5 * delta_factor)
                # Check scoring triggers
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                    # Float score particles
                    for _ in range(6):
                        particles.append(Particle(bird.x, bird.y, burst=True))

                # Delete off-screen pipes
                if pipe.x + pipe.width < -50:
                    pipes.remove(pipe)

            # 4. Check Collisions
            if check_collision(bird, pipes, ground.y):
                game_state = STATE_GAMEOVER
                # Trigger beautiful crash explosion of glowing particles
                for _ in range(30):
                    particles.append(Particle(bird.x, bird.y, burst=True))
                # Persistent high score updates
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

        elif game_state == STATE_GAMEOVER:
            # Bird falls to ground on collision
            if bird.y + bird.radius < ground.y:
                bird.velocity += bird.gravity
                bird.y += bird.velocity

        # 5. Update Particle Trail Fadeouts
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # ---------------------
        # RENDERING COMPONENT
        # ---------------------
        # A. Sunset Twilight Horizon
        draw_sky_gradient(screen)

        # B. Parallax Layers
        city_far.draw(screen, ground.y)
        city_near.draw(screen, ground.y)

        # C. Pipes
        for pipe in pipes:
            pipe.draw(screen)

        # D. Ground Perspective
        ground.draw(screen)

        # E. Particle Trail
        for p in particles:
            p.draw(screen)

        # F. Active Bird
        bird.draw(screen)

        # ---------------------
        # HUD overlays & State Panels
        # ---------------------
        if game_state == STATE_START:
            # Semi-transparent backdrop overlay
            backdrop = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            backdrop.set_alpha(140)
            backdrop.fill(BACKGROUND_COLOR_TOP)
            screen.blit(backdrop, (0, 0))

            draw_text_centered(screen, font_large, "NEON FLAPPY", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, PIPE_COLOR)
            draw_text_centered(screen, font_medium, "PRESS SPACE TO FLAP", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, TEXT_PRIMARY)
            draw_text_centered(screen, font_small, "NAVIGATE THE GLOWING Neon TUBES", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, TEXT_MUTED)
            draw_text_centered(screen, font_small, f"HIGH SCORE: {high_score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, GOLD)

        elif game_state == STATE_PLAYING:
            # Minimal score HUD displaying centered floating points
            score_surf = font_large.render(str(score), True, TEXT_PRIMARY)
            screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 40))

        elif game_state == STATE_GAMEOVER:
            # Glassmorphic Semi-transparent game over screen
            backdrop = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            backdrop.set_alpha(180)
            backdrop.fill((12, 10, 22))
            screen.blit(backdrop, (0, 0))

            draw_text_centered(screen, font_large, "CRASHED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120, TEXT_ACCENT)

            # Score Summary Card
            card_w = 260
            card_h = 160
            card_x = SCREEN_WIDTH // 2 - card_w // 2
            card_y = SCREEN_HEIGHT // 2 - 60
            pygame.draw.rect(screen, (24, 20, 38), (card_x, card_y, card_w, card_h))
            pygame.draw.rect(screen, GROUND_GRID_COLOR, (card_x, card_y, card_w, card_h), 2)

            # Details inside card
            lbl_score = font_small.render("FINAL SCORE", True, TEXT_MUTED)
            val_score = font_large.render(str(score), True, TEXT_PRIMARY)
            screen.blit(lbl_score, (card_x + 30, card_y + 20))
            screen.blit(val_score, (card_x + 30, card_y + 40))

            lbl_high = font_small.render("HIGH SCORE", True, TEXT_MUTED)
            val_high = font_large.render(str(high_score), True, GOLD)
            screen.blit(lbl_high, (card_x + 30, card_y + 90))
            screen.blit(val_high, (card_x + 30, card_y + 110))

            draw_text_centered(screen, font_medium, "PRESS 'R' TO FLAP AGAIN", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, TEXT_PRIMARY)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
