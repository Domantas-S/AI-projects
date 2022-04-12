import pygame
import neat
import time
import random
import os

pygame.font.init()

SCREEN_WIDTH = 576
SCREEN_HEIGHT = 800
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
    GAP = 200
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


def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMAGE, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    bird.draw(win)
    base.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()


def ending_screen(win):
    while True:
        the_end = [STAT_FONT.render("You lost", 1, (255, 255, 255)),
                   STAT_FONT.render("Press space to retry", 1, (255, 255, 255))]
        win.blit(the_end[0], (SCREEN_WIDTH // 2 - the_end[0].get_width() // 2, -100 + SCREEN_HEIGHT // 2))
        win.blit(the_end[1],
                 (SCREEN_WIDTH // 2 - the_end[1].get_width() // 2, -100 + the_end[0].get_height() + SCREEN_HEIGHT // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main(False)


def main(first):
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    while first:
        draw_window(win, bird, pipes, base, score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
                    first = False
        welcome = STAT_FONT.render("Fappy Bird", 1, (255, 255, 255))
        win.blit(welcome, (SCREEN_WIDTH // 2 - welcome.get_width() // 2, -100 + SCREEN_HEIGHT // 2))
        pygame.display.update()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird):  # Check for collision
                ending_screen(win)

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # Remove pipes that are off the screen
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:  # Create new pipes
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730:  # Hit the floor
            ending_screen(win)

        base.move()
        bird.move()
        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()


main(True)
