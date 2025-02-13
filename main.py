import pygame
import random
import math
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Screen setup
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Valentine's Heart Quest")

# Colors
PINK = (255, 192, 203)
LIGHT_PINK = (255, 223, 230)
DARKER_PINK = (255, 150, 180)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
DARK_PURPLE = (128, 0, 128)
BLUE = (173, 216, 230)  # New color for the time text 
# Load custom font
love_font = pygame.font.Font(None, 24)

class Heart:
    def __init__(self):
        self.size = 1  # Decreased size to be smaller than the player's size
        self.angle = 0  # For rotation
        self.scale = 1.0  # For pulsing effect
        self.scale_direction = 0.02
        self.reset()
        
    def reset(self):
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = -self.size
        self.speed = random.uniform(1, 3)
        self.worth = random.choice([1, 1, 1, 2, 3])
        self.angle = 0
        
    def draw(self, surface):
        color = GOLD if self.worth > 1 else RED
        center_x = self.x
        center_y = self.y
        
        # Update animation effects
        self.angle += 2  # Rotate
        self.scale += self.scale_direction
        if self.scale > 1.2 or self.scale < 0.8:
            self.scale_direction *= -1
            
        # Create heart shape with animation
        points = []
        for t in range(0, 100):
            t = t / 100
            # Basic heart shape
            x = 16 * math.sin(t * 2 * math.pi) ** 3
            y = -(13 * math.cos(t * 2 * math.pi) - 5 * math.cos(2 * t * 2 * math.pi) - 
                 2 * math.cos(3 * t * 2 * math.pi) - math.cos(4 * t * 2 * math.pi))
            
            # Apply scaling
            x *= self.size * self.scale
            y *= self.size * self.scale
            
            # Apply rotation
            angle_rad = math.radians(self.angle)
            rot_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
            rot_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
            
            # Translate to position
            final_x = center_x + rot_x
            final_y = center_y + rot_y
            
            points.append((int(final_x), int(final_y)))
            
        if len(points) > 2:
            pygame.draw.polygon(surface, color, points)
            # Add glow effect
            for i in range(3):
                glow_points = [(x + random.randint(-1, 1), y + random.randint(-1, 1)) 
                              for x, y in points]
                pygame.draw.polygon(surface, (*color, 50), glow_points)
    
    def move(self):
        self.y += self.speed
        if self.y > HEIGHT + self.size:
            self.reset()
            
    def collides_with(self, player):
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < (self.size + player.size)

