import pygame
import asyncio
import random
import sys
import math
from src.entities import Player, Enemy, Bullet
from src.physics import handle_collision, check_bullet_collision

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1024, 768
FPS = 60

# Colors
BG_DEEP = (3, 3, 10)
UI_ACCENT = (0, 255, 200)

class Star:
    def __init__(self):
        self.x = float(random.randint(0, WIDTH))
        self.y = float(random.randint(0, HEIGHT))
        self.size = random.uniform(0.5, 2.5)
        self.speed = self.size * 0.5
        self.brightness = random.randint(100, 255)

    def update(self, dt):
        self.y += self.speed * 60 * dt
        if self.y > HEIGHT:
            self.y = 0.0
            self.x = float(random.randint(0, WIDTH))

    def draw(self, screen):
        c = (self.brightness, self.brightness, 255)
        pygame.draw.circle(screen, c, (int(self.x), int(self.y)), int(self.size))

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-6, 6), random.uniform(-6, 6))
        self.life = 1.0
        self.color = color

    def update(self, dt):
        self.pos += self.vel * 60 * dt
        self.life -= 1.8 * dt

    def draw(self, screen):
        alpha = max(0, int(255 * self.life))
        # Surface with alpha for particles
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), 2)

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.is_hovered = False
        self.font = pygame.font.SysFont("Verdana, sans-serif", 28)

    def draw(self, screen):
        border_color = (255, 255, 255) if self.is_hovered else (80, 80, 100)
        thick = 3 if self.is_hovered else 1
        
        # Draw background
        pygame.draw.rect(screen, (20, 20, 40), self.rect, border_radius=8)
        # Draw border
        pygame.draw.rect(screen, border_color, self.rect, thick, border_radius=8)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "MENU"
        self.level = 1
        self.stars = [Star() for _ in range(120)]
        self.player = None
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.screen_shake = 0.0
        
        self.start_btn = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "INICIAR", (0, 120, 255))
        self.exit_btn = Button(WIDTH//2 - 100, HEIGHT//2 + 70, 200, 50, "SAIR", (200, 50, 50))
        
        self.font_huge = pygame.font.SysFont("Verdana", 72, bold=True)
        self.font_mid = pygame.font.SysFont("Verdana", 32)
        self.font_small = pygame.font.SysFont("Arial", 20)

    def reset_level(self, lv):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.enemies = [Enemy(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100), lv) for _ in range(1 + lv * 2)]
        self.bullets = []
        self.particles = []
        self.state = "PLAYING"
        self.level = lv

    async def run(self, clock):
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "MENU":
                        if self.start_btn.check_hover(mouse_pos):
                            self.reset_level(1)
                        if self.exit_btn.check_hover(mouse_pos):
                            running = False
                    elif self.state == "GAME_OVER" or self.state == "VICTORY":
                        self.state = "MENU"
                    elif self.state == "NEXT_LEVEL":
                        self.reset_level(self.level + 1)

            # Update Background
            for star in self.stars: star.update(dt)
            
            if self.state == "PLAYING" and self.player:
                keys = pygame.key.get_pressed()
                shot = self.player.handle_input(keys, dt)
                if shot:
                    self.bullets.append(shot)
                    self.screen_shake = 4.0
                
                self.player.update(dt)
                
                # Boundary wrap
                if self.player.pos.x < 0: self.player.pos.x = WIDTH
                if self.player.pos.x > WIDTH: self.player.pos.x = 0
                if self.player.pos.y < 0: self.player.pos.y = HEIGHT
                if self.player.pos.y > HEIGHT: self.player.pos.y = 0
                
                for enemy in self.enemies[:]:
                    enemy.update_ai(self.player.pos, dt)
                    if handle_collision(self.player, enemy):
                        self.screen_shake = 12.0
                    
                    for b in self.bullets[:]:
                        if check_bullet_collision(b, enemy):
                            enemy.hp -= 1
                            if b in self.bullets: self.bullets.remove(b)
                            self.screen_shake = 6.0
                            for _ in range(8):
                                self.particles.append(Particle(b.pos.x, b.pos.y, enemy.color))
                            
                            if enemy.hp <= 0:
                                if enemy in self.enemies: self.enemies.remove(enemy)
                                for _ in range(15):
                                    self.particles.append(Particle(enemy.pos.x, enemy.pos.y, (255, 255, 255)))
                
                for b in self.bullets[:]:
                    b.update(dt)
                    if b.life <= 0: self.bullets.remove(b)
                    
                if not self.enemies:
                    if self.level < 3:
                        self.state = "NEXT_LEVEL"
                    else:
                        self.state = "VICTORY"

            for p in self.particles[:]:
                p.update(dt)
                if p.life <= 0: self.particles.remove(p)

            # Render
            render_off = pygame.Vector2(0,0)
            if self.screen_shake > 0:
                render_off = pygame.Vector2(random.uniform(-self.screen_shake, self.screen_shake), random.uniform(-self.screen_shake, self.screen_shake))
                self.screen_shake *= 0.8
            
            self.screen.fill(BG_DEEP)
            for star in self.stars: star.draw(screen)
            
            if self.state == "MENU":
                title = self.font_huge.render("ASTRO ARENA", True, UI_ACCENT)
                self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
                self.start_btn.check_hover(mouse_pos)
                self.exit_btn.check_hover(mouse_pos)
                self.start_btn.draw(self.screen)
                self.exit_btn.draw(self.screen)
                
            elif self.state in ["PLAYING", "NEXT_LEVEL", "VICTORY"]:
                for p in self.particles: p.draw(self.screen)
                for b in self.bullets: b.draw(self.screen)
                if self.player: self.player.draw(self.screen)
                for e in self.enemies: e.draw(self.screen)
                
                # HUD
                lvl_surf = self.font_mid.render(f"FASE {self.level}", True, (255, 255, 255))
                self.screen.blit(lvl_surf, (20, 20))
                
                if self.level == 1:
                    inst = self.font_small.render("WASD: MOVER | ESPAÇO: ATIRAR", True, UI_ACCENT)
                    self.screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 40))

            if self.state == "NEXT_LEVEL":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0,0))
                txt = self.font_mid.render("COMPLETO!", True, (0, 255, 100))
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                sub = self.font_small.render("Clique para ir para a próxima fase", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 50))
                
            if self.state == "VICTORY":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                self.screen.blit(overlay, (0,0))
                txt = self.font_huge.render("CAMPEÃO!", True, UI_ACCENT)
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
                sub = self.font_small.render("Clique para voltar ao menu", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 80))

            pygame.display.flip()
            await asyncio.sleep(0)

async def main():
    global screen # Need global for pygbag/wasm simplicity sometimes
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🚀 Astro-Arena Battle")
    clock = pygame.time.Clock()
    game = Game(screen)
    await game.run(clock)

if __name__ == "__main__":
    asyncio.run(main())
