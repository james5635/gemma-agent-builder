#include <SFML/Graphics.hpp>
#include <iostream>
#include <vector>
#include <string>

// Monokai Theme Colors
const sf::Color BG_COLOR(39, 40, 34);        // #272822
const sf::Color GRID_COLOR(230, 219, 116);   // #E6DB74
const sf::Color X_COLOR(249, 38, 114);       // #F92672
const sf::Color O_COLOR(166, 226, 46);       // #A6E22E
const sf::Color TEXT_COLOR(248, 248, 242);   // #F8F8F2

// Game Constants
const int WIDTH = 600;
const int HEIGHT = 600;
const float LINE_WIDTH = 10.0f;
const int SQUARE_SIZE = WIDTH / 3;

class TicTacToe {
private:
    sf::RenderWindow window;
    sf::Font font;
    std::vector<std::vector<std::string>> board;
    std::string current_player;
    bool game_over;
    std::string winner;

public:
    TicTacToe() :
        window(sf::VideoMode({(unsigned int)WIDTH, (unsigned int)HEIGHT}), "Tic-Tac-Toe (SFML 3)"),
        board(3, std::vector<std::string>(3, "")),
        current_player("X"),
        game_over(false),
        winner("")
    {
        window.setFramerateLimit(60);

        std::vector<std::string> system_fonts = {
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/ttf-linux-libertine/LinLibertine_I.ttf",
            "Arial.ttf"
        };

        bool loaded = false;
        for (const auto& font_path : system_fonts) {
            if (font.openFromFile(font_path)) {
                std::cout << "Successfully loaded font: " << font_path << std::endl;
                loaded = true;
                break;
            }
        }

        if (!loaded) {
            std::cerr << "Error: Could not load any system fonts. Please place 'Arial.ttf' in the executable directory." << std::endl;
        }
    }

    void restart_game() {
        board.assign(3, std::vector<std::string>(3, ""));
        current_player = "X";
        game_over = false;
        winner = "";
    }

    void draw_lines() {
        sf::VertexArray lines(sf::PrimitiveType::Lines, 8);
        lines[0].position = { (float)SQUARE_SIZE, 0.f };
        lines[1].position = { (float)SQUARE_SIZE, (float)HEIGHT };
        lines[2].position = { (float)SQUARE_SIZE * 2, 0.f };
        lines[3].position = { (float)SQUARE_SIZE * 2, (float)HEIGHT };
        lines[4].position = { 0.f, (float)SQUARE_SIZE };
        lines[5].position = { (float)WIDTH, (float)SQUARE_SIZE };
        lines[6].position = { 0.f, (float)SQUARE_SIZE * 2 };
        lines[7].position = { (float)WIDTH, (float)SQUARE_SIZE * 2 };

        for (int i = 0; i < 8; ++i) lines[i].color = GRID_COLOR;
        window.draw(lines);
    }

    void draw_symbols() {
        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 3; ++col) {
                if (board[row][col] == "X") {
                    sf::Text text(font, "X", 80);
                    text.setFillColor(X_COLOR);
                    text.setOrigin({40.f, 40.f});
                    text.setPosition({(float)col * SQUARE_SIZE + SQUARE_SIZE / 2.0f, (float)row * SQUARE_SIZE + SQUARE_SIZE / 2.0f});
                    window.draw(text);
                } else if (board[row][col] == "O") {
                    sf::Text text(font, "O", 80);
                    text.setFillColor(O_COLOR);
                    text.setOrigin({40.f, 40.f});
                    text.setPosition({(float)col * SQUARE_SIZE + SQUARE_SIZE / 2.0f, (float)row * SQUARE_SIZE + SQUARE_SIZE / 2.0f});
                    window.draw(text);
                }
            }
        }
    }

    std::string check_winner() {
        for (int i = 0; i < 3; ++i) {
            if (board[i][0] != "" && board[i][0] == board[i][1] && board[i][0] == board[i][2]) return board[i][0];
            if (board[0][i] != "" && board[0][i] == board[1][i] && board[0][i] == board[2][i]) return board[0][i];
        }
        if (board[0][0] != "" && board[0][0] == board[1][1] && board[0][0] == board[2][2]) return board[0][0];
        if (board[0][2] != "" && board[0][2] == board[1][1] && board[0][2] == board[2][0]) return board[0][2];

        bool draw = true;
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                if (board[i][j] == "") draw = false;
            }
        }
        if (draw) return "Draw";

        return "";
    }

    void run() {
        while (window.isOpen()) {
            while (auto ev = window.pollEvent()) {
                if (ev->is<sf::Event::Closed>()) {
                    window.close();
                }
                if (ev->is<sf::Event::MouseButtonPressed>()) {
                    const auto* mouse_event = ev->getIf<sf::Event::MouseButtonPressed>();
                    if (mouse_event && mouse_event->button == sf::Mouse::Button::Left && !game_over) {
                        const auto& mouse_pos = mouse_event->position;
                        int row = mouse_pos.y / SQUARE_SIZE;
                        int col = mouse_pos.x / SQUARE_SIZE;

                        if (row >= 0 && row < 3 && col >= 0 && col < 3 && board[row][col] == "") {
                            board[row][col] = current_player;
                            std::string res = check_winner();
                            if (res != "") {
                                game_over = true;
                                winner = res;
                            } else {
                                current_player = (current_player == "X") ? "O" : "X";
                            }
                        }
                    }
                }
                if (ev->is<sf::Event::KeyPressed>()) {
                    if (ev->getIf<sf::Event::KeyPressed>()->code == sf::Keyboard::Key::R) {
                        restart_game();
                    }
                }
            }

            window.clear(BG_COLOR);
            draw_lines();
            draw_symbols();

            if (game_over) {
                sf::String win_text = (winner == "Draw") ? "Draw!" : (sf::String(winner) + " Wins!");
                sf::Text msg(font, win_text, 40);
                msg.setFillColor(TEXT_COLOR);
                msg.setPosition({WIDTH / 2.0f - msg.getGlobalBounds().size.x / 2.0f, HEIGHT / 2.0f - msg.getGlobalBounds().size.y / 2.0f});
                window.draw(msg);

                sf::Text restart_msg(font, "Press R to Restart", 30);
                restart_msg.setFillColor(GRID_COLOR);
                restart_msg.setPosition({WIDTH / 2.0f - restart_msg.getGlobalBounds().size.x / 2.0f, HEIGHT / 2.0f + 50});
                window.draw(restart_msg);
            }

            window.display();
        }
    }
};

int main() {
    TicTacToe game;
    game.run();
    return 0;
}
