import pygame
import neat
import random
import os

pygame.font.init()

SCREEN_WIDTH = 576
SCREEN_HEIGHT = 800
GEN = 0
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("arial", 50)


class Bird:
    IMG = BIRD_IMAGES
    MAX_ROTATION = 25
    ROT_VEL = 15
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0  # Units of time
        self.vel = 0  # Pixels per tick
        self.height = self.y
        self.image_count = 0  # Needed for creating the flapping animation
        self.img = self.IMG[0]

    def jump(self):
        self.vel = -10.5  # Up is negative, down is positive
        self.tick_count = 0
        self.height = self.y
        self.tilt = self.MAX_ROTATION

    def move(self):
        self.tick_count += 1  # Adding 1 to "time"
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2  # Displacement

        if d >= 14:  # Terminal velocity
            d = 14

        # if d < 0:  # Smoothing of jumping motion
        # d = -7

        self.y = self.y + d  # Tracking position of bird

        if d < 0 or self.y < self.height - 20:  # Checking if the bird is moving up or above previous pos
            if self.tilt > self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
            elif self.tilt < -90:
                self.tilt = -90

    def draw(self, win):
        self.image_count += 1
        if self.image_count < self.ANIMATION_TIME:  # Animates the flapping
            self.img = self.IMG[0]
        elif self.image_count < self.ANIMATION_TIME * 2:
            self.img = self.IMG[1]
        elif self.image_count < self.ANIMATION_TIME * 3:
            self.img = self.IMG[2]
        elif self.image_count < self.ANIMATION_TIME * 4:
            self.img = self.IMG[1]
        elif self.image_count == self.ANIMATION_TIME * 4 + 1:  # Reset the animation
            self.img = self.IMG[0]
            self.image_count = 0

        if self.tilt <= -80:  # Stop flapping when nose diving
            self.img = self.IMG[1]
            self.image_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)  # Code to rotate about centre and then output
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):  # For collisions
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 150
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 100
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()  # Generates 2D list of pixels of bird
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))  # Finds distance between bird and top pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))  # Finds distance between bird and bottom pipe

        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)  # Check for overlapping pixels
        top_point = bird_mask.overlap(top_mask, top_offset)

        if top_point or bottom_point:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMAGE.get_width()
    IMG = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, birds_alive):
    win.blit(BG_IMAGE, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    for bird in birds:
        bird.draw(win)
    base.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    gen_text = STAT_FONT.render("Generation: " + str(GEN), 1, (255, 255, 255))
    birds_text = STAT_FONT.render("Birds Alive: " + str(birds_alive), 1, (255, 255, 255))
    win.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    win.blit(birds_text, (10, 55))
    win.blit(gen_text, (10, 10))
    pygame.display.update()


def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)  # Creating the individual networks for each bird
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:  # Check which pipe the bird should look at
            if len(pipes) > 0 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # Add 0.1 to fitness for every frame its survives
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),
                                       abs(bird.y - pipes[pipe_ind].bottom)))  # Passing inputs into bird's network
            if output[0] > 0.5:  # Activation function returns a val between -1 and 1
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):  # Check for collision
                    ge[x].fitness -= 3  # Remove a point for colliding with pipe
                    birds.pop(x)  # Remove birds from population, they dead
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:  # Create new pipes
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # Remove pipes that are off the screen
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            for g in ge:
                g.fitness += 5  # Positive enforcement
            score += 1
            pipes.append(Pipe(600))
        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:  # Hit the floor or reach top of screen
                ge[x].fitness -= 1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, len(birds))


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)  # Creating the network

    p.add_reporter(neat.StdOutReporter(True))  # Used to output stats from the networks
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)  # Run the program for 50 generations where main is the fitness function


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
