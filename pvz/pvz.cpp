#include <SFML/Graphics.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <cmath>
#include <algorithm>
#include <optional>
#include <memory>

const int SCREEN_WIDTH = 900;
const int SCREEN_HEIGHT = 600;
const int FPS = 60;

const sf::Color COLOR_BG_TOP(20, 10, 40);
const sf::Color COLOR_BG_BOT(50, 20, 80);
const sf::Color COLOR_GRID(0, 255, 255);
const sf::Color COLOR_SUN(255, 255, 0);
const sf::Color COLOR_ZOMBIE(255, 0, 255);
const sf::Color COLOR_PEASHOOTER(0, 255, 150);
const sf::Color COLOR_SUNFLOWER(255, 150, 0);
const sf::Color COLOR_PROJECTILE(0, 255, 255);
const sf::Color COLOR_TEXT(255, 255, 255);
const sf::Color COLOR_UI_BG(30, 10, 60);
const sf::Color COLOR_UI_BORDER(200, 0, 255);

const int GRID_ROWS = 5;
const int GRID_COLS = 9;
const int CELL_WIDTH = 80;
const int CELL_HEIGHT = 100;
const int OFFSET_X = 160;
const int OFFSET_Y = 100;

float random_float(float min, float max) {
    static std::mt19937 gen(std::random_device{}());
    std::uniform_real_distribution<float> dist(min, max);
    return dist(gen);
}

int random_int(int min, int max) {
    static std::mt19937 gen(std::random_device{}());
    std::uniform_int_distribution<int> dist(min, max);
    return dist(gen);
}

bool check_collision(const sf::FloatRect& a, const sf::FloatRect& b) {
    // SFML 3 uses findIntersection, but for simple boolean we can use basic AABB
    return (a.position.x < b.position.x + b.size.x &&
            a.position.x + a.size.x > b.position.x &&
            a.position.y < b.position.y + b.size.y &&
            a.position.y + a.size.y > b.position.y);
}

class Sun {
public:
    sf::FloatRect rect;
    bool is_natural;
    int life;
    float y_vel;
    std::unique_ptr<sf::Texture> texture;
    std::unique_ptr<sf::Sprite> sprite;
    bool has_image;

    Sun(float x, float y, bool natural = true) : is_natural(natural) {
        rect = sf::FloatRect({x, y}, {40.0f, 40.0f});
        life = 500;
        y_vel = natural ? random_float(0.5f, 1.5f) : 0.0f;
        
        auto tex = std::make_unique<sf::Texture>();
        if (tex->loadFromFile("sun.png")) {
            texture = std::move(tex);
            sprite = std::make_unique<sf::Sprite>(*texture);
            sprite->setScale({40.0f / (float)texture->getSize().x, 40.0f / (float)texture->getSize().y});
            has_image = true;
        } else {
            has_image = false;
        }
    }

    void update() {
        if (is_natural) {
            rect.position.y += y_vel;
            if (rect.position.y > SCREEN_HEIGHT - 60) {
                rect.position.y = SCREEN_HEIGHT - 60;
                is_natural = false;
            }
        }
        life--;
    }

    void draw(sf::RenderWindow& window) {
        if (has_image) {
            sprite->setPosition({rect.position.x, rect.position.y});
            window.draw(*sprite);
        } else {
            for (int r = 25; r >= 15; r -= 5) {
                sf::CircleShape glow(r);
                glow.setOrigin({(float)r, (float)r});
                glow.setPosition({rect.position.x + 20, rect.position.y + 20});
                glow.setFillColor(sf::Color(255, 255, 0, 50));
                window.draw(glow);
            }
            sf::CircleShape core(12);
            core.setOrigin({12.0f, 12.0f});
            core.setPosition({rect.position.x + 20, rect.position.y + 20});
            core.setFillColor(COLOR_SUN);
            window.draw(core);
        }
    }
};

