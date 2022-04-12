import pygame
import random
import time
import os

SCREENWIDTH = 800
SCREENHEIGHT = 800
GRID_LENGTH = 20
GRID_HEIGHT = 20
BLOCK_LENGTH = SCREENWIDTH // 20

APPLE_PIC = pygame.transform.scale(pygame.image.load("apple.png"), (BLOCK_LENGTH, BLOCK_LENGTH))

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

pygame.font.init()
FONT = pygame.font.SysFont("comic sans ms", 50)


class Body:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.curr_direction = "N"

    def move(self, direction):
        if direction != "na":
            self.curr_direction = direction
            if self.curr_direction == "N":
                self.y -= 1
            elif self.curr_direction == "E":
                self.x += 1
            elif self.curr_direction == "S":
                self.y += 1
            else:
                self.x -= 1

    def draw(self, win):
        pygame.draw.rect(win, BLACK, [self.x * BLOCK_LENGTH, self.y * BLOCK_LENGTH, BLOCK_LENGTH, BLOCK_LENGTH])
        pygame.draw.rect(win, RED, [self.x * BLOCK_LENGTH + 1, self.y * BLOCK_LENGTH + 1, BLOCK_LENGTH - 1,
                                    BLOCK_LENGTH - 1])  # SQUARE


class Apple:
    def __init__(self):
        self.x = 0
        self.y = 0

    def draw_apple(self, win):
        win.blit(APPLE_PIC, (self.x * BLOCK_LENGTH, self.y * BLOCK_LENGTH))

    def place_apple(self, bodies):
        taken = True
        while taken:
            xy = [random.randint(0, 19), random.randint(0, 19)]
            used = [[body.x, body.y] for body in bodies]
            if xy not in used:
                taken = False
        self.x = xy[0]
        self.y = xy[1]


def draw_window(win, bodies, apple, score):
    win.fill(WHITE)
    for body in bodies:
        body.draw(win)
    apple.draw_apple(win)
    win.blit(FONT.render("Score: " + str(score), 1, BLACK), (0, 0))
    pygame.display.update()


def check_collisions(bodies):
    if bodies[0].x < 0 or bodies[0].x >= 20 or bodies[0].y < 0 or bodies[0].y >= 20:
        return True

    used = [[body.x, body.y] for body in bodies]
    print(used)
    for i in used:
        if used.count(i) > 1:
            return True


def ending_screen(win):
    while True:
        the_end = [FONT.render("You lost", 1, BLACK),
                   FONT.render("Press space to retry", 1, BLACK)]
        win.blit(the_end[0], (SCREENWIDTH // 2 - the_end[0].get_width() // 2, -100 + SCREENHEIGHT // 2))
        win.blit(the_end[1],
                 (SCREENWIDTH // 2 - the_end[1].get_width() // 2, -100 + the_end[0].get_height() + SCREENHEIGHT // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main()


def main():
    bodies = [Body(10, 10), Body(10, 11)]
    apple = Apple()
    apple.place_apple(bodies)

    move = "N"
    moves_list = ["N"]
    to_add = []

    win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    clock = pygame.time.Clock()

    score = 0
    ticks = 1

    lost = False

    while not lost:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if bodies[0].curr_direction != "S":
                        move = "N"
                if event.key == pygame.K_RIGHT:
                    if bodies[0].curr_direction != "W":
                        move = "E"
                if event.key == pygame.K_DOWN:
                    if bodies[0].curr_direction != "N":
                        move = "S"
                if event.key == pygame.K_LEFT:
                    if bodies[0].curr_direction != "E":
                        move = "W"

        if ticks % 10 == 0:

            if len(to_add) != 0:
                bodies.append(to_add[0])
                moves_list.append(to_add[1])
                to_add = []

            moves_list.insert(0, move)

            if len(moves_list) > len(bodies):
                moves_list.pop()

            for i in enumerate(moves_list):
                bodies[i[0]].move(i[1])
                if bodies[0].x == apple.x and bodies[0].y == apple.y:
                    score += 1

                    to_add.append(Body(bodies[len(bodies) - 1].x, bodies[len(bodies) - 1].y))
                    to_add.append(moves_list[len(moves_list) - 1])

                    apple.place_apple(bodies)

            lost = (check_collisions(bodies))

        draw_window(win, bodies, apple, score)
        ticks += 1

    ending_screen(win)


main()
