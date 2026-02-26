import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # TODO: Implementar base de entidades

class Player(Entity):
    def __init__(self):
        super().__init__()
        # TODO: Implementar jogador

class Enemy(Entity):
    def __init__(self):
        super().__init__()
        # TODO: Implementar inimigo
