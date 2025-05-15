import pygame
from setup.config import WIDTH, HEIGHT

class Player:
    def __init__(self, x, y, speed, images, direction=0):
        self.x = x
        self.y = y
        self.center_x = x + 23
        self.center_y = y + 24
        self.speed = speed
        self.images = images  # list of 4 animation frames
        self.direction = direction
        self.command = direction
        self.counter = 0
        self.flicker = False

    def move(self, turns):
        if self.direction == 0 and turns[0]:
            self.x += self.speed
        elif self.direction == 1 and turns[1]:
            self.x -= self.speed
        elif self.direction == 2 and turns[2]:
            self.y -= self.speed
        elif self.direction == 3 and turns[3]:
            self.y += self.speed
        self.center_x = self.x + 23
        self.center_y = self.y + 24

    def draw(self, screen):
        idx = self.counter // 5 % len(self.images)
        if self.direction == 0:
            screen.blit(self.images[idx], (self.x, self.y))
        elif self.direction == 1:
            screen.blit(pygame.transform.flip(self.images[idx], True, False), (self.x, self.y))
        elif self.direction == 2:
            screen.blit(pygame.transform.rotate(self.images[idx], 90), (self.x, self.y))
        elif self.direction == 3:
            screen.blit(pygame.transform.rotate(self.images[idx], 270), (self.x, self.y))

    def update_counter(self):
        if self.counter < 19:
            self.counter += 1
            if self.counter > 3:
                self.flicker = False
        else:
            self.counter = 0
            self.flicker = True

    def get_turns(self, level):
        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        num3 = 15
        turns = [False, False, False, False]  # right, left, up, down
        cx = self.center_x
        cy = self.center_y

        if 0 < cx // 30 < 29:
            if level[(cy - num3) // num1][cx // num2] < 3:
                turns[2] = True  # up
            if level[cy // num1][(cx - num3) // num2] < 3:
                turns[1] = True  # left
            if level[cy // num1][(cx + num3) // num2] < 3:
                turns[0] = True  # right
            if level[(cy + num3) // num1][cx // num2] < 3:
                turns[3] = True  # down

            if self.direction in (2, 3):
                if 12 <= cx % num2 <= 18:
                    if level[(cy + num3) // num1][cx // num2] < 3:
                        turns[3] = True
                    if level[(cy - num3) // num1][cx // num2] < 3:
                        turns[2] = True
                if 12 <= cy % num1 <= 18:
                    if level[cy // num1][(cx - num2) // num2] < 3:
                        turns[1] = True
                    if level[cy // num1][(cx + num2) // num2] < 3:
                        turns[0] = True

            if self.direction in (0, 1):
                if 12 <= cx % num2 <= 18:
                    if level[(cy + num3) // num1][cx // num2] < 3:
                        turns[3] = True
                    if level[(cy - num3) // num1][cx // num2] < 3:
                        turns[2] = True
                if 12 <= cy % num1 <= 18:
                    if level[cy // num1][(cx - num3) // num2] < 3:
                        turns[1] = True
                    if level[cy // num1][(cx + num3) // num2] < 3:
                        turns[0] = True
        else:
            turns[0] = True
            turns[1] = True

        return turns
