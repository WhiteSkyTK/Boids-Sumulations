import pygame
import random
import math

# --- INITIAL SETTINGS ---
WIDTH = 1000
HEIGHT = 700
FPS = 60

# Default Physics (Variable now!)
max_speed = 5.0
max_force = 0.2
perception_radius = 50
grid_size = 50

# Simulation State
SIM_SETTINGS = {
    "separation": True,
    "alignment": True,
    "cohesion": True,
    "follow_mouse": False, # Steer towards mouse
    "repel_mouse": False,  # Run away from mouse
    "simple_view": False,  # Performance mode (draws dots)
    "debug": False,
    "paused": False
}

# Colors
BLACK = (10, 10, 20)
WHITE = (220, 220, 220)
CYAN = (0, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
GREY = (100, 100, 100)

# --- SPATIAL GRID ---
class SpatialGrid:
    def __init__(self):
        self.grid = {}
    def clear(self):
        self.grid = {}
    def add(self, boid):
        col = int(boid.position.x // grid_size)
        row = int(boid.position.y // grid_size)
        cell = (col, row)
        if cell not in self.grid: self.grid[cell] = []
        self.grid[cell].append(boid)
    def get_nearby_boids(self, boid):
        boids = []
        col = int(boid.position.x // grid_size)
        row = int(boid.position.y // grid_size)
        for c in range(col - 1, col + 2):
            for r in range(row - 1, row + 2):
                cell = (c, r)
                if cell in self.grid:
                    boids.extend(self.grid[cell])
        return boids

# --- THE BOID CLASS ---
class Boid:
    def __init__(self):
        self.position = pygame.math.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.velocity.length() == 0: self.velocity = pygame.math.Vector2(1, 0)
        self.velocity.scale_to_length(max_speed)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.color = CYAN

    def edges(self):
        if self.position.x > WIDTH: self.position.x = 0
        elif self.position.x < 0: self.position.x = WIDTH
        if self.position.y > HEIGHT: self.position.y = 0
        elif self.position.y < 0: self.position.y = HEIGHT

    def apply_behavior(self, nearby_boids):
        alignment = pygame.math.Vector2(0, 0)
        cohesion = pygame.math.Vector2(0, 0)
        separation = pygame.math.Vector2(0, 0)
        mouse_force = pygame.math.Vector2(0, 0)

        # 1. Mouse Interaction
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
        
        if SIM_SETTINGS["follow_mouse"]:
            # Steer towards mouse
            vec_to_mouse = mouse_pos - self.position
            if vec_to_mouse.length() > 0:
                vec_to_mouse.scale_to_length(max_speed)
                steer = vec_to_mouse - self.velocity
                if steer.length() > max_force * 2: # Stronger attraction
                     steer.scale_to_length(max_force * 2)
                mouse_force += steer

        if SIM_SETTINGS["repel_mouse"]:
            # Run away from mouse if close
            dist = self.position.distance_to(mouse_pos)
            if dist < 150: # Run if within 150 pixels
                diff = self.position - mouse_pos
                diff.scale_to_length(max_speed)
                steer = diff - self.velocity
                if steer.length() > max_force * 3: # PANIC! Run fast!
                    steer.scale_to_length(max_force * 3)
                mouse_force += steer

        # 2. Flock Rules (Optimized)
        if nearby_boids:
            if SIM_SETTINGS["alignment"]: alignment = self.align(nearby_boids)
            if SIM_SETTINGS["cohesion"]: cohesion = self.cohere(nearby_boids)
            if SIM_SETTINGS["separation"]: separation = self.separate(nearby_boids)

        self.acceleration += alignment
        self.acceleration += cohesion
        self.acceleration += separation * 1.5
        self.acceleration += mouse_force

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        
        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)
        if self.velocity.length() == 0:
             self.velocity = pygame.math.Vector2(1, 0)

        self.acceleration = pygame.math.Vector2(0, 0)
        self.edges()

    def draw(self, screen):
        # Optimization: Simple View draws a dot (faster) vs Complex View draws a triangle
        if SIM_SETTINGS["simple_view"]:
            pygame.draw.rect(screen, self.color, (int(self.position.x), int(self.position.y), 2, 2))
        else:
            angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x)) - 90
            p1 = self.position + pygame.math.Vector2(0, -6).rotate(-angle)
            p2 = self.position + pygame.math.Vector2(-3, 4).rotate(-angle)
            p3 = self.position + pygame.math.Vector2(3, 4).rotate(-angle)
            pygame.draw.polygon(screen, self.color, [p1, p2, p3])

        if SIM_SETTINGS["debug"]:
            pygame.draw.circle(screen, (50, 50, 50), (int(self.position.x), int(self.position.y)), perception_radius, 1)

    # --- RULES ---
    def align(self, boids):
        steering = pygame.math.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self:
                dist = self.position.distance_to(other.position)
                if dist < perception_radius:
                    steering += other.velocity
                    total += 1
        if total > 0:
            steering /= total
            if steering.length() > 0.1: steering.scale_to_length(max_speed)
            steering -= self.velocity
            if steering.length() > max_force: steering.scale_to_length(max_force)
        return steering

    def cohere(self, boids):
        steering = pygame.math.Vector2(0, 0)
        total = 0
        center_of_mass = pygame.math.Vector2(0, 0)
        for other in boids:
            if other != self:
                dist = self.position.distance_to(other.position)
                if dist < perception_radius:
                    center_of_mass += other.position
                    total += 1
        if total > 0:
            center_of_mass /= total
            vec_to_target = center_of_mass - self.position
            if vec_to_target.length() > 0.1: vec_to_target.scale_to_length(max_speed)
            steering = vec_to_target - self.velocity
            if steering.length() > max_force: steering.scale_to_length(max_force)
        return steering

    def separate(self, boids):
        steering = pygame.math.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self:
                dist = self.position.distance_to(other.position)
                if dist < perception_radius / 2 and dist > 0:
                    diff = self.position - other.position
                    diff /= dist 
                    steering += diff
                    total += 1
        if total > 0:
            steering /= total
            if steering.length() > 0.1: steering.scale_to_length(max_speed)
            steering -= self.velocity
            if steering.length() > max_force: steering.scale_to_length(max_force)
        return steering

# --- UI HELPER ---
def draw_ui(screen, font, flock_size, clock):
    s = pygame.Surface((250, 260)) # Bigger panel
    s.set_alpha(200)
    s.fill((0, 0, 0))
    screen.blit(s, (10, 10))

    def draw_text(text, x, y, color=WHITE):
        img = font.render(text, True, color)
        screen.blit(img, (x, y))

    fps = int(clock.get_fps())
    fps_color = GREEN if fps > 50 else RED
    
    draw_text(f"FPS: {fps}", 20, 20, fps_color)
    draw_text(f"Boids: {flock_size}", 20, 40)
    
    # Physics Stats
    draw_text(f"Speed (Q/W): {max_speed:.1f}", 20, 70, YELLOW)
    draw_text(f"Force (E/R): {max_force:.2f}", 20, 90, YELLOW)

    # Toggles
    draw_text(f"[S] Separation: {'ON' if SIM_SETTINGS['separation'] else 'OFF'}", 20, 120, GREEN if SIM_SETTINGS['separation'] else RED)
    draw_text(f"[A] Alignment:  {'ON' if SIM_SETTINGS['alignment'] else 'OFF'}", 20, 140, GREEN if SIM_SETTINGS['alignment'] else RED)
    draw_text(f"[C] Cohesion:   {'ON' if SIM_SETTINGS['cohesion'] else 'OFF'}", 20, 160, GREEN if SIM_SETTINGS['cohesion'] else RED)
    
    # Mouse Modes
    mode_text = "NONE"
    mode_color = GREY
    if SIM_SETTINGS["follow_mouse"]: 
        mode_text = "FOLLOW MOUSE"
        mode_color = CYAN
    elif SIM_SETTINGS["repel_mouse"]: 
        mode_text = "SCARE (PREDATOR)"
        mode_color = RED
    
    draw_text(f"[M] Mode: {mode_text}", 20, 190, mode_color)
    draw_text(f"[V] View: {'SIMPLE' if SIM_SETTINGS['simple_view'] else 'FULL'}", 20, 210)
    draw_text(f"[D] Debug: {'ON' if SIM_SETTINGS['debug'] else 'OFF'}", 20, 230)

    draw_text("UP/DOWN: +/- Boids", 20, HEIGHT-30, GREY)

# --- MAIN LOOP ---
def main():
    global max_speed, max_force # Allow modifying these inside main
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ultimate Boids")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    flock = [Boid() for _ in range(300)]
    spatial_grid = SpatialGrid()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Toggles
                if event.key == pygame.K_s: SIM_SETTINGS["separation"] = not SIM_SETTINGS["separation"]
                if event.key == pygame.K_a: SIM_SETTINGS["alignment"] = not SIM_SETTINGS["alignment"]
                if event.key == pygame.K_c: SIM_SETTINGS["cohesion"] = not SIM_SETTINGS["cohesion"]
                if event.key == pygame.K_d: SIM_SETTINGS["debug"] = not SIM_SETTINGS["debug"]
                if event.key == pygame.K_SPACE: SIM_SETTINGS["paused"] = not SIM_SETTINGS["paused"]
                if event.key == pygame.K_v: SIM_SETTINGS["simple_view"] = not SIM_SETTINGS["simple_view"]
                
                # Mouse Modes (Toggle through them)
                if event.key == pygame.K_m:
                    if not SIM_SETTINGS["follow_mouse"] and not SIM_SETTINGS["repel_mouse"]:
                        SIM_SETTINGS["follow_mouse"] = True # Mode 1
                    elif SIM_SETTINGS["follow_mouse"]:
                        SIM_SETTINGS["follow_mouse"] = False
                        SIM_SETTINGS["repel_mouse"] = True  # Mode 2
                    else:
                        SIM_SETTINGS["repel_mouse"] = False # Mode 0
                
                # Adjust Physics Variables
                if event.key == pygame.K_q: max_speed += 0.5
                if event.key == pygame.K_w and max_speed > 1: max_speed -= 0.5
                if event.key == pygame.K_e: max_force += 0.05
                if event.key == pygame.K_r and max_force > 0.05: max_force -= 0.05

                # Add/Remove Boids
                if event.key == pygame.K_UP:
                    for _ in range(10): flock.append(Boid())
                if event.key == pygame.K_DOWN:
                    for _ in range(10): 
                        if flock: flock.pop()

        if not SIM_SETTINGS["paused"]:
            spatial_grid.clear()
            for boid in flock: spatial_grid.add(boid)
            for boid in flock:
                nearby = spatial_grid.get_nearby_boids(boid)
                boid.apply_behavior(nearby)
                boid.update()

        screen.fill(BLACK)
        for boid in flock:
            boid.draw(screen)
        draw_ui(screen, font, len(flock), clock)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()