import pygame
import math
import random

class Bullet:
    def __init__(self, x, y, angle, speed, color):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.radius = 4
        self.color = color
        self.life = 1.2 # seconds

    def update(self, dt):
        self.pos += self.velocity * dt
        self.life -= dt

    def draw(self, screen):
        # Glow effect
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius + 2)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.radius)

class Entity:
    def __init__(self, x, y, radius, color, mass=1.0):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0.0, 0.0)
        self.radius = radius
        self.color = color
        self.mass = mass
        self.angle = 0.0 # Radians
        self.drag = 0.96
        
    def update(self, dt):
        self.pos += self.velocity * dt
        self.velocity *= self.drag
        
    def draw_ship(self, screen, points):
        rotated_points = []
        for p in points:
            # Scale point for radius
            px, py = p[0], p[1]
            rx = px * math.cos(self.angle) - py * math.sin(self.angle)
            ry = px * math.sin(self.angle) + py * math.cos(self.angle)
            rotated_points.append((self.pos.x + rx, self.pos.y + ry))
        
        # Ship body
        pygame.draw.polygon(screen, self.color, rotated_points, 0)
        # Glowing border
        pygame.draw.polygon(screen, (255, 255, 255), rotated_points, 2)
        
        # Engine flare if moving fast
        if self.velocity.length() > 50:
            flare_pos = self.pos - pygame.Vector2(math.cos(self.angle), math.sin(self.angle)) * 15
            pygame.draw.circle(screen, (255, 200, 50), (int(flare_pos.x), int(flare_pos.y)), random.randint(3, 7))

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, radius=20, color=(0, 150, 255), mass=1.0)
        self.speed = 2200
        self.shoot_cooldown = 0.0
        self.max_shoot_cooldown = 0.15
        self.side = 1 # Toggle between left/right compartment
        self.points = [
            (25, 0),    # Nose
            (-15, -18), # Wing L
            (-5, 0),    # Back
            (-15, 18)   # Wing R
        ]
        
    def handle_input(self, keys, dt):
        move_dir = pygame.Vector2(0.0, 0.0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_dir.x += 1
        
        if move_dir.length() > 0:
            move_dir = move_dir.normalize()
            self.velocity += move_dir * (self.speed / self.mass) * dt
            # Rotate
            target_angle = math.atan2(move_dir.y, move_dir.x)
            diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += diff * 12 * dt

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            
        if (keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]) and self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.max_shoot_cooldown
            # Alternating compartments
            offset_y = 12 * self.side
            self.side *= -1
            # Rotate the offset relative to ship angle
            off_x = offset_y * -math.sin(self.angle)
            off_y = offset_y * math.cos(self.angle)
            
            return Bullet(self.pos.x + off_x, self.pos.y + off_y, 
                          self.angle, 950, (0, 255, 255))
        return None

    def draw(self, screen):
        self.draw_ship(screen, self.points)

class Enemy(Entity):
    def __init__(self, x, y, level=1):
        color = (255, 50, 50) if level == 1 else (200, 50, 255) if level == 2 else (255, 180, 0)
        radius = 15 + level * 3
        super().__init__(x, y, radius=radius, color=color, mass=0.6 + level * 0.3)
        self.speed = 500 + level * 250
        self.hp = level
        self.points = [
            (18, 0),
            (-15, -15),
            (-8, 0),
            (-15, 15)
        ]
        
    def update_ai(self, target_pos, dt):
        dir_vec = target_pos - self.pos
        if dir_vec.length() > 0:
            dir_vec = dir_vec.normalize()
            self.velocity += dir_vec * (self.speed / self.mass) * dt
            self.angle = math.atan2(dir_vec.y, dir_vec.x)
        super().update(dt)

    def draw(self, screen):
        self.draw_ship(screen, self.points)
