import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Window Setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# DDA Raycasting Constants
CELL_SIZE = 64
FOV = math.pi / 3  # 60 degrees
HALF_FOV = FOV / 2
NUM_RAYS = 200
STRIP_WIDTH = SCREEN_WIDTH // NUM_RAYS

# Neon Synthwave Colors
BACKGROUND_COLOR = (10, 8, 22)
SKY_COLOR_TOP = (15, 10, 30)
SKY_COLOR_BOT = (35, 12, 50)
FLOOR_COLOR = (12, 10, 20)
GRID_LINE_COLOR = (54, 36, 97)
TEXT_PRIMARY = (255, 255, 255)
TEXT_MUTED = (140, 120, 170)
CYAN = (0, 229, 255)
MAGENTA = (255, 46, 99)
GOLD = (255, 215, 0)
RED = (255, 40, 40)
GREEN = (60, 255, 120)
ORANGE = (255, 160, 40)

# 2D Map Grid (12x12)
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

MAP_WIDTH = len(MAP[0])
MAP_HEIGHT = len(MAP)


def is_walkable(px, py):
    """Check if world coords are on a walkable tile."""
    gx = int(px // CELL_SIZE)
    gy = int(py // CELL_SIZE)
    if 0 <= gx < MAP_WIDTH and 0 <= gy < MAP_HEIGHT:
        return MAP[gy][gx] == 0
    return False


def line_of_sight(x1, y1, x2, y2):
    """Check if there is clear line of sight between two world points."""
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1:
        return True
    steps = int(dist / 8)
    if steps == 0:
        return True
    for i in range(steps + 1):
        t = i / steps
        cx = x1 + dx * t
        cy = y1 + dy * t
        gx = int(cx // CELL_SIZE)
        gy = int(cy // CELL_SIZE)
        if 0 <= gx < MAP_WIDTH and 0 <= gy < MAP_HEIGHT:
            if MAP[gy][gx] == 1:
                return False
        else:
            return False
    return True


class Particle:
    """Visual particle for effects."""
    def __init__(self, x, y, dx=None, dy=None, color=CYAN, size=None):
        self.x = x
        self.y = y
        self.dx = dx if dx is not None else random.uniform(-4, 4)
        self.dy = dy if dy is not None else random.uniform(-4, 4)
        self.color = color
        self.size = size if size is not None else random.uniform(3, 7)
        self.life = 1.0
        self.decay = random.uniform(0.04, 0.08)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= self.decay
        self.size = max(0, self.size - 0.15)

    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


class Player:
    """Player state and movement."""
    def __init__(self):
        self.x = 1.5 * CELL_SIZE
        self.y = 1.5 * CELL_SIZE
        self.angle = 0.0
        self.speed = 3.5
        self.rot_speed = 0.05
        self.radius = 12
        self.health = 100
        self.max_health = 100
        self.damage_flash = 0  # screen flash when hit

    def move(self, dx, dy):
        """Wall-sliding collision."""
        nx = self.x + dx
        if is_walkable(nx, self.y):
            self.x = nx
        ny = self.y + dy
        if is_walkable(self.x, ny):
            self.y = ny

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        self.damage_flash = 15  # frames of red flash


class Enemy:
    """AI enemy that patrols, chases, and shoots at the player."""

    # Possible spawn positions (grid coords) — open corridor cells
    SPAWN_CELLS = [
        (4, 1), (7, 3), (9, 5), (5, 8), (10, 10),
        (1, 10), (3, 3), (8, 1), (10, 3), (1, 5),
        (3, 8), (8, 10), (5, 5), (5, 6)
    ]

    def __init__(self, grid_x, grid_y):
        self.x = (grid_x + 0.5) * CELL_SIZE
        self.y = (grid_y + 0.5) * CELL_SIZE
        self.alive = True
        self.health = 40
        self.max_health = 40
        self.speed = 1.8
        self.distance = 0.0  # distance to player (updated each frame)
        self.float_tick = random.randint(0, 100)

        # AI state
        self.state = "patrol"  # patrol, chase, attack
        self.patrol_angle = random.uniform(0, 2 * math.pi)
        self.patrol_timer = random.randint(60, 180)
        self.chase_range = 350.0  # distance to start chasing
        self.attack_range = 250.0  # distance to start shooting
        self.shoot_cooldown = 0
        self.shoot_interval = 80  # frames between shots
        self.damage = 8  # damage per shot
        self.hit_flash = 0  # visual flash when hit
        self.death_timer = 0  # counts up after death for respawn
        self.angle_to_player = 0.0

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 10
        if self.health <= 0:
            self.alive = False
            self.death_timer = 0

    def update(self, player, dt=1):
        if not self.alive:
            self.death_timer += 1
            return

        self.float_tick += 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Calculate distance and angle to player
        dx = player.x - self.x
        dy = player.y - self.y
        self.distance = math.sqrt(dx * dx + dy * dy)
        self.angle_to_player = math.atan2(dy, dx)

        # Check line of sight
        can_see_player = False
        if self.distance < self.chase_range * 1.5:
            can_see_player = line_of_sight(self.x, self.y, player.x, player.y)

        # State machine
        if can_see_player and self.distance < self.attack_range:
            self.state = "attack"
        elif can_see_player and self.distance < self.chase_range:
            self.state = "chase"
        else:
            self.state = "patrol"

        # Execute behavior
        if self.state == "patrol":
            self._patrol()
        elif self.state == "chase":
            self._chase(player)
        elif self.state == "attack":
            self._attack(player)

    def _patrol(self):
        """Wander around corridors randomly."""
        self.patrol_timer -= 1
        if self.patrol_timer <= 0:
            self.patrol_angle = random.uniform(0, 2 * math.pi)
            self.patrol_timer = random.randint(60, 180)

        move_x = math.cos(self.patrol_angle) * self.speed * 0.5
        move_y = math.sin(self.patrol_angle) * self.speed * 0.5

        nx = self.x + move_x
        ny = self.y + move_y
        if is_walkable(nx, ny):
            self.x = nx
            self.y = ny
        else:
            # Bounce off wall, pick new direction
            self.patrol_angle = random.uniform(0, 2 * math.pi)
            self.patrol_timer = random.randint(30, 90)

    def _chase(self, player):
        """Move towards the player."""
        angle = self.angle_to_player
        move_x = math.cos(angle) * self.speed
        move_y = math.sin(angle) * self.speed

        nx = self.x + move_x
        ny = self.y + move_y
        if is_walkable(nx, ny):
            self.x = nx
            self.y = ny
        else:
            # Try sliding along walls
            if is_walkable(nx, self.y):
                self.x = nx
            elif is_walkable(self.x, ny):
                self.y = ny

    def _attack(self, player):
        """Face the player and shoot periodically."""
        # Slowly approach if far
        if self.distance > 120:
            angle = self.angle_to_player
            move_x = math.cos(angle) * self.speed * 0.4
            move_y = math.sin(angle) * self.speed * 0.4
            nx = self.x + move_x
            ny = self.y + move_y
            if is_walkable(nx, ny):
                self.x = nx
                self.y = ny

        # Shoot at player
        if self.shoot_cooldown <= 0:
            if line_of_sight(self.x, self.y, player.x, player.y):
                player.take_damage(self.damage)
                self.shoot_cooldown = self.shoot_interval
                return True  # signal: shot fired
        return False


def draw_retro_sky(screen):
    """Gradient twilight sky."""
    for y in range(SCREEN_HEIGHT // 2):
        ratio = y / (SCREEN_HEIGHT // 2)
        color = tuple(
            int(SKY_COLOR_TOP[c] * (1.0 - ratio) + SKY_COLOR_BOT[c] * ratio)
            for c in range(3)
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))


def draw_perspective_floor(screen):
    """Synthwave perspective floor grid."""
    pygame.draw.rect(screen, FLOOR_COLOR, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    for i in range(1, 16):
        line_y = SCREEN_HEIGHT // 2 + (SCREEN_HEIGHT // 2) * (i / 16) ** 2
        shading = (i / 16) ** 1.5
        color = tuple(int(GRID_LINE_COLOR[c] * shading) for c in range(3))
        pygame.draw.line(screen, color, (0, line_y), (SCREEN_WIDTH, line_y), 1)


def draw_text_centered(screen, font, text, center_x, y, color):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(center_x, y))
    screen.blit(surf, rect)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("CYBERPUNK FPS — Synthwave Raycaster")
    clock = pygame.time.Clock()

    pygame.font.init()
    try:
        font_large = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 36, bold=True)
        font_medium = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 20, bold=True)
        font_small = pygame.font.SysFont(["Segoe UI", "Calibri", "Arial"], 14, bold=True)
    except Exception:
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)

    player = Player()

    # Spawn enemies at various corridor positions
    enemies = []
    enemy_spawn_positions = [(4, 1), (9, 5), (5, 8), (10, 10), (1, 10), (3, 3)]
    for gx, gy in enemy_spawn_positions:
        enemies.append(Enemy(gx, gy))

    particles = []
    kills = 0
    wave = 1

    # Mouse grab state
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    mouse_grabbed = True
    mouse_sensitivity = 0.003

    # Weapon state
    ammo = 24
    max_ammo = 24
    shoot_cooldown = 0
    recoil = 0.0
    bobbing_tick = 0
    is_shooting = False

    # Depth buffer
    ray_depths = [9999.0] * NUM_RAYS

    # Game over state
    game_over = False
    game_over_timer = 0

    running = True

    while running:
        dt = clock.tick(FPS) / 16.67  # normalize to ~60fps
        bobbing_tick += 1

        # ---- MOUSE LOOK ----
        if mouse_grabbed and not game_over:
            mx, my = pygame.mouse.get_rel()
            mx = max(-80, min(80, mx))
            player.angle += mx * mouse_sensitivity

        # Cooldowns
        if shoot_cooldown > 0:
            shoot_cooldown -= 1
        if recoil > 0:
            recoil -= 0.1
        else:
            recoil = 0.0
        is_shooting = shoot_cooldown > 15
        if player.damage_flash > 0:
            player.damage_flash -= 1

        # ---- EVENT LOOP ----
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        trigger_shoot = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # Restart game
                        player.health = player.max_health
                        player.x = 1.5 * CELL_SIZE
                        player.y = 1.5 * CELL_SIZE
                        player.angle = 0
                        kills = 0
                        wave = 1
                        ammo = max_ammo
                        game_over = False
                        game_over_timer = 0
                        enemies.clear()
                        for gx, gy in enemy_spawn_positions:
                            enemies.append(Enemy(gx, gy))
                        particles.clear()
                        continue
                    else:
                        trigger_shoot = True
                if event.key == pygame.K_ESCAPE:
                    mouse_grabbed = not mouse_grabbed
                    pygame.mouse.set_visible(not mouse_grabbed)
                    pygame.event.set_grab(mouse_grabbed)
                    if mouse_grabbed:
                        pygame.mouse.get_rel()  # flush
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if mouse_grabbed:
                        trigger_shoot = True
                    else:
                        mouse_grabbed = True
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()  # flush

        if game_over:
            game_over_timer += 1
            # Render game over screen
            screen.fill(BACKGROUND_COLOR)
            draw_retro_sky(screen)
            draw_perspective_floor(screen)

            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((20, 0, 0))
            screen.blit(overlay, (0, 0))

            draw_text_centered(screen, font_large, "YOU DIED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, RED)
            draw_text_centered(screen, font_medium, f"Enemies Eliminated: {kills}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, GOLD)
            draw_text_centered(screen, font_medium, f"Wave Reached: {wave}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, CYAN)
            if game_over_timer > 60:
                draw_text_centered(screen, font_medium, "Press SPACE to restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90, TEXT_PRIMARY)

            pygame.display.flip()
            continue

        # ---- MOVEMENT ----
        if keys[pygame.K_w]:
            move_x += math.cos(player.angle) * player.speed
            move_y += math.sin(player.angle) * player.speed
        if keys[pygame.K_s]:
            move_x -= math.cos(player.angle) * player.speed
            move_y -= math.sin(player.angle) * player.speed
        if keys[pygame.K_a]:
            # Strafe left
            move_x += math.sin(player.angle) * player.speed
            move_y -= math.cos(player.angle) * player.speed
        if keys[pygame.K_d]:
            # Strafe right
            move_x -= math.sin(player.angle) * player.speed
            move_y += math.cos(player.angle) * player.speed

        player.angle %= (2 * math.pi)
        if move_x != 0 or move_y != 0:
            player.move(move_x, move_y)

        # ---- SHOOTING ----
        if trigger_shoot and shoot_cooldown == 0 and ammo > 0:
            ammo -= 1
            shoot_cooldown = 20
            recoil = 1.0

            # Muzzle flash particles
            gun_tip_x = SCREEN_WIDTH // 2
            gun_tip_y = SCREEN_HEIGHT - 120
            for _ in range(8):
                particles.append(Particle(
                    gun_tip_x + random.uniform(-10, 10),
                    gun_tip_y + random.uniform(-10, 10),
                    dx=random.uniform(-3, 3),
                    dy=random.uniform(-4, -1),
                    color=CYAN
                ))

            # Hit detection — find closest enemy in crosshair
            closest_enemy = None
            closest_dist = 99999.0

            for e in enemies:
                if not e.alive:
                    continue
                dx = e.x - player.x
                dy = e.y - player.y
                dist = math.sqrt(dx * dx + dy * dy)

                theta = math.atan2(dy, dx)
                angle_diff = theta - player.angle
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi

                # Hitbox tolerance scales with distance (easier to hit closer enemies)
                tolerance = max(0.05, 0.12 - dist * 0.0001)
                if abs(angle_diff) < tolerance and dist < closest_dist:
                    if line_of_sight(player.x, player.y, e.x, e.y):
                        closest_enemy = e
                        closest_dist = dist

            if closest_enemy:
                closest_enemy.take_damage(25)

                # Hit spark particles at enemy screen position
                dx = closest_enemy.x - player.x
                dy = closest_enemy.y - player.y
                theta = math.atan2(dy, dx)
                angle_diff = theta - player.angle
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi

                proj_x = SCREEN_WIDTH / 2 + math.tan(angle_diff) * (SCREEN_WIDTH / 2)
                proj_y = SCREEN_HEIGHT / 2
                spark_color = RED if closest_enemy.alive else MAGENTA
                for _ in range(15 if not closest_enemy.alive else 30):
                    particles.append(Particle(proj_x, proj_y, color=spark_color,
                                              size=random.uniform(3, 8)))

                if not closest_enemy.alive:
                    kills += 1

        # Reload
        if keys[pygame.K_r] and ammo < max_ammo:
            ammo = max_ammo
            for _ in range(12):
                particles.append(Particle(
                    SCREEN_WIDTH // 2 + random.uniform(-30, 30),
                    SCREEN_HEIGHT - 60 + random.uniform(-10, 10),
                    dx=random.uniform(-1, 1), dy=random.uniform(-3, -1), color=GOLD
                ))

        # ---- UPDATE ENEMIES ----
        enemy_shot_fired = False
        for e in enemies:
            result = e.update(player)
            if result:
                enemy_shot_fired = True
                # Visual: enemy laser tracer particles toward screen center
                dx = e.x - player.x
                dy = e.y - player.y
                theta = math.atan2(dy, dx)
                angle_diff = theta - player.angle
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                if abs(angle_diff) < HALF_FOV + 0.3:
                    proj_x = SCREEN_WIDTH / 2 + math.tan(angle_diff) * (SCREEN_WIDTH / 2)
                    proj_x = max(0, min(SCREEN_WIDTH, proj_x))
                    for _ in range(5):
                        particles.append(Particle(
                            proj_x + random.uniform(-20, 20),
                            SCREEN_HEIGHT // 2 + random.uniform(-30, 30),
                            dx=random.uniform(-1, 1) * (SCREEN_WIDTH // 2 - proj_x) * 0.02,
                            dy=random.uniform(-1, 1),
                            color=ORANGE, size=random.uniform(2, 5)
                        ))

        # Check player death
        if player.health <= 0:
            game_over = True
            continue

        # Respawn wave: if all enemies dead, spawn new wave
        if all(not e.alive for e in enemies):
            wave += 1
            enemies.clear()
            # Each wave adds more enemies from shuffled positions
            available = list(Enemy.SPAWN_CELLS)
            random.shuffle(available)
            num_enemies = min(len(available), 4 + wave * 2)
            for i in range(num_enemies):
                gx, gy = available[i]
                new_e = Enemy(gx, gy)
                new_e.speed = min(3.0, 1.8 + wave * 0.15)
                new_e.shoot_interval = max(40, 80 - wave * 5)
                new_e.health = min(80, 40 + wave * 5)
                new_e.max_health = new_e.health
                enemies.append(new_e)
            # Bonus: restore some health per wave
            player.health = min(player.max_health, player.health + 20)
            ammo = max_ammo

        # ---- 3D RENDERING ----
        screen.fill(BACKGROUND_COLOR)
        draw_retro_sky(screen)
        draw_perspective_floor(screen)

        # A. RAYCASTING
        start_angle = player.angle - HALF_FOV
        for r_idx in range(NUM_RAYS):
            ray_angle = start_angle + (r_idx / NUM_RAYS) * FOV
            ray_cos = math.cos(ray_angle)
            ray_sin = math.sin(ray_angle)

            map_x = int(player.x // CELL_SIZE)
            map_y = int(player.y // CELL_SIZE)

            delta_dist_x = abs(1 / ray_cos) if ray_cos != 0 else 1e30
            delta_dist_y = abs(1 / ray_sin) if ray_sin != 0 else 1e30

            if ray_cos < 0:
                step_x = -1
                side_dist_x = (player.x - map_x * CELL_SIZE) * delta_dist_x / CELL_SIZE
            else:
                step_x = 1
                side_dist_x = ((map_x + 1) * CELL_SIZE - player.x) * delta_dist_x / CELL_SIZE

            if ray_sin < 0:
                step_y = -1
                side_dist_y = (player.y - map_y * CELL_SIZE) * delta_dist_y / CELL_SIZE
            else:
                step_y = 1
                side_dist_y = ((map_y + 1) * CELL_SIZE - player.y) * delta_dist_y / CELL_SIZE

            hit = 0
            side = 0
            depth = 0
            while hit == 0 and depth < 20:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1
                depth += 1
                if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                    break
                if MAP[map_y][map_x] == 1:
                    hit = 1

            if side == 0:
                perp_dist = (side_dist_x - delta_dist_x) * CELL_SIZE
            else:
                perp_dist = (side_dist_y - delta_dist_y) * CELL_SIZE

            perp_dist = max(0.1, perp_dist)
            ray_depths[r_idx] = perp_dist

            wall_h = (CELL_SIZE * SCREEN_HEIGHT) / perp_dist
            wall_h = min(2000, wall_h)
            draw_start = -wall_h / 2 + SCREEN_HEIGHT / 2
            draw_end = wall_h / 2 + SCREEN_HEIGHT / 2

            max_fade = 650.0
            shading = max(0.0, min(1.0, 1.0 - (perp_dist / max_fade)))

            if side == 0:
                color = tuple(int(CYAN[c] * shading) for c in range(3))
            else:
                color = tuple(int(MAGENTA[c] * 0.7 * shading) for c in range(3))

            pygame.draw.rect(screen, color, (r_idx * STRIP_WIDTH, int(draw_start), STRIP_WIDTH, int(wall_h)))

        # B. SPRITE RENDERING (enemies)
        # Gather all renderable sprites
        render_list = []
        for e in enemies:
            if not e.alive:
                continue
            dx = e.x - player.x
            dy = e.y - player.y
            e.distance = math.sqrt(dx * dx + dy * dy)
            if e.distance < 12:
                continue
            render_list.append(e)

        # Sort by distance descending (painter's algorithm)
        render_list.sort(key=lambda s: s.distance, reverse=True)

        for e in render_list:
            dx = e.x - player.x
            dy = e.y - player.y
            theta = math.atan2(dy, dx)
            angle_diff = theta - player.angle
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi

            if abs(angle_diff) < HALF_FOV + 0.2:
                proj_x = SCREEN_WIDTH / 2 + math.tan(angle_diff) * (SCREEN_WIDTH / 2)
                float_offset = math.sin(e.float_tick * 0.06) * 8
                proj_y = SCREEN_HEIGHT / 2 + float_offset

                sprite_size = int((CELL_SIZE * SCREEN_HEIGHT) / e.distance)
                sprite_size = max(4, min(400, sprite_size))

                ray_idx = int((proj_x / SCREEN_WIDTH) * NUM_RAYS)
                if 0 <= ray_idx < NUM_RAYS:
                    perp_enemy_dist = e.distance * math.cos(angle_diff)
                    if ray_depths[ray_idx] > perp_enemy_dist:
                        # Draw the enemy sprite
                        _draw_enemy_sprite(screen, e, int(proj_x), int(proj_y), sprite_size)

        # C. PARTICLES
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        # D. DAMAGE FLASH OVERLAY
        if player.damage_flash > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill((255, 0, 0))
            flash_surf.set_alpha(int(60 * (player.damage_flash / 15)))
            screen.blit(flash_surf, (0, 0))

        # ---- HUD ----
        # Gun
        gun_x = SCREEN_WIDTH // 2
        gun_y = SCREEN_HEIGHT
        is_moving = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        bob_x = math.sin(bobbing_tick * 0.18) * 8 if is_moving else 0.0
        bob_y = abs(math.cos(bobbing_tick * 0.18)) * 6 if is_moving else 0.0
        gun_draw_x = int(gun_x + bob_x)
        gun_draw_y = int(gun_y + bob_y + (recoil * 25))

        chassis_points = [
            (gun_draw_x - 30, gun_draw_y),
            (gun_draw_x - 18, gun_draw_y - 120),
            (gun_draw_x + 18, gun_draw_y - 120),
            (gun_draw_x + 30, gun_draw_y)
        ]
        pygame.draw.polygon(screen, (22, 18, 38), chassis_points)
        pygame.draw.polygon(screen, GRID_LINE_COLOR, chassis_points, 2)

        barrel_pts = [
            (gun_draw_x - 8, gun_draw_y - 80),
            (gun_draw_x - 5, gun_draw_y - 130),
            (gun_draw_x + 5, gun_draw_y - 130),
            (gun_draw_x + 8, gun_draw_y - 80)
        ]
        pygame.draw.polygon(screen, CYAN, barrel_pts)

        pygame.draw.line(screen, GOLD, (gun_draw_x - 18, gun_draw_y - 60), (gun_draw_x - 12, gun_draw_y - 110), 2)
        pygame.draw.line(screen, GOLD, (gun_draw_x + 18, gun_draw_y - 60), (gun_draw_x + 12, gun_draw_y - 110), 2)

        if is_shooting:
            pygame.draw.circle(screen, TEXT_PRIMARY, (gun_draw_x, gun_draw_y - 135), 24)
            pygame.draw.circle(screen, CYAN, (gun_draw_x, gun_draw_y - 135), 16)
            pygame.draw.circle(screen, TEXT_PRIMARY, (gun_draw_x, gun_draw_y - 135), 8)

        # Crosshair
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.circle(screen, CYAN, (cx, cy), 4)
        pygame.draw.line(screen, CYAN, (cx - 12, cy), (cx - 6, cy), 2)
        pygame.draw.line(screen, CYAN, (cx + 6, cy), (cx + 12, cy), 2)
        pygame.draw.line(screen, CYAN, (cx, cy - 12), (cx, cy - 6), 2)
        pygame.draw.line(screen, CYAN, (cx, cy + 6), (cx, cy + 12), 2)

        # Minimap
        map_size = 110
        map_ox = 20
        map_oy = 20
        map_card = pygame.Surface((map_size + 15, map_size + 15))
        map_card.set_alpha(160)
        map_card.fill((12, 10, 24))
        screen.blit(map_card, (map_ox - 8, map_oy - 8))
        pygame.draw.rect(screen, GRID_LINE_COLOR, (map_ox - 8, map_oy - 8, map_size + 15, map_size + 15), 2)

        mini_cell = map_size // MAP_WIDTH
        for my in range(MAP_HEIGHT):
            for mx in range(MAP_WIDTH):
                if MAP[my][mx] == 1:
                    pygame.draw.rect(screen, GRID_LINE_COLOR,
                                     (map_ox + mx * mini_cell, map_oy + my * mini_cell, mini_cell, mini_cell))

        # Enemies on minimap
        for e in enemies:
            if e.alive:
                emx = int((e.x / (MAP_WIDTH * CELL_SIZE)) * map_size)
                emy = int((e.y / (MAP_HEIGHT * CELL_SIZE)) * map_size)
                color = RED if e.state == "attack" else (ORANGE if e.state == "chase" else MAGENTA)
                pygame.draw.circle(screen, color, (map_ox + emx, map_oy + emy), 3)

        # Player on minimap
        pmx = int((player.x / (MAP_WIDTH * CELL_SIZE)) * map_size)
        pmy = int((player.y / (MAP_HEIGHT * CELL_SIZE)) * map_size)
        pygame.draw.circle(screen, CYAN, (map_ox + pmx, map_oy + pmy), 4)
        cone_pts = [
            (map_ox + pmx, map_oy + pmy),
            (map_ox + pmx + int(12 * math.cos(player.angle - HALF_FOV)),
             map_oy + pmy + int(12 * math.sin(player.angle - HALF_FOV))),
            (map_ox + pmx + int(12 * math.cos(player.angle + HALF_FOV)),
             map_oy + pmy + int(12 * math.sin(player.angle + HALF_FOV)))
        ]
        pygame.draw.polygon(screen, CYAN, cone_pts, 1)

        # Health bar (bottom left)
        hbar_x = 20
        hbar_y = SCREEN_HEIGHT - 40
        hbar_w = 160
        hbar_h = 20
        # Background
        pygame.draw.rect(screen, (30, 20, 40), (hbar_x, hbar_y, hbar_w, hbar_h))
        # Fill
        hp_ratio = player.health / player.max_health
        hp_color = GREEN if hp_ratio > 0.5 else (GOLD if hp_ratio > 0.25 else RED)
        pygame.draw.rect(screen, hp_color, (hbar_x, hbar_y, int(hbar_w * hp_ratio), hbar_h))
        pygame.draw.rect(screen, GRID_LINE_COLOR, (hbar_x, hbar_y, hbar_w, hbar_h), 2)
        hp_text = font_small.render(f"HP {player.health}/{player.max_health}", True, TEXT_PRIMARY)
        screen.blit(hp_text, (hbar_x + 6, hbar_y + 3))

        # Ammo counter (bottom right)
        card_ammo_w = 140
        card_ammo_h = 60
        card_ammo_x = SCREEN_WIDTH - card_ammo_w - 20
        card_ammo_y = SCREEN_HEIGHT - card_ammo_h - 20
        ammo_card = pygame.Surface((card_ammo_w, card_ammo_h))
        ammo_card.set_alpha(180)
        ammo_card.fill((12, 10, 24))
        screen.blit(ammo_card, (card_ammo_x, card_ammo_y))
        pygame.draw.rect(screen, GRID_LINE_COLOR, (card_ammo_x, card_ammo_y, card_ammo_w, card_ammo_h), 2)
        lbl_ammo = font_small.render("PLASMA CELL", True, TEXT_MUTED)
        val_ammo = font_large.render(f"{ammo}/{max_ammo}", True, CYAN)
        screen.blit(lbl_ammo, (card_ammo_x + 12, card_ammo_y + 8))
        screen.blit(val_ammo, (card_ammo_x + 12, card_ammo_y + 20))

        # Kills / Wave (top right)
        card_w = 150
        card_h = 75
        card_x = SCREEN_WIDTH - card_w - 20
        card_y = 20
        score_card = pygame.Surface((card_w, card_h))
        score_card.set_alpha(180)
        score_card.fill((12, 10, 24))
        screen.blit(score_card, (card_x, card_y))
        pygame.draw.rect(screen, GRID_LINE_COLOR, (card_x, card_y, card_w, card_h), 2)
        lbl_kills = font_small.render("KILLS", True, TEXT_MUTED)
        val_kills = font_large.render(str(kills), True, GOLD)
        lbl_wave = font_small.render(f"WAVE {wave}", True, MAGENTA)
        screen.blit(lbl_kills, (card_x + 12, card_y + 8))
        screen.blit(val_kills, (card_x + 12, card_y + 22))
        screen.blit(lbl_wave, (card_x + 12, card_y + 55))

        # Enemy alert indicator
        alert_enemies = [e for e in enemies if e.alive and e.state in ("chase", "attack")]
        if alert_enemies:
            alert_color = RED if any(e.state == "attack" for e in alert_enemies) else ORANGE
            pulse = abs(math.sin(bobbing_tick * 0.1))
            alert_alpha = int(180 + 75 * pulse)
            alert_text = font_small.render(f"⚠ {len(alert_enemies)} HOSTILE{'S' if len(alert_enemies) > 1 else ''} ALERT", True, alert_color)
            screen.blit(alert_text, (SCREEN_WIDTH // 2 - alert_text.get_width() // 2, 10))

        # Controls hint
        draw_text_centered(screen, font_small, "WASD: Move | Mouse: Look | Space/Click: Fire | R: Reload | ESC: Cursor",
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT - 12, TEXT_MUTED)

        # Mouse lock banner
        if not mouse_grabbed:
            banner = pygame.Surface((SCREEN_WIDTH, 35))
            banner.set_alpha(200)
            banner.fill((12, 10, 24))
            screen.blit(banner, (0, 0))
            pygame.draw.line(screen, MAGENTA, (0, 35), (SCREEN_WIDTH, 35), 2)
            draw_text_centered(screen, font_medium,
                               "CLICK INSIDE WINDOW TO ENGAGE MOUSE LOOK (ESC TO FREE CURSOR)",
                               SCREEN_WIDTH // 2, 17, MAGENTA)

        pygame.display.flip()

    pygame.quit()


def _draw_enemy_sprite(screen, enemy, px, py, size):
    """Draw an enemy as a menacing humanoid robot sprite at screen position."""
    s = max(4, size)

    # Body color: changes based on state
    if enemy.hit_flash > 0:
        body_color = TEXT_PRIMARY  # white flash on hit
        accent = TEXT_PRIMARY
    elif enemy.state == "attack":
        body_color = (200, 30, 30)
        accent = RED
    elif enemy.state == "chase":
        body_color = (200, 120, 30)
        accent = ORANGE
    else:
        body_color = (180, 50, 80)
        accent = MAGENTA

    head_r = max(2, s // 8)
    body_h = max(4, s // 3)
    body_w = max(3, s // 5)
    leg_len = max(2, s // 5)

    # Head
    pygame.draw.circle(screen, body_color, (px, py - body_h // 2 - head_r), head_r)

    # Glowing eyes
    eye_r = max(1, head_r // 3)
    eye_spread = max(1, head_r // 2)
    pygame.draw.circle(screen, accent, (px - eye_spread, py - body_h // 2 - head_r), eye_r)
    pygame.draw.circle(screen, accent, (px + eye_spread, py - body_h // 2 - head_r), eye_r)

    # Body (torso rectangle)
    torso_rect = pygame.Rect(px - body_w // 2, py - body_h // 2, body_w, body_h)
    pygame.draw.rect(screen, body_color, torso_rect)
    # Body outline glow
    pygame.draw.rect(screen, accent, torso_rect, 1)

    # Arms
    arm_len = max(2, s // 5)
    # Left arm
    pygame.draw.line(screen, body_color,
                     (px - body_w // 2, py - body_h // 4),
                     (px - body_w // 2 - arm_len, py), max(1, s // 20))
    # Right arm — points toward player if attacking
    if enemy.state == "attack":
        pygame.draw.line(screen, accent,
                         (px + body_w // 2, py - body_h // 4),
                         (px + body_w // 2 + arm_len, py - body_h // 3), max(1, s // 16))
        # Gun in hand
        pygame.draw.circle(screen, ORANGE, (px + body_w // 2 + arm_len, py - body_h // 3), max(1, s // 16))
    else:
        pygame.draw.line(screen, body_color,
                         (px + body_w // 2, py - body_h // 4),
                         (px + body_w // 2 + arm_len, py), max(1, s // 20))

    # Legs
    pygame.draw.line(screen, body_color, (px - body_w // 4, py + body_h // 2),
                     (px - body_w // 3, py + body_h // 2 + leg_len), max(1, s // 20))
    pygame.draw.line(screen, body_color, (px + body_w // 4, py + body_h // 2),
                     (px + body_w // 3, py + body_h // 2 + leg_len), max(1, s // 20))

    # Health bar above head (only if damaged)
    if enemy.health < enemy.max_health:
        bar_w = max(8, s // 3)
        bar_h = max(2, s // 20)
        bar_x = px - bar_w // 2
        bar_y = py - body_h // 2 - head_r * 2 - bar_h - 4
        pygame.draw.rect(screen, (60, 20, 20), (bar_x, bar_y, bar_w, bar_h))
        hp_ratio = enemy.health / enemy.max_health
        pygame.draw.rect(screen, RED, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
        pygame.draw.rect(screen, GRID_LINE_COLOR, (bar_x, bar_y, bar_w, bar_h), 1)


if __name__ == "__main__":
    main()
