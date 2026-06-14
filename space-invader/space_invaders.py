import pygame
import random
import os
import requests
import io

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREY = (100, 100, 100)

# Asset URLs
ASSETS_URLS = {
    "player": "https://raw.githubusercontent.com/damnlinh/spacegamePy/master/spaceship.png",
    "alien1": "https://raw.githubusercontent.com/damnlinh/spacegamePy/master/alien1.png",
    "alien2": "https://raw.githubusercontent.com/damnlinh/spacegamePy/master/alien2.png",
    "alien3": "https://raw.githubusercontent.com/damnlinh/spacegamePy/master/alien3.png",
    "bullet": "https://raw.githubusercontent.com/damnlinh/spacegamePy/master/bullet.png",
}

def ensure_assets():
    """Ensures assets exist by downloading them."""
    os.makedirs("assets", exist_ok=True)
    for name, url in ASSETS_URLS.items():
        path = f"assets/{name}.png"
        if not os.path.exists(path):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                with open(path, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Failed to download {name}: {e}")
                # Create a fallback surface
                fallback = pygame.Surface((32, 32))
                pygame.image.save(fallback, path)

def load_player_img():
    img = pygame.image.load("assets/player.png").convert_alpha()
    return pygame.transform.scale(img, (50, 40))

def load_enemy_img(type_idx):
    filename = f"assets/alien{ (type_idx % 3) + 1 }.png"
    img = pygame.image.load(filename).convert_alpha()
    return pygame.transform.scale(img, (40, 30))

def load_bullet_img():
    img = pygame.image.load("assets/bullet.png").convert_alpha()
    return pygame.transform.scale(img, (5, 15))

class Player(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
        self.speed = 6
        self.lives = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self, bullet_img):
        return Bullet(self.rect.centerx, self.rect.top, bullet_img, -1)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, direction):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 8 * direction

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a pixelated bunker look
        self.image = pygame.Surface((60, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GREY, (0, 0, 60, 20))
        # Add some "holes" to the bunker
        pygame.draw.rect(self.image, BLACK, (10, 5, 10, 10))
        pygame.draw.rect(self.image, BLACK, (25, 5, 10, 10))
        pygame.draw.rect(self.image, BLACK, (40, 5, 10, 10))
        self.rect = self.image.get_rect(topleft=(x, y))

def main():
    pygame.init()

    import os
    if "DISPLAY" not in os.environ:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders Retro")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier", 24, bold=True)
    big_font = pygame.font.SysFont("Courier", 64, bold=True)

    ensure_assets()
    player_img = load_player_img()
    bullet_img = load_bullet_img()

    # Pre-load 3 types of enemies
    enemy_imgs = [load_enemy_img(0), load_enemy_img(1), load_enemy_img(2)]

    state = "MENU"
    score = 0

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    barriers = pygame.sprite.Group()
    player = None
    enemy_direction = 1
    enemy_speed = 2

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if state == "MENU":
                if event.type == pygame.KEYDOWN:
                    state = "PLAYING"
                    all_sprites.empty()
                    enemies.empty()
                    player_bullets.empty()
                    enemy_bullets.empty()
                    barriers.empty()

                    player = Player(player_img)
                    all_sprites.add(player)

                    for row in range(5):
                        for col in range(10):
                            # Assign alien type based on row
                            img = enemy_imgs[row // 2]
                            enemy = Enemy(100 + col * 60, 50 + row * 50, img)
                            all_sprites.add(enemy)
                            enemies.add(enemy)

                    for b_col in range(4):
                        for b_row in range(2):
                            barrier = Barrier(100 + b_col * 150, 450 + b_row * 30)
                            all_sprites.add(barrier)
                            barriers.add(barrier)

                    score = 0
                    enemy_direction = 1
                    enemy_speed = 2
                    player.lives = 3

            elif state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player:
                        bullet = player.shoot(bullet_img)
                        all_sprites.add(bullet)
                        player_bullets.add(bullet)

            elif state in ("GAMEOVER", "WIN"):
                if event.type == pygame.KEYDOWN:
                    state = "MENU"

        if state == "PLAYING" and player:
            player.update()

            move_down = False
            for enemy in enemies:
                if enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
                    move_down = True
                    break

            if move_down:
                enemy_direction *= -1
                enemy_speed += 0.1
                for enemy in enemies:
                    enemy.update(enemy_speed * enemy_direction, 10)
            else:
                for enemy in enemies:
                    enemy.update(enemy_speed * enemy_direction, 0)

            if random.random() < 0.015 and enemies:
                shooter = random.choice(enemies.sprites())
                ebullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, bullet_img, 1)
                all_sprites.add(ebullet)
                enemy_bullets.add(ebullet)

            hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
            score += len(hits) * 10

            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                player.lives -= 1
                if player.lives <= 0:
                    state = "GAMEOVER"

            pygame.sprite.groupcollide(barriers, enemy_bullets, True, True)
            pygame.sprite.groupcollide(barriers, player_bullets, True, True)
            pygame.sprite.groupcollide(barriers, enemies, True, False)

            if pygame.sprite.spritecollide(player, enemies, False) or any(e.rect.bottom >= HEIGHT for e in enemies):
                state = "GAMEOVER"

            if not enemies:
                state = "WIN"

            player_bullets.update()
            enemy_bullets.update()

        screen.fill(BLACK)

        if state == "MENU":
            title = big_font.render("SPACE INVADERS", True, GREEN)
            start = font.render("Press any key to Start", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2 + 20))

        elif state == "PLAYING":
            all_sprites.draw(screen)
            score_text = font.render(f"Score: {score}  Lives: {player.lives if player else 0}", True, WHITE)
            screen.blit(score_text, (10, 10))

        elif state == "GAMEOVER":
            msg = big_font.render("GAME OVER", True, RED)
            restart = font.render("Press any key to return to Menu", True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 20))

        elif state == "WIN":
            msg = big_font.render("YOU WIN!", True, GREEN)
            restart = font.render("Press any key to return to Menu", True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
