# Introduction

This is hangman game.

# Screenshot

![Hangman Screenshot](./hangman_screenshot.png)


# Run the game 

## python version

```sh
# make sure pygame is installed
pip install pygame

python hangman.py
```

## cpp version

```sh
# make sure sfml is installed
sudo pacman -Sy sfml # for arch linux

g++ hangman.cpp -ohangman -lsfml-graphics -lsfml-window -lsfml-system
./hangman
```