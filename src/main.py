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
        self.color = (random.randint(200, 240), random.randint(220, 255), 255)
        self.pulse = random.uniform(0, math.pi * 2)

    def draw(self, screen, camera_pos):
        # Improved parallax and loop
        draw_x = (self.world_pos.x - camera_pos.x * self.parallax) % WIDTH
        draw_y = (self.world_pos.y - camera_pos.y * self.parallax) % HEIGHT
        s = self.size + math.sin(pygame.time.get_ticks() * 0.005 + self.pulse) * 0.5
        pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), max(1, int(s)))

class NebulaCloud:
    def __init__(self, level=1):
        self.pos = pygame.Vector2(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))
        self.size = random.randint(600, 1000)
        # Evolution: Colors change with universe exploration
        if level == 1: self.color = random.choice([(25, 5, 45), (5, 25, 45)])
        elif level == 2: self.color = random.choice([(45, 10, 15), (40, 30, 10)])
        else: self.color = random.choice([(10, 40, 30), (5, 15, 45)])
        
        self.parallax = 0.04
        self.surf = self._create_surf()

    def _create_surf(self):
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        for i in range(6):
            alpha = 10 - i * 1.5
            pygame.draw.circle(surf, (*self.color, int(alpha)), (self.size//2, self.size//2), (self.size//2) - i * 60)
        return surf

    def draw(self, screen, camera_pos):
        draw_x = (self.pos.x - camera_pos.x * self.parallax) % (WIDTH + self.size) - self.size//2
        draw_y = (self.pos.y - camera_pos.y * self.parallax) % (HEIGHT + self.size) - self.size//2
        screen.blit(self.surf, (draw_x, draw_y))

class SpaceDust:
    def __init__(self):
        self.pos = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.vel = pygame.Vector2(random.uniform(-10, -5), random.uniform(-2, 2))
        self.size = random.randint(1, 3)
        self.color = (150, 150, 200, 100)

    def update(self, dt):
        self.pos += self.vel * dt * 10
        if self.pos.x < -10: self.pos.x = WIDTH + 10
        if self.pos.y < -10: self.pos.y = HEIGHT + 10
        if self.pos.y > HEIGHT + 10: self.pos.y = -10

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.size)

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
        self.nebulae = []
        self.stars = [Star() for _ in range(400)]
        self.dust = [SpaceDust() for _ in range(40)]
        self.player = None
        self.enemies = []
        self.bullets = []
        self.items = []
        self.particles = []
        self.camera_pos = pygame.Vector2(0, 0)
        self.screen_shake = 0.0
        
        # Seçores (Universe exploration colors)
        self.bg_colors = [(4, 4, 15), (15, 5, 5), (5, 12, 10)]
        
        # Asset Loading
        self.pilots_img = pygame.image.load("assets/pilots.png").convert_alpha()
        self.ships_img = pygame.image.load("assets/ships.png").convert_alpha()
        self.earth_img = pygame.image.load("assets/earth.png").convert_alpha()
        
        self.selected_pilot = 0
        self.selected_ship = 0
        self.unlocked_skins = [0] # List of pilot indices unlocked
        
        self.font_title = pygame.font.SysFont("Verdana", 96, bold=True)
        self.font_ui = pygame.font.SysFont("Verdana", 28)
        self.font_instr = pygame.font.SysFont("Arial", 22)
        self.font_story = pygame.font.SysFont("Georgia", 24, italic=True)
        
        self.story_index = 0
        self.story_texts = [
            "Um astronauta sai da Terra para explorar...",
            "Mas algo deu errado no hiperespaço.",
            "O grupo se perdeu, e você ficou para trás.",
            "Agora, cercado por naves hostis...",
            "Sua única missão é voltar para casa: O Planeta Terra."
        ]
        self.story_timer = 0
        
        # Pre-render Story Surfaces
        self.story_surfs = [self.font_story.render(txt, True, (200, 200, 255)) for txt in self.story_texts]
        
        # Pre-scale Selection Assets
        self.pilot_previews = []
        pw = self.pilots_img.get_width() // 3
        ph = self.pilots_img.get_height()
        for i in range(3):
            p_rect = pygame.Rect(i * pw, 0, pw, ph)
            self.pilot_previews.append(pygame.transform.scale(self.pilots_img.subsurface(p_rect), (240, 240)))
            
        self.ship_previews = []
        sw = self.ships_img.get_width() // 3
        sh = self.ships_img.get_height()
        for i in range(3):
            s_rect = pygame.Rect(i * sw, 0, sw, sh)
            self.ship_previews.append(pygame.transform.scale(self.ships_img.subsurface(s_rect), (180, 140)))
            
        # UI Pre-renders
        self.ui_title = self.font_title.render("ASTRO ARENA", True, UI_ACCENT)
        self.ui_prompt_cont = self.font_ui.render("[CLIQUE PARA CONTINUAR]", True, UI_ACCENT)
        self.ui_header1 = self.font_ui.render("ESCOLHA SEU PILOTO", True, UI_ACCENT)
        self.ui_header2 = self.font_ui.render("ESCOLHA SUA NAVE", True, UI_ACCENT)
        self.ui_btn_mission = self.font_ui.render("INICIAR MISSÃO", True, (0, 0, 0))
        self.ui_lock = self.font_ui.render("BLOQUEADO", True, (200, 50, 50))
        
        # Static Overlays
        self.overlay_story = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay_story.fill((0, 0, 0, 230))
        self.overlay_selection = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay_selection.fill((10, 10, 30, 220))
        self.overlay_dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay_dark.fill((0, 0, 0, 200))

        self.init_background(1)

    def init_background(self, lv):
        self.nebulae = [NebulaCloud(lv) for _ in range(12)]

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
        self.init_background(lv)
        # Unlock new pilot skin on level 2 and 3
        if lv == 2 and 1 not in self.unlocked_skins: self.unlocked_skins.append(1)
        if lv == 3 and 2 not in self.unlocked_skins: self.unlocked_skins.append(2)
        
        self.player = Player(WORLD_SIZE//2, WORLD_SIZE//2, self.selected_ship)
        self.enemies = []
        enemy_count = 5 + lv * 4
        for _ in range(enemy_count):
            ex, ey = random.randint(500, WORLD_SIZE-500), random.randint(500, WORLD_SIZE-500)
            while (pygame.Vector2(ex, ey) - self.player.pos).length() < 1200:
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
                    if self.state == "MENU":
                        self.state = "STORY"
                        self.story_index = 0
                        self.story_timer = 0
                    elif self.state == "STORY":
                        self.story_index += 1
                        self.story_timer = 0
                        if self.story_index >= len(self.story_texts):
                            self.state = "SELECTION"
                    elif self.state == "SELECTION":
                        # UI Click detection for pilots/ships
                        mx, my = event.pos
                        if 100 < my < 350: # Pilot selection row
                            if 100 < mx < 350: self.selected_pilot = 0
                            elif 450 < mx < 700: self.selected_pilot = 1
                            elif 800 < mx < 1050: self.selected_pilot = 2
                        elif 450 < my < 650: # Ship selection row
                            if 100 < mx < 350: self.selected_ship = 0
                            elif 450 < mx < 700: self.selected_ship = 1
                            elif 800 < mx < 1050: self.selected_ship = 2
                        elif my > 680: # Start Button
                            if WIDTH//2 - 150 < mx < WIDTH//2 + 150:
                                self.reset_level(1)
                    elif self.state in ["GAME_OVER", "VICTORY"]:
                        self.state = "MENU"
                    elif self.state == "NEXT_LEVEL":
                        # Start button or Change Skin
                        mx, my = event.pos
                        if WIDTH//2 - 150 < mx < WIDTH//2 + 150:
                            if 620 < my < 690:
                                self.reset_level(self.level + 1)
                            elif 710 < my < 770:
                                self.state = "SELECTION"

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
                for d in self.dust:
                    d.update(dt)
                    
                if self.player.hp <= 0: self.state = "GAME_OVER"
                if not self.enemies:
                    if self.level < 3: self.state = "NEXT_LEVEL"
                    else: self.state = "VICTORY"

            # DRAWING
            self.screen.fill(self.bg_colors[self.level-1])
            for neb in self.nebulae: neb.draw(self.screen, self.camera_pos)
            
            # Level 3 Special: Earth in background
            if self.level == 3:
                e_pos = pygame.Vector2(500, 200) - self.camera_pos * 0.02
                self.screen.blit(self.earth_img, (e_pos.x, e_pos.y))
                
            for star in self.stars: star.draw(self.screen, self.camera_pos)
            for d in self.dust: d.draw(self.screen)
            
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
                self.screen.blit(self.ui_title, (WIDTH//2 - self.ui_title.get_width()//2, HEIGHT//3))
                glow = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 100 + 155
                sub = self.font_ui.render("CLIQUE PARA INICIAR A MISSÃO", True, (glow, glow, glow))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 80))
            
            elif self.state == "STORY":
                self.screen.blit(self.overlay_story, (0,0))
                for i in range(self.story_index + 1):
                    alpha = 255 if i < self.story_index else min(255, self.story_timer * 8)
                    surf = self.story_surfs[i].copy()
                    surf.set_alpha(alpha)
                    self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, 200 + i * 60))
                
                self.story_timer += 1
                prompt = self.ui_prompt_cont.copy()
                prompt.set_alpha(150 + int(math.sin(pygame.time.get_ticks() * 0.005) * 100))
                self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 100))

            elif self.state == "SELECTION":
                self.screen.blit(self.overlay_selection, (0,0))
                self.screen.blit(self.ui_header1, (WIDTH//2 - self.ui_header1.get_width()//2, 50))
                
                for i in range(3):
                    rect = pygame.Rect(100 + i * 350, 100, 250, 250)
                    color = UI_ACCENT if self.selected_pilot == i else (50, 50, 80)
                    pygame.draw.rect(self.screen, color, rect, 3 if self.selected_pilot == i else 1, border_radius=15)
                    self.screen.blit(self.pilot_previews[i], (rect.x + 5, rect.y + 5))
                    
                    if i not in self.unlocked_skins:
                        block = pygame.Surface((250, 250), pygame.SRCALPHA)
                        block.fill((0, 0, 0, 180))
                        self.screen.blit(block, rect.topleft)
                        self.screen.blit(self.ui_lock, (rect.centerx - self.ui_lock.get_width()//2, rect.centery - 15))

                self.screen.blit(self.ui_header2, (WIDTH//2 - self.ui_header2.get_width()//2, 400))
                for i in range(3):
                    rect = pygame.Rect(100 + i * 350, 450, 250, 200)
                    color = UI_ACCENT if self.selected_ship == i else (50, 50, 80)
                    pygame.draw.rect(self.screen, color, rect, 3 if self.selected_ship == i else 1, border_radius=15)
                    self.screen.blit(self.ship_previews[i], (rect.centerx - 90, rect.centery - 70))

                btn_rect = pygame.Rect(WIDTH//2 - 150, 700, 300, 60)
                pygame.draw.rect(self.screen, UI_ACCENT, btn_rect, border_radius=30)
                self.screen.blit(self.ui_btn_mission, (btn_rect.centerx - self.ui_btn_mission.get_width()//2, btn_rect.centery - 18))

            elif self.state == "NEXT_LEVEL":
                self.screen.blit(self.overlay_dark, (0,0))
                txt = self.font_title.render(f"SETOR {self.level} LIMPO", True, UI_ACCENT)
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 100))
                
                # Pre-scaled pilot info
                p_img = pygame.transform.scale(self.pilot_previews[self.selected_pilot], (300, 300))
                self.screen.blit(p_img, (WIDTH//2 - 150, 220))
                
                info = self.font_ui.render(f"PILOTO {self.selected_pilot + 1} PRONTO", True, (255, 255, 255))
                self.screen.blit(info, (WIDTH//2 - info.get_width()//2, 540))
                
                if self.level + 1 <= 3:
                    btn_rect = pygame.Rect(WIDTH//2 - 150, 620, 300, 70)
                    pygame.draw.rect(self.screen, (0, 255, 100), btn_rect, border_radius=35)
                    btn_txt = self.font_ui.render("INICIAR FASE", True, (0, 0, 0))
                    self.screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - 18))
                    
                    skin_btn = pygame.Rect(WIDTH//2 - 150, 710, 300, 60)
                    pygame.draw.rect(self.screen, (100, 100, 200), skin_btn, border_radius=30)
                    skin_txt = self.font_ui.render("TROCAR SKIN", True, (255, 255, 255))
                    self.screen.blit(skin_txt, (skin_btn.centerx - skin_txt.get_width()//2, skin_btn.centery - 18))

            elif self.state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((60, 0, 0, 180))
                self.screen.blit(overlay, (0,0))
                txt = self.font_title.render("NAVE ABATIDA", True, (255, 255, 255))
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
                sub = self.font_ui.render("CLIQUE PARA VOLTAR AO MENU", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 50))

            elif self.state == "VICTORY":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 50, 100, 180))
                self.screen.blit(overlay, (0,0))
                txt = self.font_title.render("TERRA À VISTA!", True, UI_ACCENT)
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//3))
                
                msg = self.font_story.render("Você conseguiu voltar para casa.", True, (255, 255, 255))
                self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
                
                sub = self.font_ui.render("CLIQUE PARA RECOMECAR", True, (255, 255, 255))
                self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT - 150))

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
