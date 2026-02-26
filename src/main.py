import pygame
import asyncio
import math

# Inicialização do Pygame
async def main():
    pygame.init()
    
    # Configurações da tela
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Astro-Arena: Protótipo")
    
    # Cores
    SPACE_DARK = (10, 10, 25)
    PLAYER_COLOR = (0, 200, 255)
    GLOW_COLOR = (0, 100, 255)
    
    # Propriedades do Jogador
    x, y = WIDTH // 2, HEIGHT // 2
    radius = 20
    vel_x, vel_y = 0, 0
    acceleration = 0.5
    friction = 0.98
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    running = True
    while running:
        # 1. Entrada do Usuário
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vel_x -= acceleration
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vel_x += acceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vel_y -= acceleration
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vel_y += acceleration

        # 2. Física (Movimento e Inércia)
        x += vel_x
        y += vel_y
        
        # Aplicar fricção (inércia do espaço)
        vel_x *= friction
        vel_y *= friction

        # Borda elástica simplificada
        if x - radius < 0 or x + radius > WIDTH:
            vel_x *= -0.8
            x = max(radius, min(WIDTH - radius, x))
        if y - radius < 0 or y + radius > HEIGHT:
            vel_y *= -0.8
            y = max(radius, min(HEIGHT - radius, y))

        # 3. Desenho
        screen.fill(SPACE_DARK)
        
        # Efeito de brilho (Glow)
        for i in range(5):
            pygame.draw.circle(screen, GLOW_COLOR, (int(x), int(y)), radius + (i * 2), 1)
            
        # Círculo do jogador
        pygame.draw.circle(screen, PLAYER_COLOR, (int(x), int(y)), radius)
        
        # Instruções na tela
        img = font.render("Use WASD ou Setas para mover. Sinta a Inércia!", True, (255, 255, 255))
        screen.blit(img, (20, 20))

        pygame.display.flip()
        
        # 4. Controle de FPS e Async
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