class Projectile {
public:
    sf::FloatRect rect;
    float speed = 12.0f;
    Projectile(float x, float y) { rect = sf::FloatRect({x, y}, {15.0f, 15.0f}); }
    void update() { rect.position.x += speed; }
    void draw(sf::RenderWindow& window) {
        sf::CircleShape bullet(8);
        bullet.setOrigin({8.0f, 8.0f});
        bullet.setPosition({rect.position.x + 7.5f, rect.position.y + 7.5f});
        bullet.setFillColor(sf::Color(200, 255, 255));
        window.draw(bullet);
        sf::CircleShape core(5);
        core.setOrigin({5.0f, 5.0f});
        core.setPosition({rect.position.x + 7.5f, rect.position.y + 7.5f});
        core.setFillColor(COLOR_PROJECTILE);
        window.draw(core);
    }
};

class Zombie; // Forward declaration

class Plant {
public:
    sf::FloatRect rect;
    std::string type;
    int health = 100;
    int timer = 0;
    std::unique_ptr<sf::Texture> texture;
    std::unique_ptr<sf::Sprite> sprite;
    bool has_image;

    Plant(float x, float y, std::string t) : type(t) {
        rect = sf::FloatRect({x, y}, {(float)CELL_WIDTH - 20, (float)CELL_HEIGHT - 20});
        auto tex = std::make_unique<sf::Texture>();
        if (tex->loadFromFile(type + ".png")) {
            texture = std::move(tex);
            sprite = std::make_unique<sf::Sprite>(*texture);
            sprite->setScale({(float)(CELL_WIDTH - 20) / (float)texture->getSize().x, (float)(CELL_HEIGHT - 20) / (float)texture->getSize().y});
            has_image = true;
        } else {
            has_image = false;
        }
    }

    void update(std::vector<Sun>& suns) {
        timer++;
        if (type == "sunflower" && timer >= 150) {
            suns.emplace_back(rect.position.x + 20 + random_float(-30, 30), rect.position.y + 20 + random_float(-30, 30), false);
            timer = 0;
        }
    }

    void shoot(std::vector<Projectile>& projectiles, const std::vector<Zombie>& zombies);

    void draw(sf::RenderWindow& window) {
        if (has_image) {
            sprite->setPosition({rect.position.x, rect.position.y});
            window.draw(*sprite);
        } else {
            sf::Color color = (type == "peashooter") ? COLOR_PEASHOOTER : COLOR_SUNFLOWER;
            sf::CircleShape shape(25);
            shape.setOrigin({25.0f, 25.0f});
            shape.setPosition({rect.position.x + 20, rect.position.y + 20});
            shape.setOutlineThickness(3);
            shape.setOutlineColor(color);
            shape.setFillColor(sf::Color::Transparent);
            window.draw(shape);
            sf::CircleShape core(15);
            core.setOrigin({15.0f, 15.0f});
            core.setPosition({rect.position.x + 20, rect.position.y + 20});
            core.setFillColor(color);
            window.draw(core);
        }
            sf::RectangleShape hbBg({60.f, 5.f});
            hbBg.setPosition({rect.position.x, rect.position.y - 10});
            hbBg.setFillColor(sf::Color(50, 0, 50));
            window.draw(hbBg);
            sf::RectangleShape hbFg({60.f * (health / 100.0f), 5.f});
            hbFg.setPosition({rect.position.x, rect.position.y - 10});
            hbFg.setFillColor(sf::Color::Green);
            window.draw(hbFg);
    }
};

class Zombie {
public:
    sf::FloatRect rect;
    float speed = 0.4f;
    int health = 100;
    int attack_cooldown = 0;
    std::unique_ptr<sf::Texture> texture;
    std::unique_ptr<sf::Sprite> sprite;
    bool has_image;

    Zombie(int row) {
        rect = sf::FloatRect({(float)SCREEN_WIDTH, (float)(row * CELL_HEIGHT + OFFSET_Y + 10)}, {50.0f, 80.0f});
        auto tex = std::make_unique<sf::Texture>();
        if (tex->loadFromFile("zombie.png")) {
            texture = std::move(tex);
            sprite = std::make_unique<sf::Sprite>(*texture);
            sprite->setScale({50.0f / (float)texture->getSize().x, 80.0f / (float)texture->getSize().y});
            has_image = true;
        } else {
            has_image = false;
        }
    }

    void update(std::vector<Plant>& plants) {
        bool collision = false;
        for (auto& plant : plants) {
            if (check_collision(rect, plant.rect)) {
                collision = true;
                attack_cooldown++;
                if (attack_cooldown >= 60) {
                    plant.health -= 20;
                    attack_cooldown = 0;
                }
                break;
            }
        }
        if (!collision) {
            rect.position.x -= speed;
            attack_cooldown = 0;
        }
    }

