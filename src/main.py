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
WIDTH, HEIGHT = 1200, 800
WORLD_SIZE = 5000 
FPS = 60

# Colors
BG_DEEP = (4, 4, 10)
NEBULA_COLORS = [(25, 5, 45), (5, 25, 45), (40, 10, 35)]
UI_ACCENT = (0, 255, 200)

class Star:
    def __init__(self):
        self.world_pos = pygame.Vector2(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))
        self.size = random.uniform(0.5, 3.5)
        self.parallax = (self.size / 3.5) * 0.15 
        self.color = (random.randint(200, 255), random.randint(200, 255), 255)
        self.pulse = random.uniform(0, math.pi * 2)

    def draw(self, screen, camera_pos):
        draw_x = (self.world_pos.x - camera_pos.x * self.parallax) % WIDTH
        draw_y = (self.world_pos.y - camera_pos.y * self.parallax) % HEIGHT
        s = self.size + math.sin(pygame.time.get_ticks() * 0.005 + self.pulse) * 0.5
        pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), max(1, int(s)))

class NebulaCloud:
    def __init__(self):
        self.pos = pygame.Vector2(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))
        self.size = random.randint(400, 700)
        self.color = random.choice(NEBULA_COLORS)
        self.parallax = 0.03

    def draw(self, screen, camera_pos):
        draw_x = (self.pos.x - camera_pos.x * self.parallax) % (WIDTH + self.size) - self.size//2
        draw_y = (self.pos.y - camera_pos.y * self.parallax) % (HEIGHT + self.size) - self.size//2
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        for i in range(4):
            alpha = 12 - i * 3
            pygame.draw.circle(surf, (*self.color, alpha), (self.size//2, self.size//2), (self.size//2) - i * 50)
        screen.blit(surf, (draw_x, draw_y))

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-8, 8), random.uniform(-8, 8))
        self.life = 1.0
        self.color = color

    def update(self, dt):
        self.pos += self.vel * 60 * dt
        self.life -= 1.4 * dt

    def draw(self, screen, camera_offset):
        if self.life <= 0: return
        draw_pos = self.pos - camera_offset
        pygame.draw.circle(screen, self.color, (int(draw_pos.x), int(draw_pos.y)), random.randint(3, 5))

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "MENU"
        self.level = 1
        self.nebulae = [NebulaCloud() for _ in range(10)]
        self.stars = [Star() for _ in range(350)]
        self.player = None
        self.enemies = []
        self.bullets = []
        self.items = []
        self.particles = []
        self.camera_pos = pygame.Vector2(0, 0)
        self.screen_shake = 0.0
        
        self.font_title = pygame.font.SysFont("Verdana", 96, bold=True)
        self.font_ui = pygame.font.SysFont("Verdana", 28)
        self.font_instr = pygame.font.SysFont("Arial", 20)

    def draw_minimap(self):
        map_size = 180
        margin = 25
        map_rect = pygame.Rect(WIDTH - map_size - margin, margin, map_size, map_size)
        
        # Draw Map Background (Translucent)
        s = pygame.Surface((map_size, map_size), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 160), (0, 0, map_size, map_size), border_radius=10)
        pygame.draw.rect(s, (100, 100, 150, 200), (0, 0, map_size, map_size), 2, border_radius=10)
        self.screen.blit(s, (map_rect.x, map_rect.y))
        
        # Scale world to map
        scale = map_size / WORLD_SIZE
        
        # Player (Blue Dot)
        px, py = self.player.pos.x * scale, self.player.pos.y * scale
        pygame.draw.circle(self.screen, (0, 180, 255), (map_rect.x + int(px), map_rect.y + int(py)), 4)
        
        # Enemies (Red Dots)
        for e in self.enemies:
            ex, ey = e.pos.x * scale, e.pos.y * scale
            pygame.draw.circle(self.screen, (255, 50, 50), (map_rect.x + int(ex), map_rect.y + int(ey)), 3)
            
        # Items (Green/Yellow Dots)
        for i in self.items:
            ix, iy = i.pos.x * scale, i.pos.y * scale
            pygame.draw.circle(self.screen, (0, 255, 100), (map_rect.x + int(ix), map_rect.y + int(iy)), 2)

    def reset_level(self, lv):
        self.level = lv
        self.player = Player(WORLD_SIZE//2, WORLD_SIZE//2)
        self.enemies = []
        enemy_count = 4 + lv * 3
        for _ in range(enemy_count):
            ex, ey = random.randint(500, WORLD_SIZE-500), random.randint(500, WORLD_SIZE-500)
            while (pygame.Vector2(ex, ey) - self.player.pos).length() < 900:
                ex, ey = random.randint(500, WORLD_SIZE-500), random.randint(500, WORLD_SIZE-500)
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

            if self.state == "PLAYING" and self.player:
                keys = pygame.key.get_pressed()
                target_cam = self.player.pos - pygame.Vector2(WIDTH//2, HEIGHT//2)
                self.camera_pos += (target_cam - self.camera_pos) * 5 * dt
                
                # Update Player with Mouse Aiming
                shot_data = self.player.handle_input(keys, dt, mouse_pos, self.camera_pos)
                if shot_data:
                    self.bullets.extend(shot_data)
                    self.screen_shake = 4.0
                
                self.player.update(dt)
                self.player.pos.x = max(0, min(WORLD_SIZE, self.player.pos.x))
                self.player.pos.y = max(0, min(WORLD_SIZE, self.player.pos.y))
                
                for enemy in self.enemies[:]:
                    # Update Enemy AI (Bot improvement: leading shots)
                    e_shot = enemy.update_ai(self.player.pos, self.player.velocity, dt)
                    if e_shot: self.bullets.append(e_shot)
                    
                    if handle_collision(self.player, enemy):
                        self.screen_shake = 15.0
                        damage = 25
                        if self.player.shield > 0: self.player.shield -= damage
                        else: self.player.hp -= damage
                        
                    for b in self.bullets[:]:
                        if b.owner_type == "player" and check_bullet_collision(b, enemy):
                            enemy.hp -= 20
                            if b in self.bullets: self.bullets.remove(b)
                            self.screen_shake = 6.0
                            for _ in range(10): self.particles.append(Particle(b.pos.x, b.pos.y, enemy.color))
                            if enemy.hp <= 0:
                                if enemy in self.enemies: self.enemies.remove(enemy)
                                if random.random() < 0.6: 
                                    itype = random.choice(["REPAIR", "SHIELD", "WEAPON"])
                                    self.items.append(Item(enemy.pos.x, enemy.pos.y, itype))
                                for _ in range(25): self.particles.append(Particle(enemy.pos.x, enemy.pos.y, (255, 255, 255)))
                        
                        elif b.owner_type == "enemy" and check_bullet_collision(b, self.player):
                            if b in self.bullets: self.bullets.remove(b)
                            damage = 22
                            if self.player.shield > 0: self.player.shield -= damage
                            else: self.player.hp -= damage
                            self.screen_shake = 10.0
                            for _ in range(8): self.particles.append(Particle(self.player.pos.x, self.player.pos.y, (255, 100, 0)))

                for item in self.items[:]:
                    item.update(dt)
                    if (item.pos - self.player.pos).length() < self.player.radius + item.radius:
                        if item.item_type == "REPAIR": self.player.hp = min(self.player.max_hp, self.player.hp + 60)
                        elif item.item_type == "SHIELD": self.player.shield = min(self.player.max_shield, self.player.shield + 100)
                        elif item.item_type == "WEAPON": self.player.weapon_level = min(2, self.player.weapon_level + 1)
                        self.items.remove(item)

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
            for neb in self.nebulae: neb.draw(self.screen, self.camera_pos)
            for star in self.stars: star.draw(self.screen, self.camera_pos)
            
            cam_off = self.camera_pos
            if self.screen_shake > 0:
                cam_off += pygame.Vector2(random.uniform(-self.screen_shake, self.screen_shake), random.uniform(-self.screen_shake, self.screen_shake))
                self.screen_shake *= 0.88

            if self.state != "MENU":
                for item in self.items: item.draw(self.screen, cam_off)
                for b in self.bullets: b.draw(self.screen, cam_off)
                for p in self.particles: p.draw(self.screen, cam_off)
                for e in self.enemies: e.draw(self.screen, cam_off)
                if self.player: self.player.draw(self.screen, cam_off)
                
                # Minimap
                self.draw_minimap()
                
                # HUD
                pygame.draw.rect(self.screen, (40, 40, 60), (40, HEIGHT - 90, 300, 25), border_radius=12)
                hp_w = max(0, (self.player.hp / self.player.max_hp) * 300)
                if hp_w > 0: pygame.draw.rect(self.screen, (220, 40, 40), (40, HEIGHT - 90, hp_w, 25), border_radius=12)
                pygame.draw.rect(self.screen, (30, 30, 50), (40, HEIGHT - 55, 300, 12), border_radius=10)
                sh_w = max(0, (self.player.shield / self.player.max_shield) * 300)
                if sh_w > 0: pygame.draw.rect(self.screen, (40, 120, 255), (40, HEIGHT - 55, sh_w, 12), border_radius=10)
                lvl_txt = self.font_ui.render(f"SETOR {self.level} | LASER NV {self.player.weapon_level}", True, UI_ACCENT)
                self.screen.blit(lvl_txt, (40, 40))

                if self.level == 1 and self.state == "PLAYING":
                    s = pygame.Surface((500, 150), pygame.SRCALPHA)
                    pygame.draw.rect(s, (0, 0, 0, 170), (0, 0, 500, 150), border_radius=15)
                    self.screen.blit(s, (WIDTH//2 - 250, 60))
                    i1 = self.font_instr.render("MOVIMENTO: [W,A,S,D]", True, (255, 255, 255))
                    i2 = self.font_instr.render("MIRA E TIRO: [MOUSE]", True, UI_ACCENT)
                    i3 = self.font_instr.render("USE O MAPA NO CANTO PARA ACHAR OS INIMIGOS", True, (255, 255, 100))
                    self.screen.blit(i1, (WIDTH//2 - i1.get_width()//2, 80))
                    self.screen.blit(i2, (WIDTH//2 - i2.get_width()//2, 110))
                    self.screen.blit(i3, (WIDTH//2 - i3.get_width()//2, 140))

            if self.state == "MENU":
                title = self.font_title.render("ASTRO ARENA", True, UI_ACCENT)
                self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
                sub = self.font_ui.render("CLIQUE PARA INICIAR A MISSAO", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 80))
            elif self.state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((60, 0, 0, 180))
                self.screen.blit(overlay, (0,0))
                txt = self.font_title.render("NAVE ABATIDA", True, (255, 255, 255))
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
            elif self.state == "VICTORY":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 50, 100, 180))
                self.screen.blit(overlay, (0,0))
                txt = self.font_title.render("SETOR SEGURO!", True, UI_ACCENT)
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))

            pygame.display.flip()
            await asyncio.sleep(0)

async def main():
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🚀 Astro-Arena: Battle HUD")
    clock = pygame.time.Clock()
    game = Game(screen)
    await game.run(clock)

if __name__ == "__main__":
    asyncio.run(main())
