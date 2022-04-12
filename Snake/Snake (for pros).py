import pygame
import random
import os
import neat

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

GEN = 0


class Apple:
    def __init__(self):
        self.x = 0
        self.y = 0

    def draw_apple(self, win):
        win.blit(APPLE_PIC, (self.x * BLOCK_LENGTH, self.y * BLOCK_LENGTH))

    def place_apple(self, bodies):
        taken = True
        while taken:
            xy = [random.randint(0, GRID_LENGTH-1), random.randint(0, GRID_HEIGHT-1)]
            used = [[body.x, body.y] for body in bodies]
            if xy not in used:
                taken = False
        self.x = xy[0]
        self.y = xy[1]


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


class Snake:
    def __init__(self):
        self.score = 0
        self.move = "N"
        self.moves_list = ["N", "N"]
        self.to_add = []
        self.bodies = [Body(10, 10), Body(10, 11)]
        self.ticks_without_taking_apple = 0

    def check_collisions(self):
        if self.bodies[0].x < 0 or self.bodies[0].x >= 20 or self.bodies[0].y < 0 or self.bodies[0].y >= 20:
            return True

        used = [[body.x, body.y] for body in self.bodies]
        for i in used:
            if used.count(i) > 1:
                return True

    def move_place_apple(self, apple):
        self.ticks_without_taking_apple += 1
        if len(self.to_add) != 0:
            self.bodies.append(self.to_add[0])
            self.moves_list.append(self.to_add[1])
            self.to_add = []

        self.moves_list.insert(0, self.move)

        if len(self.moves_list) > len(self.bodies):
            self.moves_list.pop()

        apple_taken = False
        for i in enumerate(self.moves_list):
            self.bodies[i[0]].move(i[1])
            if self.bodies[0].x == apple.x and self.bodies[0].y == apple.y:
                self.score += 1
                self.ticks_without_taking_apple = 0

                self.to_add.append(Body(self.bodies[len(self.bodies) - 1].x, self.bodies[len(self.bodies) - 1].y))
                self.to_add.append(self.moves_list[len(self.moves_list) - 1])

                apple.place_apple(self.bodies)

                apple_taken = True

        return apple_taken


def draw_window(win, snakes, apples, snakes_alive):
    win.fill(WHITE)
    for snake in snakes:
        for body in snake.bodies:
            body.draw(win)
    for apple in apples:
        apple.draw_apple(win)

    gen_text = FONT.render("Generation: " + str(GEN), 1, BLACK)
    snakes_text = FONT.render("Snakes Alive: " + str(snakes_alive), 1, BLACK)
    win.blit(snakes_text, (10, 55))
    win.blit(gen_text, (10, 10))
    pygame.display.update()

def info_for_head(snake, apple):
    head = snake.bodies[0]
    xy = [[i.x, i.y] for i in snake.bodies]
    food_out = [0,0,0,0] # Is food N E S W?
    safe_out = [0,0,0,0] # Is safe N E S W?

    if abs(apple.x - head.x + 1) < abs(apple.x - head.x):
        food_out[1] = 1
    if abs(apple.x - head.x - 1) < abs(apple.x - head.x):
        food_out[3] = 1
    if abs(apple.y - head.y + 1) < abs(apple.y - head.y):
        food_out[0] = 1
    if abs(apple.y - head.y - 1) < abs(apple.y - head.y):
        food_out[2] = 1

    if [head.x + 1, head.y] not in xy and head.x + 1 <= 19:
        safe_out[1] = 1
    if [head.x - 1, head.y] not in xy and head.x - 1 >= 0:
        safe_out[3] = 1
    if [head.x, head.y + 1] not in xy and head.y + 1 <= 19:
        safe_out[0] = 1
    if [head.x, head.y - 1] not in xy and head.y - 1 >= 0:
        safe_out[2] = 1

    return food_out + safe_out

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    snakes = []
    apples = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)  # Creating the individual networks for each bird
        nets.append(net)
        snakes.append(Snake())
        g.fitness = 0
        ge.append(g)
        apples.append(Apple())

    for i, apple in enumerate(apples):
        apple.place_apple(snakes[i].bodies)

    win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    clock = pygame.time.Clock()

    ticks = 1

    run = True
    while run:
        clock.tick(200)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        if len(snakes) <= 0:
            run = False
        if ticks % 10 == 0:
            for x, snake in enumerate(snakes):
                previous_snake_pos = [snake.bodies[0].x, snake.bodies[0].y]
                if snake.move_place_apple(apples[x]):
                    ge[x].fitness += 10
                else:
                    if abs(apples[x].x - snake.bodies[0].x) < abs(apples[x].x - previous_snake_pos[0]) or abs(apples[x].y - snake.bodies[0].y) < abs(apples[x].y - previous_snake_pos[1]):
                        ge[x].fitness += 0.3
                    else:
                        ge[x].fitness -= 0.4

                info = info_for_head(snake, apples[x])

                output = nets[x].activate((info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7]))

                if output[0] > 0.5 and snake.bodies[0].curr_direction != "N":
                    snake.move = "S"
                elif output[1] > 0.5 and snake.bodies[0].curr_direction != "S":
                    snake.move = "N"
                elif output[2] > 0.5 and snake.bodies[0].curr_direction != "W":
                    snake.move = "E"
                elif output[3] > 0.5 and snake.bodies[0].curr_direction != "E":
                    snake.move = "W"

                if snake.check_collisions() or snake.ticks_without_taking_apple == 500:
                    ge[x].fitness -= 10
                    snakes.pop(x)
                    apples.pop(x)
                    nets.pop(x)
                    ge.pop(x)

        draw_window(win, snakes, apples, len(snakes))
        ticks += 1


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)  # Creating the network

    p.add_reporter(neat.StdOutReporter(True))  # Used to output stats from the networks
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 100)  # Run the program for 50 generations where main is the fitness function


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "snake-config-feedforward.txt")
    run(config_path)