    void draw(sf::RenderWindow& window) {
        if (has_image) {
            sprite->setPosition({rect.position.x, rect.position.y});
            window.draw(*sprite);
        } else {
            sf::RectangleShape body({50.f, 80.f});
            body.setPosition({rect.position.x, rect.position.y});
            body.setOutlineThickness(3);
            body.setOutlineColor(COLOR_ZOMBIE);
            body.setFillColor(sf::Color::Transparent);
            window.draw(body);
            sf::CircleShape head(12);
            head.setOrigin({12.0f, 12.0f});
            head.setPosition({rect.position.x + 25, rect.position.y + 20});
            head.setOutlineThickness(2);
            head.setOutlineColor(COLOR_ZOMBIE);
            head.setFillColor(sf::Color::Transparent);
            window.draw(head);
            sf::CircleShape eyeL(3);
            eyeL.setFillColor(sf::Color::White);
            eyeL.setPosition({rect.position.x + 20, rect.position.y + 18});
            window.draw(eyeL);
            sf::CircleShape eyeR(3);
            eyeR.setFillColor(sf::Color::White);
            eyeR.setPosition({rect.position.x + 30, rect.position.y + 18});
            window.draw(eyeR);
            sf::RectangleShape hbBg({40.f, 5.f});
            hbBg.setPosition({rect.position.x + 5, rect.position.y - 20});
            hbBg.setFillColor(sf::Color(50, 0, 50));
            window.draw(hbBg);
            sf::RectangleShape hbFg({40.f * (health / 100.0f), 5.f});
            hbFg.setPosition({rect.position.x + 5, rect.position.y - 20});
            hbFg.setFillColor(sf::Color::Red);
            window.draw(hbFg);
        }
    }
};

void Plant::shoot(std::vector<Projectile>& projectiles, const std::vector<Zombie>& zombies) {
    if (type == "peashooter" && timer >= 60) {
        bool zombie_in_lane = false;
        for (const auto& z : zombies) {
            if ((int)(z.rect.position.y / CELL_HEIGHT) == (int)(rect.position.y / CELL_HEIGHT)) {
                zombie_in_lane = true;
                break;
            }
        }
        if (zombie_in_lane) {
            projectiles.emplace_back(rect.position.x + rect.size.x, rect.position.y + rect.size.y / 2);
            timer = 0;
        }
    }
}

class Game {
public:
    sf::RenderWindow window;
    sf::Font font;
    sf::Texture texSunBtn, texPeaBtn;
    int sun_score;
    std::vector<Plant> plants;
    std::vector<Zombie> zombies;
    std::vector<Sun> suns;
    std::vector<Projectile> projectiles;
    std::string selected_plant;
    bool game_over;
    int frame_count;

    Game() {
        window.create(sf::VideoMode({SCREEN_WIDTH, SCREEN_HEIGHT}), "NEON PVZ C++");
        window.setFramerateLimit(FPS);
        if (!font.openFromFile("/usr/share/fonts/libertinus/LibertinusSans-Bold.ttf")) {
            if (!font.openFromFile("/usr/share/fonts/libertinus/LibertinusSans-Regular.ttf")) {
                std::cerr << "Failed to load any font!" << std::endl;
            }
        }
        if (!texSunBtn.loadFromFile("sunflower.png")) {
            std::cerr << "Failed to load sunflower button icon!" << std::endl;
        }
        if (!texPeaBtn.loadFromFile("peashooter.png")) {
            std::cerr << "Failed to load peashooter button icon!" << std::endl;
        }
        reset();
    }

    void reset() {
        sun_score = 100;
        plants.clear();
        zombies.clear();
        suns.clear();
        projectiles.clear();
        selected_plant = "";
        game_over = false;
        frame_count = 0;
    }

    void spawn_sun() {
        suns.emplace_back(random_float(OFFSET_X, SCREEN_WIDTH - 50), random_float(-100, 0));
    }

