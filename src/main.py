import pygame
import asyncio

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Astro-Arena")
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((20, 20, 30))  # Cor de fundo escura (espaço)
        
        # TODO: Desenhar entidades
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # Obrigatório para o pygbag/web

if __name__ == "__main__":
    asyncio.run(main())
