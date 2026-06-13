import pygame
import sys
from typing import List, Optional, Union

# Monokai Theme Colors
BG_COLOR = (39, 40, 34)        # #272822
GRID_COLOR = (230, 219, 116)   # #E6DB74
X_COLOR = (249, 38, 114)       # #F92672
O_COLOR = (166, 226, 46)       # #A6E22E
TEXT_COLOR = (248, 248, 242)   # #F8F8F2

# Game Constants
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 10
SQUARE_SIZE = WIDTH // 3

class TicTacToe:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tic-Tac-Toe (Monokai)")
        self.font = pygame.font.SysFont("Arial", 80, bold=True)
        self.msg_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.board: List[List[Optional[str]]] = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.winner: Optional[str] = None

    def restart_game(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None

    def draw_lines(self):
        # Vertical lines
        pygame.draw.line(self.screen, GRID_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(self.screen, GRID_COLOR, (SQUARE_SIZE * 2, 0), (SQUARE_SIZE * 2, HEIGHT), LINE_WIDTH)
        # Horizontal lines
        pygame.draw.line(self.screen, GRID_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(self.screen, GRID_COLOR, (0, SQUARE_SIZE * 2), (WIDTH, SQUARE_SIZE * 2), LINE_WIDTH)

    def draw_symbols(self):
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "X":
                    text = self.font.render("X", True, X_COLOR)
                    text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    self.screen.blit(text, text_rect)
                elif self.board[row][col] == "O":
                    text = self.font.render("O", True, O_COLOR)
                    text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    self.screen.blit(text, text_rect)

    def check_winner(self) -> Optional[str]:
        # Check rows and columns
        for i in range(3):
            if self.board[i][0] and self.board[i][0] == self.board[i][1] == self.board[i][2] and self.board[i][0] is not None:
                return self.board[i][0]
            if self.board[0][i] and self.board[0][i] == self.board[1][i] == self.board[2][i] and self.board[0][i] is not None:
                return self.board[0][i]
        
        # Check diagonals
        if self.board[0][0] and self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] is not None:
            return self.board[0][0]
        if self.board[0][2] and self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] is not None:
            return self.board[0][2]
        
        # Check draw
        if all(cell is not None for row in self.board for cell in row):
            return "Draw"
        
        return None

    def run(self):
        while True:
            self.screen.fill(BG_COLOR)
            self.draw_lines()
            self.draw_symbols()
            
            if self.game_over:
                if self.winner == "Draw":
                    msg = self.msg_font.render("Draw!", True, TEXT_COLOR)
                else:
                    msg = self.msg_font.render(f"{self.winner} Wins!", True, TEXT_COLOR)
                msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(msg, msg_rect)
                
                restart_msg = self.msg_font.render("Press R to Restart", True, GRID_COLOR)
                restart_rect = restart_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
                self.screen.blit(restart_msg, restart_rect)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.restart_game()
                            break
                
                pygame.display.update()
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    mouseX = event.pos[0]
                    mouseY = event.pos[1]
                    row = mouseY // SQUARE_SIZE
                    col = mouseX // SQUARE_SIZE
                    
                    if self.board[row][col] is None:
                        # Player turn
                        self.board[row][col] = "X"
                        winner = self.check_winner()
                        if winner:
                            self.game_over = True
                            self.winner = winner
                        else:
                            # Bot turn
                            self.current_player = "O"
                            for r in range(3):
                                for c in range(3):
                                    if self.board[r][c] is None:
                                        self.board[r][c] = "O"
                                        winner = self.check_winner()
                                        if winner:
                                            self.game_over = True
                                            self.winner = winner
                                        else:
                                            self.current_player = "X"
                                        break
                                else: continue
                                break

            pygame.display.update()

if __name__ == "__main__":
    game = TicTacToe()
    game.run()