    void update() {
        if (game_over) return;
        frame_count++;

        float spawn_chance = std::min(0.06f, 0.003f + (frame_count / 15000.0f) * 0.057f);
        if (random_float(0, 1) < spawn_chance) {
            int min_cluster = 1 + (int)(frame_count / 3600.0f) * 9;
            int max_cluster = min_cluster + random_int(0, 5);
            int num = random_int(min_cluster, max_cluster);
            for (int i = 0; i < num; ++i) zombies.emplace_back(random_int(0, GRID_ROWS - 1));
        }
        if (random_float(0, 1) < 0.01f) spawn_sun();

        for (auto it = suns.begin(); it != suns.end();) {
            it->update();
            if (it->life <= 0) it = suns.erase(it); else ++it;
        }
        for (auto it = plants.begin(); it != plants.end();) {
            it->update(suns);
            if (it->health <= 0) it = plants.erase(it); else ++it;
        }
        for (auto it = zombies.begin(); it != zombies.end();) {
            it->update(plants);
            if (it->rect.position.x < OFFSET_X) { game_over = true; break; }
            if (it->health <= 0) it = zombies.erase(it); else ++it;
        }
        for (auto it = projectiles.begin(); it != projectiles.end();) {
            it->update();
            bool hit = false;
            for (auto& z : zombies) {
                if (check_collision(it->rect, z.rect)) {
                    z.health -= 20;
                    hit = true;
                    break;
                }
            }
            if (hit || it->rect.position.x > SCREEN_WIDTH) it = projectiles.erase(it); else ++it;
        }
        for (auto& p : plants) p.shoot(projectiles, zombies);
    }

    void draw() {
        window.clear();
        sf::VertexArray gradient(sf::PrimitiveType::TriangleFan, 4);
        gradient[0].position = {0, 0}; gradient[0].color = COLOR_BG_TOP;
        gradient[1].position = {SCREEN_WIDTH, 0}; gradient[1].color = COLOR_BG_TOP;
        gradient[2].position = {SCREEN_WIDTH, SCREEN_HEIGHT}; gradient[2].color = COLOR_BG_BOT;
        gradient[3].position = {0, SCREEN_HEIGHT}; gradient[3].color = COLOR_BG_BOT;
        window.draw(gradient);

        for (int r = 0; r <= GRID_ROWS; ++r) {
            sf::RectangleShape line({(float)(SCREEN_WIDTH - OFFSET_X), 2.f});
            line.setPosition({(float)OFFSET_X, (float)(OFFSET_Y + r * CELL_HEIGHT)});
            line.setFillColor(COLOR_GRID);
            window.draw(line);
        }
        for (int c = 0; c <= GRID_COLS; ++c) {
            sf::RectangleShape line({2.f, (float)(GRID_ROWS * CELL_HEIGHT)});
            line.setPosition({(float)(OFFSET_X + c * CELL_WIDTH), (float)OFFSET_Y});
            line.setFillColor(COLOR_GRID);
            window.draw(line);
        }

        sf::RectangleShape uiPanel({140.f, (float)SCREEN_HEIGHT});
        uiPanel.setFillColor(COLOR_UI_BG);
        window.draw(uiPanel);
        sf::RectangleShape uiBorder({3.f, (float)SCREEN_HEIGHT});
        uiBorder.setPosition({140.0f, 0.0f});
        uiBorder.setFillColor(COLOR_UI_BORDER);
        window.draw(uiBorder);

        sf::Text sunTxt(font, "SUN: " + std::to_string(sun_score));
        sunTxt.setCharacterSize(20);
        sunTxt.setPosition({20, 30});
        sunTxt.setFillColor(COLOR_TEXT);
        window.draw(sunTxt);

        int time_seconds = frame_count / FPS;
        int hours = time_seconds / 3600;
        int minutes = (time_seconds % 3600) / 60;
        int seconds = time_seconds % 60;
        char time_buf[32];
        snprintf(time_buf, sizeof(time_buf), "TIME: %02d:%02d:%02d", hours, minutes, seconds);
        sf::Text timeTxt(font, time_buf);
        timeTxt.setCharacterSize(20);
        timeTxt.setPosition({20, 60});
        timeTxt.setFillColor(COLOR_TEXT);
        window.draw(timeTxt);

        draw_button("SUNFLOWER", 0, 100, COLOR_SUNFLOWER, 50, &texSunBtn);
        draw_button("PEA-SHOT", 1, 100, COLOR_PEASHOOTER, 100, &texPeaBtn);

        for (auto& s : suns) s.draw(window);
        for (auto& p : plants) p.draw(window);
        for (auto& z : zombies) z.draw(window);
        for (auto& pr : projectiles) pr.draw(window);

        if (game_over) {
            sf::RectangleShape overlay({(float)SCREEN_WIDTH, (float)SCREEN_HEIGHT});
            overlay.setFillColor(sf::Color(0, 0, 0, 180));
            window.draw(overlay);
            sf::Text goTxt(font, "SYSTEM FAILURE: BRAINS CONSUMED");
            goTxt.setCharacterSize(30);
            goTxt.setPosition({SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2});
            goTxt.setFillColor(sf::Color::Red);
            window.draw(goTxt);
            sf::Text reTxt(font, "PRESS 'R' TO REBOOT");
            reTxt.setCharacterSize(20);
            reTxt.setPosition({SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 40});
            reTxt.setFillColor(COLOR_TEXT);
            window.draw(reTxt);
        }
        window.display();
    }

