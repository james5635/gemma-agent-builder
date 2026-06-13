import pygame
import random

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1

    def update(self, speed, move_down=False):
        if move_down:
            self.rect.y += 10
            self.direction *= -1

        self.rect.x += speed * self.direction


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


def main():
    pygame.init()
    # Use dummy driver for headless environments to avoid errors during testing
    import os

    if "DISPLAY" not in os.environ:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    # Create enemy grid
    for row in range(5):
        for col in range(10):
            enemy = Enemy(100 + col * 60, 50 + row * 50)
            all_sprites.add(enemy)
            enemies.add(enemy)

    score = 0
    enemy_speed = 2
    running = True

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = player.shoot()
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        # 2. Update Logic
        player.update()

        # Check if enemies hit the edge
        move_down = False
        for enemy in enemies:
            if enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
                move_down = True
                break

        if move_down:
            for enemy in enemies:
                enemy.update(0, move_down=True)
        else:
            for enemy in enemies:
                enemy.update(enemy_speed)

        # Bullet collision with enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        if hits:
            score += len(hits)

        # Enemy collision with player
        if pygame.sprite.spritecollide(player, enemies, False):
            running = False  # Game Over

        # 3. Rendering
        screen.fill(BLACK)
        all_sprites.draw(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
