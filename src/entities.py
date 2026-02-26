import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.radius = radius
        self.color = color

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 20, (0, 200, 255))
        self.acceleration = 0.5
        self.friction = 0.98

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 15, (255, 50, 50))
        self.speed = 2
