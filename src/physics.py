import pygame
import math
import random

def handle_collision(obj1, obj2):
    """
    Handle elastic collision between two circular objects.
    """
    dist_vec = obj1.pos - obj2.pos
    distance = dist_vec.length()
    
    if distance < obj1.radius + obj2.radius:
        # Prevent overlapping
        overlap = (obj1.radius + obj2.radius) - distance
        if distance > 0:
            separation_vec = dist_vec.normalize() * (overlap / 2)
            obj1.pos += separation_vec
            obj2.pos -= separation_vec
            
            # Physics: Elastic collision
            normal = dist_vec.normalize()
            rel_vel = obj1.velocity - obj2.velocity
            vel_along_normal = rel_vel.dot(normal)
            
            if vel_along_normal > 0: return False

            restitution = 0.6
            j = -(1 + restitution) * vel_along_normal
            j /= (1 / obj1.mass + 1 / obj2.mass)
            
            impulse = j * normal
            obj1.velocity += impulse / obj1.mass
            obj2.velocity -= impulse / obj2.mass
            return True
    return False

def check_bullet_collision(bullet, entity):
    dist = (bullet.pos - entity.pos).length()
    return dist < entity.radius
