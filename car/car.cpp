#include <SFML/Graphics.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <algorithm>
#include <optional>

const int SCREEN_WIDTH = 500;
const int SCREEN_HEIGHT = 700;
const int FPS = 60;

const sf::Color BG_COLOR(10, 8, 22);
const sf::Color ROAD_COLOR(20, 15, 35);
const sf::Color LINE_COLOR(0, 229, 255);
const sf::Color PLAYER_COLOR(255, 46, 99);
const sf::Color ENEMY_COLOR(255, 215, 0);
const sf::Color TEXT_COLOR(255, 255, 255);

const float CAR_WIDTH = 50.0f;
const float CAR_HEIGHT = 90.0f;
const float PLAYER_START_X = (SCREEN_WIDTH / 2.0f) - (CAR_WIDTH / 2.0f);
const float PLAYER_START_Y = SCREEN_HEIGHT - 120.0f;
const float LANE_WIDTH = SCREEN_WIDTH / 4.0f;

class Car {
public:
    sf::FloatRect rect;
    sf::Color color;
    float speed;

    Car(float x, float y, sf::Color c) : color(c), speed(0.0f) {
        rect = sf::FloatRect({x, y}, {CAR_WIDTH, CAR_HEIGHT});
    }

    void draw(sf::RenderWindow& window) {
        sf::RectangleShape body({CAR_WIDTH, CAR_HEIGHT});
        body.setPosition({rect.position.x, rect.position.y});
        body.setFillColor(color);
        window.draw(body);

        sf::RectangleShape windshield({CAR_WIDTH - 10.0f, 20.0f});
        windshield.setPosition({rect.position.x + 5.0f, rect.position.y + 15.0f});
        windshield.setFillColor(sf::Color(50, 50, 80));
        window.draw(windshield);

        sf::CircleShape lightL(5.0f);
        lightL.setPosition({rect.position.x + 5.0f, rect.position.y});
        lightL.setFillColor(sf::Color(255, 255, 200));
        window.draw(lightL);

        sf::CircleShape lightR(5.0f);
        lightR.setPosition({rect.position.x + CAR_WIDTH - 10.0f, rect.position.y});
        lightR.setFillColor(sf::Color(255, 255, 200));
        window.draw(lightR);
    }
};

class Game {
public:
    sf::RenderWindow window;
    sf::Font font;
    Car player;
    std::vector<Car> enemies;
    int score;
    bool game_over;
    float lane_offset;
    int enemy_spawn_timer;
    float game_speed;
    float current_speed;

    Game() : window(sf::VideoMode({SCREEN_WIDTH, SCREEN_HEIGHT}), "NEON RACER"),
             player(0, 0, PLAYER_COLOR) {
        window.setFramerateLimit(FPS);
        if (!font.openFromFile("/usr/share/fonts/libertinus/LibertinusSans-Bold.ttf")) {
            font.openFromFile("/usr/share/fonts/libertinus/LibertinusSans-Regular.ttf");
        }
        reset();
    }

    void reset() {
        player = Car(PLAYER_START_X, PLAYER_START_Y, PLAYER_COLOR);
        enemies.clear();
        score = 0;
        game_over = false;
        lane_offset = 0;
        enemy_spawn_timer = 0;
        game_speed = 5.0f;
        current_speed = 5.0f;
    }

    void spawn_enemy() {
        std::vector<int> lanes = {0, 1, 2, 3};
        static std::mt19937 gen(std::random_device{}());
        std::shuffle(lanes.begin(), lanes.end(), gen);

        for (int lane : lanes) {
            float x = lane * LANE_WIDTH + (LANE_WIDTH - CAR_WIDTH) / 2.0f;
            bool too_close = false;
            for (const auto& enemy : enemies) {
                if (enemy.rect.position.x == x && enemy.rect.position.y < 300.0f) {
                    too_close = true;
                    break;
                }
            }

            if (!too_close) {
                Car enemy(x, -CAR_HEIGHT, ENEMY_COLOR);
                float variance = 1.0f + (score / 10) * 0.5f;
                std::uniform_real_distribution<float> dist(-variance, variance);
                enemy.speed = dist(gen);
                enemies.push_back(enemy);
                return;
            }
        }
    }

