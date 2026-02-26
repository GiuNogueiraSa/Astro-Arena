import pygame
import math
import random

class Bullet:
    def __init__(self, x, y, angle, speed, color, owner_type="player"):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.radius = 4
        self.color = color
        self.life = 2.0
        self.owner_type = owner_type

    def update(self, dt):
        self.pos += self.velocity * dt
        self.life -= dt

    def draw(self, screen, camera_offset):
        draw_pos = self.pos - camera_offset
        # Bullet glow
        pygame.draw.circle(screen, self.color, (int(draw_pos.x), int(draw_pos.y)), self.radius + 3)
        pygame.draw.circle(screen, (255, 255, 255), (int(draw_pos.x), int(draw_pos.y)), self.radius)

class Item:
    def __init__(self, x, y, item_type):
        self.pos = pygame.Vector2(x, y)
        self.item_type = item_type # "REPAIR", "SHIELD", "WEAPON"
        self.radius = 15
        self.angle = 0
        self.color = (0, 255, 100) if item_type == "REPAIR" else (0, 100, 255) if item_type == "SHIELD" else (255, 200, 0)

    def update(self, dt):
        self.angle += 3 * dt # Rotation effect

    def draw(self, screen, camera_offset):
        draw_pos = self.pos - camera_offset
        # Floating diamond shape
        pts = []
        for i in range(4):
            a = self.angle + i * (math.pi/2)
            pts.append((draw_pos.x + math.cos(a)*15, draw_pos.y + math.sin(a)*15))
        pygame.draw.polygon(screen, self.color, pts, 0)
        pygame.draw.polygon(screen, (255, 255, 255), pts, 2)

class Entity:
    def __init__(self, x, y, radius, color, mass=1.0, hp=100):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0.0, 0.0)
        self.radius = radius
        self.color = color
        self.mass = mass
        self.angle = 0.0
        self.drag = 0.97
        self.hp = hp
        self.max_hp = hp
        
    def update(self, dt):
        self.pos += self.velocity * dt
        self.velocity *= self.drag
        
    def draw_ship(self, screen, points, camera_offset, show_hp=True):
        draw_pos = self.pos - camera_offset
        rotated_points = []
        for p in points:
            rx = p[0] * math.cos(self.angle) - p[1] * math.sin(self.angle)
            ry = p[0] * math.sin(self.angle) + p[1] * math.cos(self.angle)
            rotated_points.append((draw_pos.x + rx, draw_pos.y + ry))
        
        pygame.draw.polygon(screen, self.color, rotated_points, 0)
        pygame.draw.polygon(screen, (255, 255, 255), rotated_points, 2)
        
        # Engine trails
        if self.velocity.length() > 20:
            flare_pos = draw_pos - pygame.Vector2(math.cos(self.angle), math.sin(self.angle)) * (self.radius * 0.8)
            pygame.draw.circle(screen, (255, 150, 50), (int(flare_pos.x), int(flare_pos.y)), random.randint(4, 9))

        if show_hp:
            # HP bar
            pygame.draw.rect(screen, (50, 0, 0), (draw_pos.x - 20, draw_pos.y - self.radius - 15, 40, 5))
            hp_w = (self.hp / self.max_hp) * 40
            pygame.draw.rect(screen, (0, 255, 0), (draw_pos.x - 20, draw_pos.y - self.radius - 15, hp_w, 5))

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, radius=25, color=(0, 100, 255), mass=1.2, hp=100)
        self.speed = 2500
        self.shoot_cooldown = 0.0
        self.max_shoot_cooldown = 0.12
        self.shield = 50
        self.max_shield = 100
        self.weapon_level = 1
        
        # Sleek Hero Ship Shape
        self.points = [
            (35, 0),    # Nose
            (5, -10),   # Cockpit L
            (-5, -25),  # Wing L tip
            (-20, -10), # Wing L back
            (-15, 0),   # Center back
            (-20, 10),  # Wing R back
            (-5, 25),   # Wing R tip
            (5, 10),    # Cockpit R
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
            # Smooth rotation
            target_angle = math.atan2(move_dir.y, move_dir.x)
            diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += diff * 10 * dt

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            
        if (keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]) and self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.max_shoot_cooldown
            # Multi-laser based on weapon level
            bullets = []
            if self.weapon_level >= 1:
                bullets.append(Bullet(self.pos.x, self.pos.y, self.angle, 1100, (0, 255, 255), "player"))
            if self.weapon_level >= 2:
                bullets.append(Bullet(self.pos.x, self.pos.y, self.angle - 0.1, 1100, (0, 255, 255), "player"))
                bullets.append(Bullet(self.pos.x, self.pos.y, self.angle + 0.1, 1100, (0, 255, 255), "player"))
            return bullets
        return None

    def draw(self, screen, camera_offset):
        if self.shield > 0:
            draw_pos = self.pos - camera_offset
            pygame.draw.circle(screen, (0, 150, 255), (int(draw_pos.x), int(draw_pos.y)), self.radius + 5, 2)
        self.draw_ship(screen, self.points, camera_offset)

class Enemy(Entity):
    def __init__(self, x, y, level=1):
        super().__init__(x, y, radius=22, color=(255, 50, 50), mass=1.0, hp=20 * level)
        self.level = level
        self.speed = 600 + level * 200
        self.shoot_cooldown = random.uniform(1, 3)
        self.max_shoot_cooldown = max(0.8, 2.5 - level * 0.5)
        
        # Aggressive Enemy Shape
        self.points = [
            (25, 0),
            (0, -20),
            (-15, -15),
            (-5, 0),
            (-15, 15),
            (0, 20)
        ]
        
    def update_ai(self, target_pos, dt):
        dir_vec = target_pos - self.pos
        dist = dir_vec.length()
        
        if dist > 0:
            dir_vec = dir_vec.normalize()
            # Enemies try to stay at a distance but keep rotating towards player
            if dist > 300:
                self.velocity += dir_vec * (self.speed / self.mass) * dt
            elif dist < 200:
                self.velocity -= dir_vec * (self.speed / self.mass) * dt
            
            self.angle = math.atan2(dir_vec.y, dir_vec.x)

        # Shooting AI
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        elif dist < 600:
            self.shoot_cooldown = self.max_shoot_cooldown
            return Bullet(self.pos.x, self.pos.y, self.angle, 700, (255, 100, 0), "enemy")
        return None

    def draw(self, screen, camera_offset):
        self.draw_ship(screen, self.points, camera_offset)
