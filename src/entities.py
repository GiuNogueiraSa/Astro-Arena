import pygame
import math
import random

class Bullet:
    def __init__(self, x, y, angle, speed, color, owner_type="player"):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.radius = 6
        self.color = color
        self.life = 2.0
        self.owner_type = owner_type

    def update(self, dt):
        self.pos += self.velocity * dt
        self.life -= dt

    def draw(self, screen, camera_offset):
        draw_pos = self.pos - camera_offset
        pygame.draw.circle(screen, self.color, (int(draw_pos.x), int(draw_pos.y)), self.radius + 4)
        pygame.draw.circle(screen, (255, 255, 255), (int(draw_pos.x), int(draw_pos.y)), self.radius)

class Item:
    def __init__(self, x, y, item_type):
        self.pos = pygame.Vector2(x, y)
        self.item_type = item_type # "REPAIR", "SHIELD", "WEAPON"
        self.radius = 20
        self.angle = 0
        self.color = (0, 255, 100) if item_type == "REPAIR" else (0, 100, 255) if item_type == "SHIELD" else (255, 200, 0)

    def update(self, dt):
        self.angle += 3 * dt

    def draw(self, screen, camera_offset):
        draw_pos = self.pos - camera_offset
        pts = []
        for i in range(4):
            a = self.angle + i * (math.pi/2)
            pts.append((draw_pos.x + math.cos(a)*18, draw_pos.y + math.sin(a)*18))
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
        
    def draw_ship(self, screen, points, camera_offset, show_hp=True, engine_count=1, cockpit_color=(255,200,50)):
        draw_pos = self.pos - camera_offset
        rotated_points = []
        for p in points:
            rx = p[0] * math.cos(self.angle) - p[1] * math.sin(self.angle)
            ry = p[0] * math.sin(self.angle) + p[1] * math.cos(self.angle)
            rotated_points.append((draw_pos.x + rx, draw_pos.y + ry))
        
        pygame.draw.polygon(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2), rotated_points, 0)
        pygame.draw.polygon(screen, (255, 255, 255), rotated_points, 2)
        
        cockpit_pos = draw_pos + pygame.Vector2(math.cos(self.angle), math.sin(self.angle)) * 10
        pygame.draw.circle(screen, cockpit_color, (int(cockpit_pos.x), int(cockpit_pos.y)), 6)
        
        if self.velocity.length() > 30:
            for i in range(engine_count):
                offset = (i - (engine_count-1)/2) * 15
                off_vec = pygame.Vector2(math.cos(self.angle + math.pi/2), math.sin(self.angle + math.pi/2)) * offset
                flare_pos = draw_pos - pygame.Vector2(math.cos(self.angle), math.sin(self.angle)) * (self.radius * 0.8) + off_vec
                flare_color = (100, 200, 255) if self.color[2] > 200 else (255, 100, 50)
                pygame.draw.circle(screen, flare_color, (int(flare_pos.x), int(flare_pos.y)), random.randint(6, 12))

        if show_hp:
            pygame.draw.rect(screen, (50, 0, 0), (draw_pos.x - 30, draw_pos.y - self.radius - 20, 60, 6))
            hp_w = max(0, (self.hp / self.max_hp) * 60)
            pygame.draw.rect(screen, (0, 255, 0), (draw_pos.x - 30, draw_pos.y - self.radius - 20, hp_w, 6))

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, radius=40, color=(30, 120, 255), mass=1.5, hp=150)
        self.speed = 3000
        self.shoot_cooldown = 0.0
        self.max_shoot_cooldown = 0.1
        self.shield = 100
        self.max_shield = 100
        self.weapon_level = 1
        
        self.points = [
            (50, 0), (10, -15), (5, -35), (-25, -40), (-15, -15), (-35, -20),
            (-20, 0), (-35, 20), (-15, 15), (-25, 40), (5, 35), (10, 15),
        ]
        
    def handle_input(self, keys, dt, mouse_pos, camera_offset):
        # Movement Input (WASD)
        move_dir = pygame.Vector2(0.0, 0.0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_dir.x += 1
        
        if move_dir.length() > 0:
            move_dir = move_dir.normalize()
            self.velocity += move_dir * (self.speed / self.mass) * dt

        # Orientation Input (Mouse Aim)
        # Mouse position relative to the world
        ship_screen_pos = self.pos - camera_offset
        mouse_vec = pygame.Vector2(mouse_pos) - ship_screen_pos
        if mouse_vec.length() > 0:
            target_angle = math.atan2(mouse_vec.y, mouse_vec.x)
            # Smoothly rotate to aim at mouse
            angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += angle_diff * 15 * dt

        # Shooting
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            
        if (keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]) and self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.max_shoot_cooldown
            bullets = []
            if self.weapon_level >= 1:
                bullets.append(Bullet(self.pos.x, self.pos.y, self.angle, 1300, (0, 255, 255), "player"))
            if self.weapon_level >= 2:
                off_x = 25 * math.cos(self.angle + math.pi/2)
                off_y = 25 * math.sin(self.angle + math.pi/2)
                bullets.append(Bullet(self.pos.x + off_x, self.pos.y + off_y, self.angle, 1300, (0, 255, 255), "player"))
                bullets.append(Bullet(self.pos.x - off_x, self.pos.y - off_y, self.angle, 1300, (0, 255, 255), "player"))
            return bullets
        return None

    def draw(self, screen, camera_offset):
        if self.shield > 0:
            draw_pos = self.pos - camera_offset
            pygame.draw.circle(screen, (0, 200, 255), (int(draw_pos.x), int(draw_pos.y)), self.radius + 12, 2)
        self.draw_ship(screen, self.points, camera_offset, engine_count=3, cockpit_color=(255, 200, 0))

class Enemy(Entity):
    def __init__(self, x, y, level=1):
        super().__init__(x, y, radius=35, color=(220, 40, 40), mass=1.2, hp=40 * level)
        self.level = level
        self.speed = 800 + level * 100
        self.shoot_cooldown = random.uniform(1, 3)
        self.max_shoot_cooldown = max(0.5, 2.0 - level * 0.3)
        
        self.points = [
            (35, 0), (15, -25), (-15, -35), (-30, -20), (-20, 0), (-30, 20),
            (-15, 35), (15, 25),
        ]
        
    def update_ai(self, target_pos, target_vel, dt):
        dir_vec = target_pos - self.pos
        dist = dir_vec.length()
        
        if dist > 0:
            dir_vec = dir_vec.normalize()
            # Movement AI: Mantém distância tática
            if dist > 450:
                self.velocity += dir_vec * (self.speed / self.mass) * dt
            elif dist < 350:
                self.velocity -= dir_vec * (self.speed / self.mass) * dt
            
            # Predictive Aiming: Aponta para onde o player vai estar
            prediction_factor = dist / 1300 # Tempo de voo da bala estimado
            aim_pos = target_pos + target_vel * prediction_factor
            aim_vec = aim_pos - self.pos
            self.angle = math.atan2(aim_vec.y, aim_vec.x)

        # Improved Shooting logic
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        elif dist < 800:
            self.shoot_cooldown = self.max_shoot_cooldown
            # Tiro levemente impreciso para o player ter chance
            aim_noise = random.uniform(-0.1, 0.1)
            return Bullet(self.pos.x, self.pos.y, self.angle + aim_noise, 850, (255, 50, 50), "enemy")
        return None

    def draw(self, screen, camera_offset):
        self.draw_ship(screen, self.points, camera_offset, engine_count=2, cockpit_color=(0, 255, 255))
