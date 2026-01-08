import pygame
import numpy as np
import random

# --- SETTINGS ---
WIDTH = 1000
HEIGHT = 700
FPS = 60

# Default Counts (Start high!)
NUM_BOIDS = 800 

# Physics Constants
MAX_SPEED = 6.0
MAX_FORCE = 0.15
PERCEPTION_RADIUS = 60
SEPARATION_DISTANCE = 30

# Colors
BLACK = (10, 10, 20)
CYAN = (0, 255, 255)
WHITE = (220, 220, 220)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
GREY = (100, 100, 100)

# Simulation State
SIM_SETTINGS = {
    "separation": True,
    "alignment": True,
    "cohesion": True,
    "mouse_mode": 0, # 0=None, 1=Follow, 2=Scare
    "simple_view": True, # Default to True for performance
    "paused": False
}

def init_boids(num):
    # Create huge tables of data
    pos = np.random.rand(num, 2) * [WIDTH, HEIGHT]
    vel = (np.random.rand(num, 2) - 0.5) * MAX_SPEED
    acc = np.zeros((num, 2))
    return pos, vel, acc

def update_boids(pos, vel, mouse_pos):
    num = len(pos)
    
    # 1. PREPARE DISTANCES (The Heavy Lifting)
    # This creates a matrix of vector differences
    diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    dist_sq = np.sum(diff**2, axis=2)
    
    # Masks (Who is close?)
    # We ignore self (identity matrix) by setting diagonal to infinity
    np.fill_diagonal(dist_sq, np.inf)
    
    radius_sq = PERCEPTION_RADIUS ** 2
    sep_sq = SEPARATION_DISTANCE ** 2
    
    neighbor_mask = dist_sq < radius_sq
    sep_mask = dist_sq < sep_sq
    
    # 2. CALCULATE RULES
    
    # -- ALIGNMENT --
    if SIM_SETTINGS["alignment"]:
        # Average velocity of neighbors
        # We perform dot product of mask and velocities
        neighbor_counts = neighbor_mask.sum(axis=1).reshape(-1, 1)
        neighbor_counts[neighbor_counts == 0] = 1 # Avoid div by zero
        
        avg_vel = (neighbor_mask @ vel) / neighbor_counts
        align_force = avg_vel - vel
    else:
        align_force = np.zeros_like(vel)

    # -- COHESION --
    if SIM_SETTINGS["cohesion"]:
        # Average position of neighbors
        avg_pos = (neighbor_mask @ pos) / neighbor_counts
        cohesion_force = avg_pos - pos
        # Normalize
        # (This is a simplified cohesion for speed)
    else:
        cohesion_force = np.zeros_like(vel)

    # -- SEPARATION --
    if SIM_SETTINGS["separation"]:
        # Push away from close neighbors 
        # Weight by inverse distance (closer = push harder)
        dist_sq_safe = dist_sq.copy()
        # Avoid division by zero
        dist_sq_safe[dist_sq_safe < 0.1] = 0.1
        
        push = diff / dist_sq_safe[:, :, np.newaxis]
        # Sum up only the separation neighbors
        sep_force = np.einsum('ij,ijk->ik', sep_mask, push) * 50 # Multiplier
    else:
        sep_force = np.zeros_like(vel)

    # -- MOUSE INTERACTION --
    mouse_force = np.zeros_like(vel)
    if SIM_SETTINGS["mouse_mode"] != 0:
        # Calculate vector to mouse for ALL birds
        to_mouse = mouse_pos - pos
        dist_mouse = np.linalg.norm(to_mouse, axis=1, keepdims=True)
        
        if SIM_SETTINGS["mouse_mode"] == 1: # FOLLOW
            # Normalize and steer
            dist_mouse[dist_mouse == 0] = 1
            desired = (to_mouse / dist_mouse) * MAX_SPEED
            steer = desired - vel
            mouse_force = steer * 2.0
            
        elif SIM_SETTINGS["mouse_mode"] == 2: # SCARE
            # Only affect birds within 200px
            scare_mask = (dist_mouse < 200).flatten()
            if np.any(scare_mask):
                # Run away!
                dist_mouse[dist_mouse == 0] = 1
                desired = (to_mouse[scare_mask] / dist_mouse[scare_mask]) * -MAX_SPEED
                steer = desired - vel[scare_mask]
                mouse_force[scare_mask] = steer * 5.0

    # 3. APPLY FORCES
    total_acc = (align_force * 0.5) + (cohesion_force * 0.01) + (sep_force * 1.5) + mouse_force
    
    # Cap Force
    force_mags = np.linalg.norm(total_acc, axis=1, keepdims=True)
    force_mags[force_mags == 0] = 1
    # If force > MAX_FORCE, scale it down
    total_acc = np.where(force_mags > MAX_FORCE, total_acc / force_mags * MAX_FORCE, total_acc)
    
    return total_acc

