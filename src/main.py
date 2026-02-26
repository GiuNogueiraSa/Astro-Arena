import pygame
import asyncio
import random
import sys
from src.entities import Player, Enemy
from src.physics import handle_collision

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BG_COLOR = (15, 15, 25)
ARENA_COLOR = (30, 30, 45)

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
        self.life = 1.0
        self.color = color

    def update(self, dt):
        self.pos += self.vel * 60 * dt
        self.life -= 2.0 * dt

    def draw(self, screen):
        val = int(255 * self.life)
        if val > 0:
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), 2)

async def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🚀 Astro-Arena")
    clock = pygame.time.Clock()
    
    player = Player(WIDTH // 2, HEIGHT // 2)
    enemies = [Enemy(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)) for _ in range(3)]
    particles = []
    
    screen_shake = 0
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Update
        keys = pygame.key.get_pressed()
        dashed = player.handle_input(keys, dt)
        if dashed:
            screen_shake = 10
            # Add trail particles
            for _ in range(10):
                particles.append(Particle(player.pos.x, player.pos.y, player.color))
        
        player.update(dt)
        
        for enemy in enemies:
            enemy.update_ai(player.pos, dt)
            if handle_collision(player, enemy):
                screen_shake = 15
                # Collision particles
                for _ in range(15):
                    particles.append(Particle((player.pos.x + enemy.pos.x)/2, (player.pos.y + enemy.pos.y)/2, (255, 255, 100)))

        # Boundary checks (Bordas elásticas conforme doc)
        for ent in [player] + enemies:
            if ent.pos.x < ent.radius:
                ent.pos.x = ent.radius
                ent.velocity.x *= -0.8
            elif ent.pos.x > WIDTH - ent.radius:
                ent.pos.x = WIDTH - ent.radius
                ent.velocity.x *= -0.8
            if ent.pos.y < ent.radius:
                ent.pos.y = ent.radius
                ent.velocity.y *= -0.8
            elif ent.pos.y > HEIGHT - ent.radius:
                ent.pos.y = HEIGHT - ent.radius
                ent.velocity.y *= -0.8
        
        # Update particles
        for p in particles[:]:
            p.update(dt)
            if p.life <= 0:
                particles.remove(p)
                
        # Draw
        render_offset = pygame.Vector2(0, 0)
        if screen_shake > 0:
            render_offset = pygame.Vector2(random.uniform(-screen_shake, screen_shake), random.uniform(-screen_shake, screen_shake))
            screen_shake -= 1
            
        screen.fill(BG_COLOR)
        
        # Draw Arena
        pygame.draw.rect(screen, ARENA_COLOR, (0, 0, WIDTH, HEIGHT), 5)
        
        # Draw everything with offset
        for p in particles:
            p.draw(screen)
            
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
            
        # Draw UI (Dash cooldown)
        if player.dash_cooldown > 0:
            pygame.draw.arc(screen, (255,255,255), (player.pos.x - 25, player.pos.y - 25, 50, 50), 0, (player.dash_cooldown / player.max_dash_cooldown) * 2 * 3.14, 3)

        pygame.display.flip()
        
        # Pygbag requirement: yield control to the browser
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
