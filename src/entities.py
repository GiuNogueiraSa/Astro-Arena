import pygame
import math
from src.physics import handle_collision

class Entity:
    def __init__(self, x, y, radius, color, mass=1.0):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius
        self.color = color
        self.mass = mass
        self.drag = 0.98 # Atmospheric/space drag to simulate inertia
        
    def update(self, dt):
        # Apply velocity
        self.pos += self.velocity * dt
        # Apply drag
        self.velocity *= self.drag
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))
        # Optional: Add a subtle glow or outline
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), int(self.radius), 2)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, radius=20, color=(100, 200, 255), mass=1.0)
        self.speed = 1500
        self.dash_speed = 4000
        self.dash_cooldown = 0
        self.max_dash_cooldown = 1.0 # seconds
        self.energy = 100
        
    def handle_input(self, keys, dt):
        move_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_dir.x += 1
        
        if move_dir.length() > 0:
            move_dir = move_dir.normalize()
            # Acceleration based on mass: a = F/m
            acceleration = (self.speed / self.mass) * dt
            self.velocity += move_dir * acceleration
            
        # Dash mechanic
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
            
        if keys[pygame.K_SPACE] and self.dash_cooldown <= 0:
            if move_dir.length() > 0:
                self.velocity += move_dir * (self.dash_speed / self.mass)
                self.dash_cooldown = self.max_dash_cooldown
                return True # Dash triggered
        return False

class Enemy(Entity):
    def __init__(self, x, y, radius=15):
        super().__init__(x, y, radius=radius, color=(255, 100, 100), mass=0.8)
        self.speed = 800
        
    def update_ai(self, target_pos, dt):
        # Simple chase AI
        dir_vec = target_pos - self.pos
        if dir_vec.length() > 0:
            dir_vec = dir_vec.normalize()
            acceleration = (self.speed / self.mass) * dt
            self.velocity += dir_vec * acceleration
        super().update(dt)