def draw_ui(screen, font, clock, num_boids):
    # UI Box
    s = pygame.Surface((220, 200))
    s.set_alpha(200)
    s.fill((0, 0, 0))
    screen.blit(s, (10, 10))
    
    def txt(t, x, y, c=WHITE):
        screen.blit(font.render(t, True, c), (x, y))

    fps = int(clock.get_fps())
    c = GREEN if fps > 45 else RED
    txt(f"FPS: {fps}", 20, 20, c)
    txt(f"Count: {num_boids}", 20, 40)
    
    # Settings
    txt(f"[S] Sep: {SIM_SETTINGS['separation']}", 20, 70, GREEN if SIM_SETTINGS['separation'] else RED)
    txt(f"[A] Ali: {SIM_SETTINGS['alignment']}", 20, 90, GREEN if SIM_SETTINGS['alignment'] else RED)
    txt(f"[C] Coh: {SIM_SETTINGS['cohesion']}", 20, 110, GREEN if SIM_SETTINGS['cohesion'] else RED)
    
    # Modes
    m_text = "NONE"
    if SIM_SETTINGS["mouse_mode"] == 1: m_text = "FOLLOW"
    if SIM_SETTINGS["mouse_mode"] == 2: m_text = "SCARE"
    txt(f"[M] Mouse: {m_text}", 20, 140, CYAN)
    
    txt(f"[V] Simple: {SIM_SETTINGS['simple_view']}", 20, 160)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NumPy Boids - Super Speed")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    # Init Data
    pos, vel, acc = init_boids(NUM_BOIDS)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s: SIM_SETTINGS["separation"] = not SIM_SETTINGS["separation"]
                if event.key == pygame.K_a: SIM_SETTINGS["alignment"] = not SIM_SETTINGS["alignment"]
                if event.key == pygame.K_c: SIM_SETTINGS["cohesion"] = not SIM_SETTINGS["cohesion"]
                if event.key == pygame.K_SPACE: SIM_SETTINGS["paused"] = not SIM_SETTINGS["paused"]
                if event.key == pygame.K_v: SIM_SETTINGS["simple_view"] = not SIM_SETTINGS["simple_view"]
                
                if event.key == pygame.K_m:
                    SIM_SETTINGS["mouse_mode"] = (SIM_SETTINGS["mouse_mode"] + 1) % 3
                
                # Dynamic Adding/Removing not supported in simple NumPy array demo
                # (Requires resizing arrays which is slow, so we stick to fixed size for speed)

        if not SIM_SETTINGS["paused"]:
            mouse_pos = np.array(pygame.mouse.get_pos())
            
            # Physics Update
            acc = update_boids(pos, vel, mouse_pos)
            vel += acc
            
            # Cap Speed
            speeds = np.linalg.norm(vel, axis=1, keepdims=True)
            speeds[speeds == 0] = 1
            vel = np.where(speeds > MAX_SPEED, vel / speeds * MAX_SPEED, vel)
            
            pos += vel
            
            # Wrap Edges
            pos[:, 0] = pos[:, 0] % WIDTH
            pos[:, 1] = pos[:, 1] % HEIGHT

        # Draw
        screen.fill(BLACK)
        
        # Super fast drawing for 1000+ items
        if SIM_SETTINGS["simple_view"]:
            # Draw single pixels (extremely fast)
            for i in range(len(pos)):
                screen.set_at((int(pos[i,0]), int(pos[i,1])), CYAN)
        else:
            # Draw circles (slower)
            for i in range(len(pos)):
                pygame.draw.circle(screen, CYAN, (int(pos[i,0]), int(pos[i,1])), 2)

        draw_ui(screen, font, clock, len(pos))
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()