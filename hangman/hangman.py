import pygame
import random
import sys

# Monokai Theme Colors
COLOR_BG = (39, 40, 34)       # #272822
COLOR_FG = (248, 248, 242)    # #F8F8F2
COLOR_YELLOW = (230, 219, 116) # #E6DB74
COLOR_MAGENTA = (249, 38, 114) # #F92672
COLOR_CYAN = (102, 217, 239)    # #66D9EF
COLOR_GREEN = (166, 226, 46)    # #A6E22E
COLOR_ORANGE = (253, 151, 31)   # #FD971F

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

def get_word():
    words = ["PYTHON", "CPLUSPLUS", "SFML", "PROGRAMMING", "DEVELOPER", "COMPUTER", "NETWORK", "ALGORITHM", "SENSORS", "SYNTHWAVE"]
    return random.choice(words).upper()

class HangmanGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MONOKAI HANGMAN")
        self.clock = pygame.time.Clock()
        
        try:
            self.font = pygame.font.Font("/usr/share/fonts/libertinus/LibertinusSans-Bold.ttf", 32)
            self.small_font = pygame.font.Font("/usr/share/fonts/libertinus/LibertinusSans-Bold.ttf", 24)
        except:
            self.font = pygame.font.SysFont("Arial", 32, bold=True)
            self.small_font = pygame.font.SysFont("Arial", 24, bold=True)

        self.reset()

    def reset(self):
        self.word = get_word()
        self.guessed_letters = set()
        self.tries = 0
        self.max_tries = 6
        self.game_state = "PLAYING" # PLAYING, WON, LOST

    def draw_hangman(self):
        # Gallow
        pygame.draw.line(self.screen, COLOR_FG, (100, 500), (300, 500), 5) # Base
        pygame.draw.line(self.screen, COLOR_FG, (200, 500), (200, 100), 5) # Post
        pygame.draw.line(self.screen, COLOR_FG, (200, 100), (300, 100), 5) # Beam
        pygame.draw.line(self.screen, COLOR_FG, (300, 100), (300, 150), 5) # Rope

        if self.tries >= 1: # Head
            pygame.draw.circle(self.screen, COLOR_MAGENTA, (300, 170), 20, 5)
        if self.tries >= 2: # Body
            pygame.draw.line(self.screen, COLOR_MAGENTA, (300, 190), (300, 300), 5)
        if self.tries >= 3: # Left Arm
            pygame.draw.line(self.screen, COLOR_MAGENTA, (300, 210), (260, 250), 5)
        if self.tries >= 4: # Right Arm
            pygame.draw.line(self.screen, COLOR_MAGENTA, (300, 210), (340, 250), 5)
        if self.tries >= 5: # Left Leg
            pygame.draw.line(self.screen, COLOR_MAGENTA, (300, 300), (260, 350), 5)
        if self.tries >= 6: # Right Leg
            pygame.draw.line(self.screen, COLOR_MAGENTA, (300, 300), (340, 350), 5)

    def draw_word(self):
        display_text = ""
        for char in self.word:
            if char in self.guessed_letters:
                display_text += char + " "
            else:
                display_text += "_ "
        
        text_surf = self.font.render(display_text, True, COLOR_CYAN)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(text_surf, text_rect)

    def draw_keyboard(self):
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        start_x = 100
        start_y = 460
        btn_w = 40
        btn_h = 40
        gap = 10

        for i, char in enumerate(alphabet):
            row = i // 13
            col = i % 13
            rect = pygame.Rect(start_x + col * (btn_w + gap), start_y + row * (btn_h + gap), btn_w, btn_h)
            
            color = COLOR_BG
            if char in self.guessed_letters:
                color = (60, 60, 50) # Darker
            
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, COLOR_FG, rect, 2, border_radius=5)
            
            txt = self.small_font.render(char, True, COLOR_YELLOW if char not in self.guessed_letters else COLOR_FG)
            txt_rect = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txt_rect)
            
            # Return rects for collision detection in the run loop
            # (Actually easier to just calculate based on mouse pos)

    def draw_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        msg = "YOU WON!" if self.game_state == "WON" else "GAME OVER"
        color = COLOR_GREEN if self.game_state == "WON" else COLOR_MAGENTA
        
        res_text = self.font.render(msg, True, color)
        res_rect = res_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(res_text, res_rect)
        
        word_text = self.font.render(f"Word was: {self.word}", True, COLOR_FG)
        word_rect = word_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(word_text, word_rect)
        
        restart_text = self.small_font.render("Press 'R' to Restart", True, COLOR_CYAN)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True
        while running:
            self.screen.fill(COLOR_BG)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                
                if event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "PLAYING":
                    mx, my = pygame.mouse.get_pos()
                    # Check keyboard clicks
                    start_x = 100
                    start_y = 460
                    btn_w = 40
                    btn_h = 40
                    gap = 10
                    
                    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    for i, char in enumerate(alphabet):
                        row = i // 13
                        col = i % 13
                        rect = pygame.Rect(start_x + col * (btn_w + gap), start_y + row * (btn_h + gap), btn_w, btn_h)
                        if rect.collidepoint(mx, my) and char not in self.guessed_letters:
                            self.guessed_letters.add(char)
                            if char not in self.word:
                                self.tries += 1
                            if all(c in self.guessed_letters for c in self.word):
                                self.game_state = "WON"
                            elif self.tries >= self.max_tries:
                                self.game_state = "LOST"

            self.draw_hangman()
            self.draw_word()
            self.draw_keyboard()
            
            if self.game_state != "PLAYING":
                self.draw_overlay()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    HangmanGame().run()
