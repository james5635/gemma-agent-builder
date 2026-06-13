#include <SFML/Graphics.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <set>
#include <algorithm>
#include <cmath>
#include <optional>

// Monokai Theme Colors
const sf::Color COLOR_BG(39, 40, 34);
const sf::Color COLOR_FG(248, 248, 242);
const sf::Color COLOR_YELLOW(230, 219, 116);
const sf::Color COLOR_MAGENTA(249, 38, 114);
const sf::Color COLOR_CYAN(102, 217, 239);
const sf::Color COLOR_GREEN(166, 226, 46);
const sf::Color COLOR_ORANGE(253, 151, 31);

const int SCREEN_WIDTH = 800;
const int SCREEN_HEIGHT = 600;

std::string getWord() {
    std::vector<std::string> words = {"PYTHON", "CPLUSPLUS", "SFML", "PROGRAMMING", "DEVELOPER", "COMPUTER", "NETWORK", "ALGORITHM", "SENSORS", "SYNTHWAVE"};
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, (int)words.size() - 1);
    return words[dis(gen)];
}

class HangmanGame {
public:
    HangmanGame() {
        window.create(sf::VideoMode({SCREEN_WIDTH, SCREEN_HEIGHT}), "MONOKAI HANGMAN");
        
        if (!font.openFromFile("/usr/share/fonts/libertinus/LibertinusSans-Bold.ttf")) {
            std::cerr << "Could not load font, please ensure /usr/share/fonts/libertinus/LibertinusSans-Bold.ttf exists." << std::endl;
        }
        
        reset();
    }

    void reset() {
        word = getWord();
        guessedLetters.clear();
        tries = 0;
        maxTries = 6;
        gameState = "PLAYING";
    }

    void drawLine(float x1, float y1, float x2, float y2, float thickness, sf::Color color) {
        sf::RectangleShape line;
        float dx = x2 - x1;
        float dy = y2 - y1;
        float length = std::sqrt(dx * dx + dy * dy);
        line.setSize({length, thickness});
        line.setRotation(sf::degrees(std::atan2(dy, dx) * 180.0f / 3.14159f));
        line.setPosition({x1, y1});
        line.setFillColor(color);
        window.draw(line);
    }

    void drawHangman() {
        drawLine(100, 500, 300, 500, 5, COLOR_FG);
        drawLine(200, 500, 200, 100, 5, COLOR_FG);
        drawLine(200, 100, 300, 100, 5, COLOR_FG);
        drawLine(300, 100, 300, 150, 5, COLOR_FG);

        if (tries >= 1) {
            sf::CircleShape head(20);
            head.setOutlineThickness(5);
            head.setOutlineColor(COLOR_MAGENTA);
            head.setFillColor(sf::Color::Transparent);
            head.setPosition({300.0f - 20.0f, 170.0f - 20.0f});
            window.draw(head);
        }
        if (tries >= 2) drawLine(300, 190, 300, 300, 5, COLOR_MAGENTA);
        if (tries >= 3) drawLine(300, 210, 260, 250, 5, COLOR_MAGENTA);
        if (tries >= 4) drawLine(300, 210, 340, 250, 5, COLOR_MAGENTA);
        if (tries >= 5) drawLine(300, 300, 260, 350, 5, COLOR_MAGENTA);
        if (tries >= 6) drawLine(300, 300, 340, 350, 5, COLOR_MAGENTA);
    }

    void drawWord() {
        std::string displayText = "";
        for (char c : word) {
            if (guessedLetters.count(c)) {
                displayText += c;
                displayText += " ";
            } else {
                displayText += "_ ";
            }
        }
        sf::Text text(font, displayText, 32);
        text.setFillColor(COLOR_CYAN);
        sf::FloatRect textRect = text.getLocalBounds();
        text.setOrigin({textRect.position.x + textRect.size.x / 2.0f, textRect.position.y + textRect.size.y / 2.0f});
        text.setPosition({SCREEN_WIDTH / 2.0f, 400.0f});
        window.draw(text);
    }

