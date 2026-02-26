import pygame
import asyncio
import random
import sys
import math
from src.entities import Player, Enemy, Bullet, Item
from src.physics import handle_collision, check_bullet_collision

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1024, 768
WORLD_SIZE = 3000 # Map size for "exploration"
FPS = 60

# Colors
BG_DEEP = (2, 2, 8)
UI_ACCENT = (0, 255, 200)

class Star:
    def __init__(self):
        self.world_pos = pygame.Vector2(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))
        self.size = random.uniform(0.5, 3.0)
        self.parallax = self.size * 0.1 # Distance effect
        self.color = (random.randint(180, 255), random.randint(180, 255), 255)

    def draw(self, screen, camera_pos):
        # Calculate screen position based on parallax
        # The star moves slightly with camera
        draw_x = (self.world_pos.x - camera_pos.x * self.parallax) % WIDTH
        draw_y = (self.world_pos.y - camera_pos.y * self.parallax) % HEIGHT
        pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), int(self.size))

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
        self.life = 1.0
        self.color = color

    def update(self, dt):
        self.pos += self.vel * 60 * dt
        self.life -= 1.5 * dt

    def draw(self, screen, camera_offset):
        if self.life <= 0: return
        draw_pos = self.pos - camera_offset
        pygame.draw.circle(screen, self.color, (int(draw_pos.x), int(draw_pos.y)), 2)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "MENU"
        self.level = 1
        self.stars = [Star() for _ in range(250)]
        self.player = None
        self.enemies = []
        self.bullets = []
        self.items = []
        self.particles = []
        self.camera_pos = pygame.Vector2(0, 0)
        self.screen_shake = 0.0
        
        # Menu buttons
        self.font_h = pygame.font.SysFont("Verdana", 72, bold=True)
        self.font_m = pygame.font.SysFont("Verdana", 28)
        self.font_s = pygame.font.SysFont("Arial", 18)

    def spawn_item(self, x, y):
        itype = random.choice(["REPAIR", "SHIELD", "WEAPON"])
        self.items.append(Item(x, y, itype))

    def reset_level(self, lv):
        self.level = lv
        self.player = Player(WORLD_SIZE//2, WORLD_SIZE//2)
        # Spawn enemies in the world
        self.enemies = []
        for _ in range(3 + lv * 3):
            ex = random.randint(100, WORLD_SIZE-100)
            ey = random.randint(100, WORLD_SIZE-100)
            self.enemies.append(Enemy(ex, ey, lv))
        
        self.bullets = []
        self.items = []
        self.particles = []
        self.state = "PLAYING"

    async def run(self, clock):
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state in ["MENU", "GAME_OVER", "VICTORY"]:
                        self.reset_level(1)
                    elif self.state == "NEXT_LEVEL":
                        self.reset_level(self.level + 1)

            # Update loop
            if self.state == "PLAYING" and self.player:
                keys = pygame.key.get_pressed()
                # 1. Update Camera (Follow Player)
                target_cam = self.player.pos - pygame.Vector2(WIDTH//2, HEIGHT//2)
                self.camera_pos += (target_cam - self.camera_pos) * 5 * dt
                
                # 2. Player Input/Update
                shot_data = self.player.handle_input(keys, dt)
                if shot_data:
                    if isinstance(shot_data, list): self.bullets.extend(shot_data)
                    else: self.bullets.append(shot_data)
                    self.screen_shake = 3.0
                
                self.player.update(dt)
                # World Bounds
                self.player.pos.x = max(0, min(WORLD_SIZE, self.player.pos.x))
                self.player.pos.y = max(0, min(WORLD_SIZE, self.player.pos.y))
                
                # 3. Enemies
                for enemy in self.enemies[:]:
                    e_shot = enemy.update_ai(self.player.pos, dt)
                    if e_shot: self.bullets.append(e_shot)
                    
                    if handle_collision(self.player, enemy):
                        self.screen_shake = 10.0
                        damage = 10
                        if self.player.shield > 0: self.player.shield -= damage
                        else: self.player.hp -= damage
                        
                    # Bullets check
                    for b in self.bullets[:]:
                        if b.owner_type == "player" and check_bullet_collision(b, enemy):
                            enemy.hp -= 15
                            if b in self.bullets: self.bullets.remove(b)
                            self.screen_shake = 5.0
                            for _ in range(5): self.particles.append(Particle(b.pos.x, b.pos.y, enemy.color))
                            
                            if enemy.hp <= 0:
                                if enemy in self.enemies: self.enemies.remove(enemy)
                                if random.random() < 0.4: self.spawn_item(enemy.pos.x, enemy.pos.y)
                                for _ in range(15): self.particles.append(Particle(enemy.pos.x, enemy.pos.y, (255, 255, 255)))
                        
                        elif b.owner_type == "enemy" and check_bullet_collision(b, self.player):
                            if b in self.bullets: self.bullets.remove(b)
                            damage = 10
                            if self.player.shield > 0: self.player.shield -= damage
                            else: self.player.hp -= damage
                            self.screen_shake = 8.0
                            for _ in range(5): self.particles.append(Particle(self.player.pos.x, self.player.pos.y, (255, 0, 0)))

                # 4. Items
                for item in self.items[:]:
                    item.update(dt)
                    if (item.pos - self.player.pos).length() < self.player.radius + item.radius:
                        if item.item_type == "REPAIR": self.player.hp = min(self.player.max_hp, self.player.hp + 30)
                        elif item.item_type == "SHIELD": self.player.shield = min(self.player.max_shield, self.player.shield + 50)
                        elif item.item_type == "WEAPON": self.player.weapon_level = min(3, self.player.weapon_level + 1)
                        self.items.remove(item)

                # 5. General Updates
                for b in self.bullets[:]:
                    b.update(dt)
                    if b.life <= 0: self.bullets.remove(b)
                for p in self.particles[:]:
                    p.update(dt)
                    if p.life <= 0: self.particles.remove(p)
                    
                if self.player.hp <= 0: self.state = "GAME_OVER"
                if not self.enemies:
                    if self.level < 3: self.state = "NEXT_LEVEL"
                    else: self.state = "VICTORY"

            # DRAWING
            self.screen.fill(BG_DEEP)
            # Far background stars (parallax)
            for star in self.stars: star.draw(self.screen, self.camera_pos)
            
            # World Objects (apply camera offset)
            cam_off = self.camera_pos
            if self.screen_shake > 0:
                cam_off += pygame.Vector2(random.uniform(-self.screen_shake, self.screen_shake), random.uniform(-self.screen_shake, self.screen_shake))
                self.screen_shake *= 0.9

            if self.state != "MENU":
                for item in self.items: item.draw(self.screen, cam_off)
                for b in self.bullets: b.draw(self.screen, cam_off)
                for p in self.particles: p.draw(self.screen, cam_off)
                for e in self.enemies: e.draw(self.screen, cam_off)
                if self.player: self.player.draw(self.screen, cam_off)
                
                # DRAW WORLD BOUNDS
                bound_rect = pygame.Rect(-cam_off.x, -cam_off.y, WORLD_SIZE, WORLD_SIZE)
                pygame.draw.rect(self.screen, (30, 30, 50), bound_rect, 5)

                # HUD
                # HP Bar
                pygame.draw.rect(self.screen, (60, 0, 0), (30, HEIGHT - 60, 200, 20))
                hp_w = (self.player.hp / self.player.max_hp) * 200
                pygame.draw.rect(self.screen, (255, 0, 0), (30, HEIGHT - 60, hp_w, 20))
                # Shield Bar
                pygame.draw.rect(self.screen, (0, 30, 60), (30, HEIGHT - 35, 200, 10))
                sh_w = (self.player.shield / self.player.max_shield) * 200
                pygame.draw.rect(self.screen, (0, 150, 255), (30, HEIGHT - 35, sh_w, 10))
                
                lvl_txt = self.font_m.render(f"FASE {self.level} | ARMA: NV {self.player.weapon_level}", True, UI_ACCENT)
                self.screen.blit(lvl_txt, (30, 30))

            # Overlays
            if self.state == "MENU":
                title = self.font_h.render("ASTRO ARENA", True, UI_ACCENT)
                self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
                sub = self.font_m.render("CLIQUE PARA EXPLORAR O ESPAÇO", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 50))
                
            elif self.state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((100, 0, 0, 150))
                self.screen.blit(overlay, (0,0))
                txt = self.font_h.render("NAVE DESTRUÍDA", True, (255, 255, 255))
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                
            elif self.state == "VICTORY":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 50, 0, 150))
                self.screen.blit(overlay, (0,0))
                txt = self.font_h.render("GALAXY CLEAR!", True, UI_ACCENT)
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))

            pygame.display.flip()
            await asyncio.sleep(0)

async def main():
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🚀 Astro-Arena: Expedition")
    clock = pygame.time.Clock()
    game = Game(screen)
    await game.run(clock)

if __name__ == "__main__":
    asyncio.run(main())
