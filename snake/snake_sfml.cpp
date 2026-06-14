#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include <deque>
#include <vector>
#include <random>
#include <optional>
#include <string>
#include <iostream>

// Monokai Theme Colors
namespace Monokai {
    const sf::Color Background{0x27, 0x28, 0x22};
    const sf::Color Panel{0x18, 0x19, 0x1e}; // Darker panel for better contrast
    const sf::Color SnakeBody{0xA6, 0xE2, 0x2E};
    const sf::Color SnakeHead{0xF9, 0x26, 0x72};
    const sf::Color Food{0xFD, 0x97, 0x1F};
    const sf::Color GoldenFood{0xFFD700};
    const sf::Color Text{0xF8, 0xF8, 0xF8};
}

class SnakeGame {
public:
    SnakeGame(unsigned int width, unsigned int height, unsigned int gridSize, const std::string& fontPath)
        : m_width(width), m_height(height), m_gridSize(gridSize), m_isGameOver(false), m_score(0), m_highScore(0), m_foodEatenCount(0), m_panelWidth(200) {

        m_cols = (m_width - m_panelWidth) / m_gridSize;
        m_rows = m_height / m_gridSize;

        m_window.create(sf::VideoMode({m_width, m_height}), "Snake SFML 3 - Enhanced Monokai");
        m_window.setFramerateLimit(10);

        if (!m_font.openFromFile(fontPath)) {
            std::cerr << "Error loading font: " << fontPath << std::endl;
        }

        setupText();
        reset();
    }

    void run() {
        while (m_window.isOpen()) {
            handleEvents();
            if (!m_isGameOver) {
                update();
            }
            render();
        }
    }

private:
    void setupText() {
        m_scoreText.emplace(m_font, "", 20);
        if (m_scoreText) {
            m_scoreText->setFillColor(Monokai::Text);
        }

        m_highScoreText.emplace(m_font, "", 20);
        if (m_highScoreText) {
            m_highScoreText->setFillColor(Monokai::Text);
        }

        m_gameOverText.emplace(m_font, "", 50);
        if (m_gameOverText) {
            m_gameOverText->setFillColor(Monokai::SnakeHead);
            m_gameOverText->setStyle(sf::Text::Bold);
        }

        m_restartText.emplace(m_font, "", 20);
        if (m_restartText) {
            m_restartText->setFillColor(Monokai::Text);
        }
    }

    void reset() {
        m_snake.clear();
        m_snake.push_back({0, 10});
        m_snake.push_back({0, 11});
        m_snake.push_back({0, 12});

        m_direction = {0, -1};
        m_isGameOver = false;
        m_score = 0;
        m_foodEatenCount = 0;
        m_goldenFood = std::nullopt;
        m_window.setFramerateLimit(10);
    }

    void handleEvents() {
        while (const std::optional event = m_window.pollEvent()) {
            if (event->is<sf::Event::Closed>()) {
                m_window.close();
            } else if (const auto* keyPressed = event->getIf<sf::Event::KeyPressed>()) {
                switch (keyPressed->scancode) {
                    case sf::Keyboard::Scancode::Up:
                        if (m_direction.y != 1) m_direction = {0, -1};
                        break;
                    case sf::Keyboard::Scancode::Down:
                        if (m_direction.y != -1) m_direction = {0, 1};
                        break;
                    case sf::Keyboard::Scancode::Left:
                        if (m_direction.x != 1) m_direction = {-1, 0};
                        break;
                    case sf::Keyboard::Scancode::Right:
                        if (m_direction.x != -1) m_direction = {1, 0};
                        break;
                    case sf::Keyboard::Scancode::R:
                        reset();
                        break;
                    case sf::Keyboard::Scancode::Escape:
                        m_window.close();
                        break;
                    default:
                        break;
                }
            }
        }
    }

    void update() {
        sf::Vector2i newHead = m_snake.front() + m_direction;

        // Wall wrapping
        if (newHead.x < 0) newHead.x = m_cols - 1;
        else if (newHead.x >= static_cast<int>(m_cols)) newHead.x = 0;

        if (newHead.y < 0) newHead.y = m_rows - 1;
        else if (newHead.y >= static_cast<int>(m_rows)) newHead.y = 0;

        for (const auto& segment : m_snake) {
            if (newHead == segment) {
                m_isGameOver = true;
                return;
            }
        }

        m_snake.push_front(newHead);

        if (m_goldenFood && newHead == *m_goldenFood) {
            m_score += 50;
            m_goldenFood = std::nullopt;
            m_foodEatenCount = 0;
        } else if (newHead == m_food) {
            m_score += 10;
            m_foodEatenCount++;
            generateFood();

            unsigned int newLimit = 10 + (m_score / 20);
            m_window.setFramerateLimit(newLimit);

            if (m_foodEatenCount >= 10) {
                generateGoldenFood();
            }
        } else {
            m_snake.pop_back();
        }

        if (m_score > m_highScore) {
            m_highScore = m_score;
        }
    }

    void generateFood() {
        static std::mt19937 gen(std::random_device{}());
        std::uniform_int_distribution<int> distX(0, m_cols - 1);
        std::uniform_int_distribution<int> distY(0, m_rows - 1);

        m_food = {distX(gen), distY(gen)};

        for (const auto& segment : m_snake) {
            if (m_food == segment) {
                generateFood();
                return;
            }
        }
    }