    void drawKeyboard() {
        std::string alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        float startX = 100, startY = 460;
        float btnW = 40, btnH = 40, gap = 10;

        for (int i = 0; i < (int)alphabet.length(); ++i) {
            char c = alphabet[i];
            int row = i / 13;
            int col = i % 13;
            float x = startX + col * (btnW + gap);
            float y = startY + row * (btnH + gap);

            sf::RectangleShape rect({btnW, btnH});
            rect.setPosition({x, y});
            rect.setFillColor(guessedLetters.count(c) ? sf::Color(60, 60, 50) : COLOR_BG);
            rect.setOutlineThickness(2);
            rect.setOutlineColor(COLOR_FG);
            window.draw(rect);

            sf::Text text(font, std::string(1, c), 24);
            text.setFillColor(guessedLetters.count(c) ? COLOR_FG : COLOR_YELLOW);
            sf::FloatRect textRect = text.getLocalBounds();
            text.setOrigin({textRect.position.x + textRect.size.x / 2.0f, textRect.position.y + textRect.size.y / 2.0f});
            text.setPosition({x + btnW / 2.0f, y + btnH / 2.0f});
            window.draw(text);
        }
    }

    void drawOverlay() {
        sf::RectangleShape overlay({(float)SCREEN_WIDTH, (float)SCREEN_HEIGHT});
        overlay.setFillColor(sf::Color(0, 0, 0, 180));
        window.draw(overlay);

        std::string msg = (gameState == "WON") ? "YOU WON!" : "GAME OVER";
        sf::Color color = (gameState == "WON") ? COLOR_GREEN : COLOR_MAGENTA;

        sf::Text resText(font, msg, 32);
        resText.setFillColor(color);
        sf::FloatRect resRect = resText.getLocalBounds();
        resText.setOrigin({resRect.position.x + resRect.size.x / 2.0f, resRect.position.y + resRect.size.y / 2.0f});
        resText.setPosition({SCREEN_WIDTH / 2.0f, SCREEN_HEIGHT / 2.0f - 20.0f});
        window.draw(resText);

        sf::Text wordText(font, "Word was: " + word, 32);
        wordText.setFillColor(COLOR_FG);
        sf::FloatRect wRect = wordText.getLocalBounds();
        wordText.setOrigin({wRect.position.x + wRect.size.x / 2.0f, wRect.position.y + wRect.size.y / 2.0f});
        wordText.setPosition({SCREEN_WIDTH / 2.0f, SCREEN_HEIGHT / 2.0f + 20.0f});
        window.draw(wordText);

        sf::Text restartText(font, "Press 'R' to Restart", 24);
        restartText.setFillColor(COLOR_CYAN);
        sf::FloatRect rRect = restartText.getLocalBounds();
        restartText.setOrigin({rRect.position.x + rRect.size.x / 2.0f, rRect.position.y + rRect.size.y / 2.0f});
        restartText.setPosition({SCREEN_WIDTH / 2.0f, SCREEN_HEIGHT / 2.0f + 60.0f});
        window.draw(restartText);
    }

    void run() {
        while (window.isOpen()) {
            while (const std::optional event = window.pollEvent()) {
                if (event->is<sf::Event::Closed>())
                    window.close();
                
                if (const auto* keyPressed = event->getIf<sf::Event::KeyPressed>()) {
                    if (keyPressed->code == sf::Keyboard::Key::R) {
                        reset();
                    }
                }

                if (const auto* mousePressed = event->getIf<sf::Event::MouseButtonPressed>()) {
                    if (mousePressed->button == sf::Mouse::Button::Left && gameState == "PLAYING") {
                        sf::Vector2i mousePos = sf::Mouse::getPosition(window);
                        float mx = (float)mousePos.x;
                        float my = (float)mousePos.y;
                        
                        std::string alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
                        float startX = 100, startY = 460, btnW = 40, btnH = 40, gap = 10;
                        
                        for (int i = 0; i < (int)alphabet.length(); ++i) {
                            char c = alphabet[i];
                            int row = i / 13;
                            int col = i % 13;
                            float x = startX + col * (btnW + gap);
                            float y = startY + row * (btnH + gap);
                            
                            if (mx >= x && mx <= x + btnW && my >= y && my <= y + btnH && !guessedLetters.count(c)) {
                                guessedLetters.insert(c);
                                if (word.find(c) == std::string::npos) {
                                    tries++;
                                }
                                
                                bool won = true;
                                for (char wc : word) {
                                    if (!guessedLetters.count(wc)) {
                                        won = false;
                                        break;
                                    }
                                }
                                if (won) gameState = "WON";
                                else if (tries >= maxTries) gameState = "LOST";
                            }
                        }
                    }
                }
            }

            window.clear(COLOR_BG);
            drawHangman();
            drawWord();
            drawKeyboard();
            if (gameState != "PLAYING") drawOverlay();
            window.display();
        }
    }

private:
    sf::RenderWindow window;
    sf::Font font;
    std::string word;
    std::set<char> guessedLetters;
    int tries;
    int maxTries;
    std::string gameState;
};

int main() {
    HangmanGame game;
    game.run();
    return 0;
}