    void draw_button(std::string name, int idx, int y, sf::Color color, int cost, sf::Texture* tex = nullptr) {
        sf::RectangleShape rect({110.f, 60.f});
        rect.setPosition({15.0f, (float)(y + (idx * 80))});
        rect.setFillColor(sf::Color(20, 0, 40));
        rect.setOutlineThickness(2);
        rect.setOutlineColor(color);
        window.draw(rect);

        if (tex) {
            sf::Sprite s(*tex);
            s.setPosition({rect.getPosition().x + 5, rect.getPosition().y + 5});
            s.setScale({40.0f / tex->getSize().x, 40.0f / tex->getSize().y});
            window.draw(s);
        }

        sf::Text txt(font);
        txt.setString(name);
        txt.setCharacterSize(14);
        txt.setPosition({rect.getPosition().x + 45, rect.getPosition().y + 12});
        txt.setFillColor(color);
        window.draw(txt);

        sf::Text ctxt(font);
        ctxt.setString(std::to_string(cost) + " S");
        ctxt.setCharacterSize(14);
        ctxt.setPosition({rect.getPosition().x + 45, rect.getPosition().y + 32});
        ctxt.setFillColor(COLOR_TEXT);
        window.draw(ctxt);
    }

    void run() {
        while (window.isOpen()) {
            while (const std::optional event = window.pollEvent()) {
                if (event->is<sf::Event::Closed>()) window.close();
                if (const auto* keyPressed = event->getIf<sf::Event::KeyPressed>()) {
                    if (keyPressed->code == sf::Keyboard::Key::R && game_over) reset();
                }
                if (const auto* mousePressed = event->getIf<sf::Event::MouseButtonPressed>()) {
                    sf::Vector2i pos = sf::Mouse::getPosition(window);
                    for (auto it = suns.begin(); it != suns.end();) {
                        if (it->rect.contains({(float)pos.x, (float)pos.y})) {
                            sun_score += 25;
                            it = suns.erase(it);
                        } else ++it;
                    }
                    if (pos.x < 140) {
                        if (pos.y >= 100 && pos.y < 160) selected_plant = "sunflower";
                        else if (pos.y >= 170 && pos.y < 230) selected_plant = "peashooter";
                    } else if (!selected_plant.empty()) {
                        int cost = (selected_plant == "sunflower") ? 50 : 100;
                        if (sun_score >= cost) {
                            int col = (pos.x - OFFSET_X) / CELL_WIDTH;
                            int row = (pos.y - OFFSET_Y) / CELL_HEIGHT;
                            if (col >= 0 && col < GRID_COLS && row >= 0 && row < GRID_ROWS) {
                                bool occ = false;
                                for (auto& p : plants) if (check_collision(p.rect, sf::FloatRect({(float)pos.x, (float)pos.y}, {1.0f, 1.0f}))) occ = true;
                                if (!occ) {
                                    plants.emplace_back(OFFSET_X + col * CELL_WIDTH + 10, OFFSET_Y + row * CELL_HEIGHT + 10, selected_plant);
                                    sun_score -= cost;
                                    selected_plant = "";
                                }
                            }
                        }
                    }
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