    void generateGoldenFood() {
        static std::mt19937 gen(std::random_device{}());
        std::uniform_int_distribution<int> distX(0, m_cols - 1);
        std::uniform_int_distribution<int> distY(0, m_rows - 1);

        m_goldenFood = {distX(gen), distY(gen)};

        for (const auto& segment : m_snake) {
            if (m_goldenFood == segment) {
                generateGoldenFood();
                return;
            }
        }
    }

    void render() {
        m_window.clear(Monokai::Background);

        // Draw Panel
        sf::RectangleShape panelShape(sf::Vector2f(static_cast<float>(m_panelWidth), static_cast<float>(m_height)));
        panelShape.setFillColor(Monokai::Panel);
        panelShape.setPosition({0.f, 0.f});
        m_window.draw(panelShape);

        // Draw Food
        sf::RectangleShape foodShape(sf::Vector2f(m_gridSize, m_gridSize));
        foodShape.setFillColor(Monokai::Food);
        foodShape.setPosition({static_cast<float>(m_food.x * m_gridSize + m_panelWidth), static_cast<float>(m_food.y * m_gridSize)});
        m_window.draw(foodShape);

        // Draw Golden Food
        if (m_goldenFood) {
            sf::RectangleShape goldShape(sf::Vector2f(m_gridSize, m_gridSize));
            goldShape.setFillColor(Monokai::GoldenFood);
            goldShape.setPosition({static_cast<float>(m_goldenFood->x * m_gridSize + m_panelWidth), static_cast<float>(m_goldenFood->y * m_gridSize)});
            m_window.draw(goldShape);
        }

        // Draw Snake
        for (size_t i = 0; i < m_snake.size(); ++i) {
            sf::RectangleShape segmentShape(sf::Vector2f(m_gridSize - 1, m_gridSize - 1));
            segmentShape.setFillColor(i == 0 ? Monokai::SnakeHead : Monokai::SnakeBody);
            segmentShape.setPosition({static_cast<float>(m_snake[i].x * m_gridSize + m_panelWidth), static_cast<float>(m_snake[i].y * m_gridSize)});
            m_window.draw(segmentShape);
        }

        // Draw UI (Centered in Panel)
        if (m_scoreText) {
            m_scoreText->setString("Score: " + std::to_string(m_score));
            sf::FloatRect textRect = m_scoreText->getLocalBounds();
            m_scoreText->setOrigin({textRect.position.x + textRect.size.x / 2.0f, textRect.position.y + textRect.size.y / 2.0f});
            m_scoreText->setPosition({static_cast<float>(m_panelWidth) / 2.0f, 30.f});
            m_window.draw(*m_scoreText);
        }

        if (m_highScoreText) {
            m_highScoreText->setString("High Score: " + std::to_string(m_highScore));
            sf::FloatRect textRect = m_highScoreText->getLocalBounds();
            m_highScoreText->setOrigin({textRect.position.x + textRect.size.x / 2.0f, textRect.position.y + textRect.size.y / 2.0f});
            m_highScoreText->setPosition({static_cast<float>(m_panelWidth) / 2.0f, 60.f});
            m_window.draw(*m_highScoreText);
        }

        if (m_isGameOver) {
            float gameAreaCenterX = static_cast<float>(m_panelWidth) + (static_cast<float>(m_width - m_panelWidth) / 2.0f);
            float gameAreaCenterY = static_cast<float>(m_height) / 2.0f;

            if (m_gameOverText) {
                m_gameOverText->setString("GAME OVER");
                sf::FloatRect textRect = m_gameOverText->getLocalBounds();
                m_gameOverText->setOrigin({textRect.position.x + textRect.size.x / 2.0f, textRect.position.y + textRect.size.y / 2.0f});
                m_gameOverText->setPosition({gameAreaCenterX, gameAreaCenterY});
                m_window.draw(*m_gameOverText);
            }

            if (m_restartText) {
                m_restartText->setString("Press 'R' to Restart");
                sf::FloatRect rtRect = m_restartText->getLocalBounds();
                m_restartText->setOrigin({rtRect.position.x + rtRect.size.x / 2.0f, rtRect.position.y + rtRect.size.y / 2.0f});
                m_restartText->setPosition({gameAreaCenterX, gameAreaCenterY + 60.0f});
                m_window.draw(*m_restartText);
            }
        }

        m_window.display();
    }

    sf::RenderWindow m_window;
    unsigned int m_width;
    unsigned int m_height;
    unsigned int m_gridSize;
    unsigned int m_panelWidth;
    unsigned int m_cols;
    unsigned int m_rows;
    std::deque<sf::Vector2i> m_snake;
    sf::Vector2i m_direction;
    sf::Vector2i m_food;
    std::optional<sf::Vector2i> m_goldenFood;
    bool m_isGameOver;
    int m_score;
    int m_highScore;
    int m_foodEatenCount;

    sf::Font m_font;
    std::optional<sf::Text> m_scoreText;
    std::optional<sf::Text> m_highScoreText;
    std::optional<sf::Text> m_gameOverText;
    std::optional<sf::Text> m_restartText;
};

int main() {
    const std::string fontPath = "/usr/share/fonts/TTF/DejaVuSansMono.ttf";
    SnakeGame game(800, 600, 20, fontPath);
    game.run();
    return 0;
}
