import pygame

def calculate_collision(entity1, entity2):
    """
    Calcula a colisão elástica simples entre duas entidades.
    """
    distance = entity1.pos.distance_to(entity2.pos)
    if distance < entity1.radius + entity2.radius:
        # Transferência de momento básica
        entity1.vel, entity2.vel = entity2.vel, entity1.vel
        return True
    return False

def apply_dash(entity, direction_vector):
    """
    Aplica uma força de arranque (dash).
    """
    dash_force = 15
    entity.vel += direction_vector * dash_force
