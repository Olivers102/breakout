import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280  # Increased from 1024
WINDOW_HEIGHT = 900  # Increased from 768
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
BALL_SIZE = 10
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_ROWS = 8  # Increased from 6
BRICK_COLS = 15  # Increased from 12
FPS = 60
POWERUP_SIZE = 20
POWERUP_SPEED = 3
POWERUP_DURATION = 10  # seconds
POWERUP_FALL_DURATION = 5  # seconds before powerup disappears if not caught

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.width = POWERUP_SIZE
        self.height = POWERUP_SIZE
        self.speed = POWERUP_SPEED
        self.type = powerup_type
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.active = True
        self.creation_time = pygame.time.get_ticks()
        
        # Set color based on powerup type
        if powerup_type == "speed":
            self.color = GREEN
        elif powerup_type == "paddle":
            self.color = BLUE
        elif powerup_type == "multiball":
            self.color = PURPLE
        else:
            self.color = WHITE
            
    def move(self):
        self.y += self.speed
        self.rect.y = self.y
        
        # Deactivate if it falls off the screen or time limit reached
        current_time = pygame.time.get_ticks()
        if self.y > WINDOW_HEIGHT or (current_time - self.creation_time) > POWERUP_FALL_DURATION * 1000:
            self.active = False
            
    def draw(self):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)
            
            # Draw a timer bar to show remaining time
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.creation_time
            remaining_time = max(0, POWERUP_FALL_DURATION - elapsed_time / 1000)
            timer_width = (remaining_time / POWERUP_FALL_DURATION) * self.width
            
            # Draw timer bar
            pygame.draw.rect(screen, WHITE, (self.x, self.y - 5, timer_width, 3))

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - 40
        self.speed = 8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.powerup_timer = 0
        self.powerup_active = False
        self.powerup_type = None
        self.powerup_end_time = 0

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < WINDOW_WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x
        
    def apply_powerup(self, powerup_type):
        self.powerup_type = powerup_type
        self.powerup_active = True
        self.powerup_timer = pygame.time.get_ticks()
        self.powerup_end_time = self.powerup_timer + POWERUP_DURATION * 1000
        
        if powerup_type == "speed":
            self.speed = 12  # Increased speed
        elif powerup_type == "paddle":
            self.width = PADDLE_WIDTH * 1.5  # 50% larger paddle
            self.rect.width = self.width
            
    def update_powerup(self):
        if self.powerup_active:
            current_time = pygame.time.get_ticks()
            if current_time > self.powerup_end_time:
                self.deactivate_powerup()
                
    def deactivate_powerup(self):
        self.powerup_active = False
        self.powerup_type = None
        
        if self.powerup_type == "speed":
            self.speed = 8  # Reset speed
        elif self.powerup_type == "paddle":
            self.width = PADDLE_WIDTH  # Reset paddle size
            self.rect.width = self.width

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)
        
        # Draw powerup timer if active
        if self.powerup_active:
            current_time = pygame.time.get_ticks()
            remaining_time = max(0, self.powerup_end_time - current_time)
            timer_width = (remaining_time / (POWERUP_DURATION * 1000)) * self.width
            
            # Draw timer bar above paddle
            pygame.draw.rect(screen, self.get_powerup_color(), (self.x, self.y - 5, timer_width, 3))
    
    def get_powerup_color(self):
        if self.powerup_type == "speed":
            return GREEN
        elif self.powerup_type == "paddle":
            return BLUE
        elif self.powerup_type == "multiball":
            return PURPLE
        return WHITE

class Ball:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 60
        self.speed_x = 5
        self.speed_y = -5
        self.rect = pygame.Rect(self.x, self.y, BALL_SIZE, BALL_SIZE)
        
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Wall collisions
        if self.x <= 0 or self.x >= WINDOW_WIDTH - BALL_SIZE:
            self.speed_x *= -1
        if self.y <= 0:
            self.speed_y *= -1
            
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

class Brick:
    def __init__(self, x, y, color, is_special=False, powerup_type=None, is_strong=False):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.visible = True
        self.is_special = is_special
        self.powerup_type = powerup_type
        self.is_strong = is_strong
        self.hits_required = 2 if is_strong else 1
        self.hits = 0

    def hit(self):
        if self.is_strong:
            self.hits += 1
            if self.hits >= self.hits_required:
                self.visible = False
                return True
            return False
        else:
            self.visible = False
            return True

    def draw(self):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            
            # Draw special indicators
            if self.is_special:
                # Draw a star or symbol to indicate special brick
                center_x = self.rect.centerx
                center_y = self.rect.centery
                pygame.draw.circle(screen, WHITE, (center_x, center_y), 5)
                
            # Draw strong brick indicator
            if self.is_strong:
                # Draw a border to indicate strong brick
                pygame.draw.rect(screen, GRAY, self.rect, 2)
                # Draw a number to show hits remaining
                font = pygame.font.Font(None, 24)
                hits_text = font.render(str(self.hits_required - self.hits), True, WHITE)
                text_rect = hits_text.get_rect(center=self.rect.center)
                screen.blit(hits_text, text_rect)

