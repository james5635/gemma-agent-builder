# Introduction

This is plant vs. zombie game.

# Screenshot

![PVZ Screenshot](./pvz_screenshot.png)


# Run the game 

## python version

```sh
# make sure pygame is installed
pip install pygame

python pvz.py
```

## cpp version

```sh
# make sure sfml is installed
sudo pacman -Sy sfml # for arch linux

g++ pvz.cpp -opvz -lsfml-graphics -lsfml-window -lsfml-system
./pvz
```