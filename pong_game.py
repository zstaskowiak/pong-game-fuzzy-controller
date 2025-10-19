
"""
🎮 Pong with AI-controlled paddle using Fuzzy Logic
---------------------------------------------------

GitHub: https://github.com/zstaskowiak
Description:
    A simple Pong game implemented in Python using pygame and scikit-fuzzy.
    The top paddle is controlled by a fuzzy logic system that reacts dynamically
    to the position and velocity of the ball.

    This project demonstrates:
    - Basic AI control using fuzzy logic rules
    - Real-time simulation in pygame
    - Application of fuzzy sets and membership functions in an intuitive context
"""

import pygame
import sys
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class Ball:
    def __init__(self, x, y, speed_x, speed_y, radius):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = radius

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def bounce_x(self):
        self.speed_x *= -1

    def bounce_y(self):
        self.speed_y *= -1

    def reset(self, x, y, speed_x, speed_y):
        """Reset ball to a given position and velocity."""
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def move_left(self):
        self.x -= self.speed

    def move_right(self):
        self.x += self.speed

    def clamp(self, screen_width):
        """Keep the paddle within screen bounds."""
        self.x = max(0, min(self.x, screen_width - self.width))

    

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pong Game")
        self.clock = pygame.time.Clock()

        # Define color palette
        self.colors = {
            'light': (255, 255, 217),
            'light2': (255, 240, 217),
            'dark': (198, 159, 213),
            'evil': (143, 83, 184)
        }

        # Draw checkered background
        self.ts = 50  # tile size
        self.background = pygame.Surface((self.width, self.height))
        for x in range(0, self.width, self.ts):
            for y in range(0, self.height, self.ts):
                color = self.colors["light"] if (x // self.ts + y // self.ts) % 2 == 0 else self.colors["light2"]
                pygame.draw.rect(self.background, color, (x, y, self.ts, self.ts))


        # Initialize game objects
        self.ball_color = self.colors['dark']
        self.ball = Ball(self.width // 2, self.height // 2, 2.0, 2.0, 10)
        self.player_paddle = Paddle(self.width // 2 + 100, self.height - 40, 100, 15, 2.0)
        self.ai_paddle = Paddle(self.width // 2 - 50, 30, 100, 15, 2.0)
        self.growth = 0.2
        self.setup_fuzzy()
        self.running = True

    def setup_fuzzy(self):

        """Initialize fuzzy control system for paddle movement."""
        self.velocity_universe = np.arange(-200, 200, 0.1)
        self.x_diff_universe = np.arange(-400, 401, 1)
        self.y_diff_universe = np.arange(0, 401, 1)

        self.x_diff = ctrl.Antecedent(self.x_diff_universe, 'x_diff')
        self.y_diff = ctrl.Antecedent(self.y_diff_universe, 'y_diff')

        self.paddle_velocity = ctrl.Consequent(self.velocity_universe, 'paddle_velocity')

        # Define fuzzy sets
        self.x_diff['left'] = fuzz.trimf(self.x_diff_universe, [-400, -200, 0])
        self.x_diff['center'] = fuzz.trimf(self.x_diff_universe, [-50, 0, 50])
        self.x_diff['right'] = fuzz.trimf(self.x_diff_universe, [0, 200, 400])

        self.y_diff['close'] = fuzz.trimf(self.y_diff_universe, [0, 0, 20])
        self.y_diff['medium'] = fuzz.trimf(self.y_diff_universe, [0, 200, 300])
        self.y_diff['far'] = fuzz.trimf(self.y_diff_universe, [200, 200, 400])

        # self.x_diff.view()
        # self.y_diff.view()

        self.create_paddle_simulation(abs(self.ball.speed_x))

    def create_paddle_simulation(self, current_vel_max):
        
        if abs(self.ball.speed_x) > 6:
            self.x_diff['center'] = fuzz.trimf(self.x_diff_universe, [-1, 0, 1])
        else:
            self.x_diff['center'] = fuzz.trimf(self.x_diff_universe, [-10, 0, 10])

        
        # Define fuzzy output sets
    
        self.paddle_velocity['left_fast'] = fuzz.trimf(self.velocity_universe, [-current_vel_max, -current_vel_max, -current_vel_max * 0.9])
        self.paddle_velocity['left_slow'] = fuzz.trimf(self.velocity_universe, [-current_vel_max * 0.9, -current_vel_max * 0.7, -current_vel_max * 0.5])
        self.paddle_velocity['stop'] = fuzz.trimf(self.velocity_universe, [-current_vel_max * 0.5, 0, current_vel_max * 0.5])
        self.paddle_velocity['right_slow'] = fuzz.trimf(self.velocity_universe, [current_vel_max * 0.5, current_vel_max * 0.7, current_vel_max * 0.9])
        self.paddle_velocity['right_fast'] = fuzz.trimf(self.velocity_universe, [current_vel_max * 0.9, current_vel_max, current_vel_max])
        
        # Define fuzzy rules
        rules = [
            ctrl.Rule(self.x_diff['left'] & self.y_diff['far'], self.paddle_velocity['left_fast']),
            ctrl.Rule(self.x_diff['left'] & self.y_diff['medium'], self.paddle_velocity['left_fast']),
            ctrl.Rule(self.x_diff['center'], self.paddle_velocity['stop']),
            ctrl.Rule(self.x_diff['right'] & self.y_diff['medium'], self.paddle_velocity['right_fast']),
            ctrl.Rule(self.x_diff['right'] & self.y_diff['far'], self.paddle_velocity['right_fast']),
            ctrl.Rule(self.x_diff['left'] & self.y_diff['close'], self.paddle_velocity['left_slow']),
            ctrl.Rule(self.x_diff['right'] & self.y_diff['close'], self.paddle_velocity['right_slow'])]
        
        self.paddle_ctrl = ctrl.ControlSystem(rules)
        
        self.paddle_sim = ctrl.ControlSystemSimulation(self.paddle_ctrl)

    def reset_ball(self):
        self.ball.reset(self.width // 2, self.height // 2, 3.0, 3.0)
        self.player_paddle.speed = 3.0
        self.ai_paddle.speed = 3.0
        self.player_paddle.x = 500
        self.ai_paddle.x = 400
        self.create_paddle_simulation(3.0)

    def handle_events(self):
        """Handle keyboard and window events."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_paddle.move_left()
        if keys[pygame.K_RIGHT]:
            self.player_paddle.move_right()
        self.player_paddle.clamp(self.width)

        
        self.ball.move()

        # Ball collisions with side walls
        if self.ball.x - self.ball.radius <= 0 or self.ball.x + self.ball.radius >= self.width:
            self.ball.bounce_x()

        # Ball collision with player paddle 
        player_rect = pygame.Rect(self.player_paddle.x, self.player_paddle.y, self.player_paddle.width, self.player_paddle.height)
        ball_rect = pygame.Rect(self.ball.x - self.ball.radius, self.ball.y - self.ball.radius, self.ball.radius * 2, self.ball.radius * 2)

        if player_rect.colliderect(ball_rect) and self.ball.speed_y > 0:
            self.ball.bounce_y()
            self.ball.y = self.player_paddle.y - self.ball.radius
            self.increase_speed()
            self.ball_color = self.colors['dark']

        # Ball collision with fuzzy player paddle 

        ai_rect = pygame.Rect(self.ai_paddle.x, self.ai_paddle.y, self.ai_paddle.width, self.ai_paddle.height)
        ball_rect = pygame.Rect(self.ball.x - self.ball.radius, self.ball.y - self.ball.radius, self.ball.radius * 2, self.ball.radius * 2)

        if ai_rect.colliderect(ball_rect) and self.ball.speed_y < 0:
            self.ball.bounce_y()
            self.ball.y = self.ai_paddle.y + self.ai_paddle.height + self.ball.radius
            self.increase_speed()
            self.ball_color = self.colors['evil']

        
        if self.ball.y < 0:
            # fuzzy player scores
            self.reset_ball()
        elif self.ball.y > self.height:
            # Player scores 
            self.reset_ball()

        # === Fuzzy AI Decision ===

        x_diff_val = self.ball.x - (self.ai_paddle.x + self.ai_paddle.width / 2)
        y_diff_val = abs(self.ball.y - (self.ai_paddle.y + self.ai_paddle.height / 2))
        x_diff_val = max(-400, min(400, x_diff_val))
        y_diff_val = max(0, min(400, y_diff_val))
        
        self.paddle_sim.input['x_diff'] = x_diff_val
        self.paddle_sim.input['y_diff'] = y_diff_val

        try:
            self.paddle_sim.compute()
            move = float(self.paddle_sim.output.get('paddle_velocity', 0.0))
        except Exception as e:
            print("Fuzzy error:", e)
            move = 0.0
        
        self.ai_paddle.x += move
        self.ai_paddle.clamp(self.width)

    def increase_speed(self):
        """Increase ball and paddle speed after each bounce."""
        self.ball.speed_x = np.sign(self.ball.speed_x) * (abs(self.ball.speed_x) + self.growth)
        self.ball.speed_y = np.sign(self.ball.speed_y) * (abs(self.ball.speed_y) + self.growth)
        self.player_paddle.speed += self.growth
        self.ai_paddle.speed += self.growth
        self.create_paddle_simulation(abs(self.ball.speed_x))

    def draw(self):
        """Render all game elements."""
        self.screen.blit(self.background, (0, 0))
        pygame.draw.rect(self.screen, self.colors['dark'], (int(self.player_paddle.x), int(self.player_paddle.y), self.player_paddle.width, self.player_paddle.height))
        pygame.draw.rect(self.screen, self.colors['evil'], (int(self.ai_paddle.x), int(self.ai_paddle.y), self.ai_paddle.width, self.ai_paddle.height))
        pygame.draw.circle(self.screen, self.ball_color, (int(self.ball.x), int(self.ball.y)), self.ball.radius)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()