class Game:
    def __init__(self):
        self.paddle = Paddle()
        self.balls = [Ball()]  # List to hold multiple balls
        self.bricks = []
        self.powerups = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.create_bricks()

    def create_bricks(self):
        colors = [RED, GREEN, BLUE, YELLOW, WHITE, ORANGE]
        powerup_types = ["speed", "paddle", "multiball"]
        
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = col * (BRICK_WIDTH + 2) + 1
                y = row * (BRICK_HEIGHT + 2) + 1
                
                # Make some bricks special with powerups (about 10% of bricks)
                is_special = random.random() < 0.1
                powerup_type = random.choice(powerup_types) if is_special else None
                
                # Make some bricks strong (require 2 hits) (about 15% of bricks)
                is_strong = random.random() < 0.15
                
                # Special bricks get a different color
                if is_special:
                    color = PURPLE
                elif is_strong:
                    color = GRAY
                else:
                    color = colors[row % len(colors)]
                
                self.bricks.append(Brick(x, y, color, is_special, powerup_type, is_strong))

    def handle_collisions(self):
        # Paddle collision
        for ball in self.balls:
            if ball.rect.colliderect(self.paddle.rect):
                ball.speed_y = -abs(ball.speed_y)  # Always bounce up
                # Add some angle based on where the ball hits the paddle
                relative_intersect_x = (self.paddle.x + (self.paddle.width/2)) - ball.x
                normalized_relative_intersect_x = relative_intersect_x/(self.paddle.width/2)
                bounce_angle = normalized_relative_intersect_x * 0.75  # Max 75 degrees
                ball.speed_x = -bounce_angle * 5
                ball.speed_y = -5

        # Brick collisions
        for ball in self.balls:
            for brick in self.bricks:
                if brick.visible and ball.rect.colliderect(brick.rect):
                    # Handle brick hit
                    if brick.hit():
                        ball.speed_y *= -1
                        self.score += 30 if brick.is_special else (20 if brick.is_strong else 10)
                        
                        # Create powerup if it's a special brick
                        if brick.is_special:
                            powerup = PowerUp(brick.rect.centerx - POWERUP_SIZE//2, 
                                             brick.rect.centery, 
                                             brick.powerup_type)
                            self.powerups.append(powerup)
                    else:
                        # Brick was hit but not destroyed (strong brick)
                        ball.speed_y *= -1
                        self.score += 5  # Small points for hitting a strong brick
                    break

        # Powerup collisions
        for powerup in self.powerups[:]:
            if powerup.active and powerup.rect.colliderect(self.paddle.rect):
                self.paddle.apply_powerup(powerup.type)
                powerup.active = False
                self.powerups.remove(powerup)
                
                # Handle multiball powerup
                if powerup.type == "multiball":
                    # Create two additional balls
                    for _ in range(2):
                        new_ball = Ball()
                        new_ball.x = self.paddle.x + self.paddle.width//2
                        new_ball.y = self.paddle.y - BALL_SIZE
                        new_ball.speed_x = random.choice([-5, 5])
                        new_ball.speed_y = -5
                        self.balls.append(new_ball)

        # Check if balls are below paddle
        for ball in self.balls[:]:
            if ball.y > WINDOW_HEIGHT:
                self.balls.remove(ball)
                
        # If all balls are lost, decrease lives
        if not self.balls:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                # Reset with one ball
                self.balls = [Ball()]
                self.balls[0].reset()

    def draw(self):
        screen.fill(BLACK)
        self.paddle.draw()
        
        # Draw all balls
        for ball in self.balls:
            ball.draw()
            
        # Draw all bricks
        for brick in self.bricks:
            brick.draw()
            
        # Draw all powerups
        for powerup in self.powerups:
            powerup.draw()
        
        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        lives_text = font.render(f'Lives: {self.lives}', True, WHITE)
        screen.blit(score_text, (10, WINDOW_HEIGHT - 30))
        screen.blit(lives_text, (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 30))

        if self.game_over:
            game_over_text = font.render('GAME OVER', True, RED)
            screen.blit(game_over_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))

        pygame.display.flip()

    def update(self):
        if not self.game_over:
            # Update paddle powerups
            self.paddle.update_powerup()
            
            # Update all balls
            for ball in self.balls:
                ball.move()
                
            # Update all powerups
            for powerup in self.powerups[:]:
                powerup.move()
                if not powerup.active:
                    self.powerups.remove(powerup)
                    
            self.handle_collisions()

def main():
    game = Game()
    ball_launched = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not ball_launched:
                    ball_launched = True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game.paddle.move("left")
        if keys[pygame.K_RIGHT]:
            game.paddle.move("right")

        if not ball_launched:
            # Only update the ball's x position to match the paddle's center
            game.balls[0].x = game.paddle.x + game.paddle.width//2 - BALL_SIZE//2
            game.balls[0].rect.x = game.balls[0].x
            # Reset the ball's y position to stay above the paddle
            game.balls[0].y = game.paddle.y - BALL_SIZE
            game.balls[0].rect.y = game.balls[0].y

        game.update()
        game.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    main() 