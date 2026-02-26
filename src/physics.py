import pygame
import math

def handle_collision(obj1, obj2):
    """
    Handle elastic collision between two circular objects.
    Calculates new velocities based on momentum conservation.
    """
    dist_vec = obj1.pos - obj2.pos
    distance = dist_vec.length()
    
    if distance < obj1.radius + obj2.radius:
        # Prevent overlapping by moving objects apart
        overlap = (obj1.radius + obj2.radius) - distance
        separation_vec = dist_vec.normalize() * (overlap / 2)
        obj1.pos += separation_vec
        obj2.pos -= separation_vec
        
        # Physics: Elastic collision in 2D
        # Normal vector at collision
        normal = dist_vec.normalize()
        # Relative velocity
        rel_vel = obj1.velocity - obj2.velocity
        
        # Velocity component along the normal
        vel_along_normal = rel_vel.dot(normal)
        
        # Do not resolve if velocities are separating
        if vel_along_normal > 0:
            return

        # Restitution (1.0 = perfectly elastic)
        restitution = 0.8
        
        # Impulse scalar
        j = -(1 + restitution) * vel_along_normal
        j /= (1 / obj1.mass + 1 / obj2.mass)
        
        # Apply impulse
        impulse = j * normal
        obj1.velocity += impulse / obj1.mass
        obj2.velocity -= impulse / obj2.mass
        
        return True # Collision occurred
    return False
