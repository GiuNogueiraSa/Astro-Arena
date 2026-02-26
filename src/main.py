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
WORLD_SIZE = 4000 # Increased world for larger ships
FPS = 60

# Colors
BG_DEEP = (2, 2, 8)
UI_ACCENT = (0, 255, 200)

class Star:
    def __init__(self):
        self.world_pos = pygame.Vector2(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))
        self.size = random.uniform(0.5, 4.0)
        self.parallax = self.size * 0.12 # Stronger parallax
        self.color = (random.randint(180, 255), random.randint(180, 255), 255)

    def draw(self, screen, camera_pos):
        draw_x = (self.world_pos.x - camera_pos.x * self.parallax) % WIDTH
        draw_y = (self.world_pos.y - camera_pos.y * self.parallax) % HEIGHT
        pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), int(self.size))

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-7, 7), random.uniform(-7, 7))
        self.life = 1.0
        self.color = color

    def update(self, dt):
        self.pos += self.vel * 60 * dt
        self.life -= 1.6 * dt

    def draw(self, screen, camera_offset):
        if self.life <= 0: return
        draw_pos = self.pos - camera_offset
        # Glowy particle
        pygame.draw.circle(screen, self.color, (int(draw_pos.x), int(draw_pos.y)), random.randint(2, 4))

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "MENU"
        self.level = 1
        self.stars = [Star() for _ in range(300)]
        self.player = None
        self.enemies = []
        self.bullets = []
        self.items = []
        self.particles = []
        self.camera_pos = pygame.Vector2(0, 0)
        self.screen_shake = 0.0
        
        self.font_h = pygame.font.SysFont("Verdana", 80, bold=True)
        self.font_m = pygame.font.SysFont("Verdana", 32)
        self.font_s = pygame.font.SysFont("Arial", 22)
        self.font_warn = pygame.font.SysFont("Verdana", 40, bold=True)

    def spawn_item(self, x, y):
        itype = random.choice(["REPAIR", "SHIELD", "WEAPON"])
        self.items.append(Item(x, y, itype))

    def reset_level(self, lv):
        self.level = lv
        self.player = Player(WORLD_SIZE//2, WORLD_SIZE//2)
        self.enemies = []
        # Fewer but larger, tougher enemies
        enemy_count = 2 + lv * 2
        for _ in range(enemy_count):
            ex, ey = random.randint(200, WORLD_SIZE-200), random.randint(200, WORLD_SIZE-200)
            # Don't spawn on player
            while (pygame.Vector2(ex, ey) - self.player.pos).length() < 500:
                ex, ey = random.randint(200, WORLD_SIZE-200), random.randint(200, WORLD_SIZE-200)
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
                self.camera_pos += (target_cam - self.camera_pos) * 6 * dt
                
                shot_data = self.player.handle_input(keys, dt)
                if shot_data:
                    self.bullets.extend(shot_data)
                    self.screen_shake = 4.0
                
                self.player.update(dt)
                self.player.pos.x = max(0, min(WORLD_SIZE, self.player.pos.x))
                self.player.pos.y = max(0, min(WORLD_SIZE, self.player.pos.y))
                
                for enemy in self.enemies[:]:
                    e_shot = enemy.update_ai(self.player.pos, dt)
                    if e_shot: self.bullets.append(e_shot)
                    
                    if handle_collision(self.player, enemy):
                        self.screen_shake = 15.0
                        damage = 15
                        if self.player.shield > 0: self.player.shield -= damage
                        else: self.player.hp -= damage
                        
                    for b in self.bullets[:]:
                        if b.owner_type == "player" and check_bullet_collision(b, enemy):
                            enemy.hp -= 15
                            if b in self.bullets: self.bullets.remove(b)
                            self.screen_shake = 6.0
                            for _ in range(8): self.particles.append(Particle(b.pos.x, b.pos.y, enemy.color))
                            if enemy.hp <= 0:
                                if enemy in self.enemies: self.enemies.remove(enemy)
                                if random.random() < 0.5: self.spawn_item(enemy.pos.x, enemy.pos.y)
                                for _ in range(25): self.particles.append(Particle(enemy.pos.x, enemy.pos.y, (255, 255, 255)))
                        
                        elif b.owner_type == "enemy" and check_bullet_collision(b, self.player):
                            if b in self.bullets: self.bullets.remove(b)
                            damage = 20
                            if self.player.shield > 0: self.player.shield -= damage
                            else: self.player.hp -= damage
                            self.screen_shake = 10.0
                            for _ in range(8): self.particles.append(Particle(self.player.pos.x, self.player.pos.y, (255, 0, 0)))

                for item in self.items[:]:
                    item.update(dt)
                    if (item.pos - self.player.pos).length() < self.player.radius + item.radius:
                        if item.item_type == "REPAIR": self.player.hp = min(self.player.max_hp, self.player.hp + 50)
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
            for star in self.stars: star.draw(self.screen, self.camera_pos)
            
            cam_off = self.camera_pos
            if self.screen_shake > 0:
                cam_off += pygame.Vector2(random.uniform(-self.screen_shake, self.screen_shake), random.uniform(-self.screen_shake, self.screen_shake))
                self.screen_shake *= 0.85

            if self.state != "MENU":
                for item in self.items: item.draw(self.screen, cam_off)
                for b in self.bullets: b.draw(self.screen, cam_off)
                for p in self.particles: p.draw(self.screen, cam_off)
                for e in self.enemies: e.draw(self.screen, cam_off)
                if self.player: self.player.draw(self.screen, cam_off)
                
                # HUD
                pygame.draw.rect(self.screen, (60, 0, 0), (30, HEIGHT - 80, 250, 25))
                hp_w = max(0, (self.player.hp / self.player.max_hp) * 250)
                pygame.draw.rect(self.screen, (255, 0, 0), (30, HEIGHT - 80, hp_w, 25))
                pygame.draw.rect(self.screen, (0, 30, 60), (30, HEIGHT - 45, 250, 15))
                sh_w = max(0, (self.player.shield / self.player.max_shield) * 250)
                pygame.draw.rect(self.screen, (0, 150, 255), (30, HEIGHT - 45, sh_w, 15))
                
                lvl_txt = self.font_m.render(f"FASE {self.level} | ARMAS NV {self.player.weapon_level}", True, UI_ACCENT)
                self.screen.blit(lvl_txt, (30, 30))

                # Instructions for Phase 1
                if self.level == 1 and self.state == "PLAYING":
                    overlay = pygame.Surface((400, 120), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 120))
                    self.screen.blit(overlay, (WIDTH//2 - 200, 50))
                    inst1 = self.font_s.render("PILOte com WASD / Setas", True, (255, 255, 255))
                    inst2 = self.font_s.render("ATIRE com ESPACO ou MOUSE", True, UI_ACCENT)
                    inst3 = self.font_s.render("Cuidado com as naves vermelhas!", True, (255, 100, 100))
                    self.screen.blit(inst1, (WIDTH//2 - inst1.get_width()//2, 60))
                    self.screen.blit(inst2, (WIDTH//2 - inst2.get_width()//2, 90))
                    self.screen.blit(inst3, (WIDTH//2 - inst3.get_width()//2, 120))

            if self.state == "MENU":
                title = self.font_h.render("ASTRO ARENA", True, UI_ACCENT)
                self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
                sub = self.font_m.render("CLIQUE PARA INICIAR A MISSAO", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 50))
                
            elif self.state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((100, 0, 0, 160))
                self.screen.blit(overlay, (0,0))
                txt = self.font_h.render("MISSAO FALHOU", True, (255, 255, 255))
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                sub = self.font_m.render("CLIQUE PARA RECOMECAR", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 80))
                
            elif self.state == "VICTORY":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 100, 200, 140))
                self.screen.blit(overlay, (0,0))
                txt = self.font_h.render("VITORIA TOTAL!", True, UI_ACCENT)
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                sub = self.font_m.render("CLIQUE PARA O MENU", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 80))

            pygame.display.flip()
            await asyncio.sleep(0)

async def main():
    global screen
    # Use default flags for better performance
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🚀 Astro-Arena: Battle Edition")
    clock = pygame.time.Clock()
    game = Game(screen)
    await game.run(clock)

if __name__ == "__main__":
    asyncio.run(main())