class WinAnimation:
    def __init__(self):
        self.frame = 0
        self.boy_x = WIDTH // 2 - 100
        self.girl_x = WIDTH // 2 + 100
        self.y = HEIGHT // 2
        self.hearts = []
        for _ in range(20):
            self.hearts.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(5, 15),
                'speed': random.uniform(1, 3)
            })

    def draw(self, surface):
        # Draw floating hearts background
        for heart in self.hearts:
            heart['y'] -= heart['speed']
            if heart['y'] < -20:
                heart['y'] = HEIGHT + 20
            self.draw_heart(surface, heart['x'], heart['y'], heart['size'], DARKER_PINK)

        # Draw boy and girl
        # Boy
        pygame.draw.circle(surface, (135, 206, 235), (int(self.boy_x), self.y), 30)  # Head
        pygame.draw.rect(surface, (0, 0, 139), (int(self.boy_x)-20, self.y+30, 40, 50))  # Body
        
        # Girl
        pygame.draw.circle(surface, (255, 192, 203), (int(self.girl_x), self.y), 30)  # Head
        pygame.draw.polygon(surface, (255, 105, 180), [
            (int(self.girl_x)-20, self.y+30),
            (int(self.girl_x)+20, self.y+30),
            (int(self.girl_x)+30, self.y+80),
            (int(self.girl_x)-30, self.y+80)
        ])  # Dress

        # Animate characters coming together
        if self.boy_x < WIDTH // 2 - 20:
            self.boy_x += 1
        if self.girl_x > WIDTH // 2 + 20:
            self.girl_x -= 1

        # Draw hearts between them when close
        if abs(self.boy_x - self.girl_x) < 100:
            self.draw_heart(surface, WIDTH // 2, self.y - 40, 20, RED)

    def draw_heart(self, surface, x, y, size, color):
        points = []
        for t in range(0, 100):
            t = t / 100
            px = x + size * (16 * math.sin(t * 2 * math.pi) ** 3) / 16
            py = y - size * (13 * math.cos(t * 2 * math.pi) - 5 * math.cos(2 * t * 2 * math.pi) -
                           2 * math.cos(3 * t * 2 * math.pi) - math.cos(4 * t * 2 * math.pi)) / 16
            points.append((int(px), int(py)))
        if len(points) > 2:
            pygame.draw.polygon(surface, color, points)

class Game:
    def __init__(self):
        self.player = Player()
        self.hearts = [Heart() for _ in range(5)]
        self.font = pygame.font.Font(None, 36)
        self.required_score = 50
        self.game_over = False
        self.start_time = pygame.time.get_ticks()
        self.time_limit = 60000  # 60 seconds
        self.particles = []
        self.win_animation = None
        
    def create_particles(self, x, y, color):
        for _ in range(10):
            particle = {
                'x': x,
                'y': y,
                'dx': random.uniform(-2, 2),
                'dy': random.uniform(-2, 2),
                'lifetime': 30,
                'color': color
            }
            self.particles.append(particle)
            
    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                
    def draw_particles(self, surface):
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / 30))
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(surface, color, 
                             (int(particle['x']), int(particle['y'])), 2)
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        particle_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        while running:
            current_time = pygame.time.get_ticks()
            time_remaining = max(0, (self.time_limit - (current_time - self.start_time)) // 1000)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            if not self.game_over:
                self.player.move()
                
                for heart in self.hearts:
                    heart.move()
                    if heart.collides_with(self.player):
                        self.player.collected += heart.worth
                        self.create_particles(heart.x, heart.y, 
                                           GOLD if heart.worth > 1 else RED)
                        heart.reset()
                
                if self.player.collected >= self.required_score:
                    self.game_over = True
                    self.win_animation = WinAnimation()
                    
                if time_remaining <= 0:
                    self.game_over = True
            
            # Draw background with gradient
            for i in range(HEIGHT):
                progress = i / HEIGHT
                color = tuple(int(a + (b - a) * progress) for a, b in zip(LIGHT_PINK, DARKER_PINK))
                pygame.draw.line(screen, color, (0, i), (WIDTH, i))
            
            # Draw decorative background hearts
            if not self.game_over or not self.win_animation:
                for _ in range(5):
                    x = random.randint(0, WIDTH)
                    y = random.randint(0, HEIGHT)
                    size = random.randint(5, 15)
                    color = (*DARKER_PINK, 50)  # Semi-transparent
                    pygame.draw.circle(screen, color, (x, y), size)
            
            if not self.game_over:
                self.player.draw(screen)
                for heart in self.hearts:
                    heart.draw(screen)
                
                # Update and draw particles
                self.update_particles()
                particle_surface.fill((0, 0, 0, 0))
                self.draw_particles(particle_surface)
                screen.blit(particle_surface, (0, 0))
                
                # Draw UI
                score_text = self.font.render(f'Hearts: {self.player.collected}/{self.required_score}', 
                                            True, BLUE)
                time_text = self.font.render(f'Time: {time_remaining}s', True, BLUE)
                screen.blit(score_text, (10, 10))
                screen.blit(time_text, (WIDTH - 150, 10))
                
                # Draw instructions
                instructions_text = love_font.render('Collect hearts to score points!', True, BLUE)
                screen.blit(instructions_text, (10, 40))
            
            if self.game_over:
                if self.player.collected >= self.required_score:
                    if self.win_animation:
                        self.win_animation.draw(screen)
                    result_text = self.font.render('You Win! Happy Valentine\'s Day!', 
                                                 True, DARK_PURPLE)
                else:
                    result_text = self.font.render('Game Over - Try Again!', True, RED)
                screen.blit(result_text, 
                          (WIDTH//2 - result_text.get_width()//2, 
                           HEIGHT//2 - result_text.get_height()//2 - 100))
            
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 5
        self.size = 40
        self.collected = 0
        
    def draw(self, surface):
        # Draw cupid-like character
        pygame.draw.circle(surface, PINK, (self.x, self.y), self.size)
        # Draw wings with gradient effect
        for i in range(30):
            alpha = 255 - i * 8
            wing_color = (*WHITE, alpha)
            pygame.draw.ellipse(surface, wing_color, 
                              (self.x - 40 + i//2, self.y - 20, 30, 40))
            pygame.draw.ellipse(surface, wing_color, 
                              (self.x + 10 - i//2, self.y - 20, 30, 40))
        
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > self.size:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.size:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.size:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.size:
            self.y += self.speed

if __name__ == "__main__":
    game = Game()
    game.run() 