    void update() {
        if (game_over) return;

        current_speed = game_speed;
        if (sf::Keyboard::isKeyPressed(sf::Keyboard::Key::Up) || sf::Keyboard::isKeyPressed(sf::Keyboard::Key::W)) {
            current_speed += 5.0f;
        }

        if ((sf::Keyboard::isKeyPressed(sf::Keyboard::Key::Left) || sf::Keyboard::isKeyPressed(sf::Keyboard::Key::A)) && player.rect.position.x > 0) {
            player.rect.position.x -= 7.0f;
        }
        if ((sf::Keyboard::isKeyPressed(sf::Keyboard::Key::Right) || sf::Keyboard::isKeyPressed(sf::Keyboard::Key::D)) && player.rect.position.x + CAR_WIDTH < SCREEN_WIDTH) {
            player.rect.position.x += 7.0f;
        }

        lane_offset += current_speed;
        if (lane_offset >= 100.0f) lane_offset = 0;

        int spawn_interval = std::max(30, 60 - (score / 2));
        enemy_spawn_timer++;
        if (enemy_spawn_timer > spawn_interval) {
            spawn_enemy();
            enemy_spawn_timer = 0;
        }

        for (auto it = enemies.begin(); it != enemies.end();) {
            it->rect.position.y += current_speed + it->speed;
            if (it->rect.position.y > SCREEN_HEIGHT) {
                it = enemies.erase(it);
                score++;
                if (score % 5 == 0) game_speed += 0.5f;
            } else {
                if (check_collision(player.rect, it->rect)) {
                    game_over = true;
                }
                ++it;
            }
        }
    }

    bool check_collision(const sf::FloatRect& a, const sf::FloatRect& b) {
        return (a.position.x < b.position.x + b.size.x &&
                a.position.x + a.size.x > b.position.x &&
                a.position.y < b.position.y + b.size.y &&
                a.position.y + a.size.y > b.position.y);
    }

    void draw() {
        window.clear(BG_COLOR);

        sf::RectangleShape road({(float)SCREEN_WIDTH, (float)SCREEN_HEIGHT});
        road.setFillColor(ROAD_COLOR);
        window.draw(road);

        for (int i = 1; i < 4; ++i) {
            float x = i * LANE_WIDTH;
            for (int y = -100; y < SCREEN_HEIGHT; y += 100) {
                sf::RectangleShape line({3.0f, 50.0f});
                line.setPosition({x, (float)y + lane_offset});
                line.setFillColor(LINE_COLOR);
                window.draw(line);
            }
        }

        player.draw(window);
        for (auto& enemy : enemies) enemy.draw(window);

        sf::Text scoreTxt(font, "SCORE: " + std::to_string(score));
        scoreTxt.setCharacterSize(24);
        scoreTxt.setPosition({20, 20});
        scoreTxt.setFillColor(TEXT_COLOR);
        window.draw(scoreTxt);

        sf::Text speedTxt(font, "SPEED: " + std::to_string((int)current_speed));
        speedTxt.setCharacterSize(24);
        speedTxt.setPosition({20, 50});
        speedTxt.setFillColor(LINE_COLOR);
        window.draw(speedTxt);

        if (game_over) {
            sf::RectangleShape overlay({(float)SCREEN_WIDTH, (float)SCREEN_HEIGHT});
            overlay.setFillColor(sf::Color(0, 0, 0, 180));
            window.draw(overlay);

            sf::Text goTxt(font, "GAME OVER");
            goTxt.setCharacterSize(30);
            goTxt.setFillColor(PLAYER_COLOR);
            goTxt.setPosition({SCREEN_WIDTH / 2.0f - 80.0f, SCREEN_HEIGHT / 2.0f - 20.0f});
            window.draw(goTxt);

            sf::Text reTxt(font, "Press 'R' to Restart");
            reTxt.setCharacterSize(20);
            reTxt.setFillColor(TEXT_COLOR);
            reTxt.setPosition({SCREEN_WIDTH / 2.0f - 100.0f, SCREEN_HEIGHT / 2.0f + 20.0f});
            window.draw(reTxt);
        }

        window.display();
    }

    void run() {
        while (window.isOpen()) {
            while (const std::optional event = window.pollEvent()) {
                if (event->is<sf::Event::Closed>()) window.close();
                if (const auto* keyPressed = event->getIf<sf::Event::KeyPressed>()) {
                    if (keyPressed->code == sf::Keyboard::Key::R && game_over) reset();
                }
            }
            update();
            draw();
        }
    }
};

int main() {
    Game game;
    game.run();
    return 0;
}
