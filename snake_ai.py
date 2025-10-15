# AI-Enhanced Snake Game with A* Pathfinding
# This version integrates the A* algorithm for automated gameplay

import pygame
import time
import random
from astar_pathfinding import SnakeAI

# Game configuration
snake_speed = 15
window_x = 720
window_y = 480

# Colors
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
yellow = pygame.Color(255, 255, 0)

# Game modes
MANUAL_MODE = "manual"
AI_MODE = "ai"

class SnakeGame:
    """
    Enhanced Snake game with AI capabilities using A* pathfinding.
    """
    
    def __init__(self):
        pygame.init()
        self.window_x = window_x
        self.window_y = window_y
        self.game_window = pygame.display.set_mode((self.window_x, self.window_y))
        pygame.display.set_caption('AI Snake Game with A* Pathfinding')
        self.fps = pygame.time.Clock()
        
        # Initialize AI
        self.snake_ai = SnakeAI(self.window_x, self.window_y)
        
        # Game state
        self.reset_game()
        self.game_mode = MANUAL_MODE  # Start in manual mode
        self.path_visualization = []  # For visualizing A* path
        
    def reset_game(self):
        """Reset the game to initial state"""
        self.snake_position = [100, 50]
        self.snake_body = [[100, 50], [90, 50], [80, 50], [70, 50]]
        self.fruit_position = [random.randrange(1, (self.window_x // 10)) * 10,
                              random.randrange(1, (self.window_y // 10)) * 10]
        self.fruit_spawn = True
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.score = 0
        self.path_visualization = []
        
    def show_score(self, color, font, size):
        """Display current score"""
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render('Score: ' + str(self.score), True, color)
        score_rect = score_surface.get_rect()
        self.game_window.blit(score_surface, score_rect)
        
    def show_mode(self):
        """Display current game mode"""
        mode_font = pygame.font.SysFont('arial', 20)
        mode_text = f"Mode: {'AI (A*)' if self.game_mode == AI_MODE else 'Manual'}"
        mode_surface = mode_font.render(mode_text, True, yellow)
        mode_rect = mode_surface.get_rect()
        mode_rect.topright = (self.window_x - 10, 10)
        self.game_window.blit(mode_surface, mode_rect)
        
    def show_instructions(self):
        """Display control instructions"""
        instruction_font = pygame.font.SysFont('arial', 16)
        instructions = [
            "Space: Toggle AI/Manual mode",
            "Arrow Keys: Manual control",
            "R: Reset game"
        ]
        
        y_offset = 40
        for instruction in instructions:
            instruction_surface = instruction_font.render(instruction, True, white)
            instruction_rect = instruction_surface.get_rect()
            instruction_rect.topright = (self.window_x - 10, y_offset)
            self.game_window.blit(instruction_surface, instruction_rect)
            y_offset += 20
            
    def visualize_path(self, path):
        """Visualize the A* path on screen"""
        if not path:
            return
            
        for i, pos in enumerate(path):
            # Draw path with decreasing opacity
            alpha = max(50, 255 - (i * 20))
            color = (*blue[:3], alpha)  # Blue with alpha
            
            # Create a surface with per-pixel alpha
            path_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            path_surface.fill(color)
            
            # Center the path marker in the cell
            rect = pygame.Rect(pos[0] + 1, pos[1] + 1, 8, 8)
            self.game_window.blit(path_surface, rect)
    
    def game_over(self):
        """Handle game over state"""
        my_font = pygame.font.SysFont('times new roman', 50)
        game_over_surface = my_font.render(
            f'Final Score: {self.score}', True, red)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (self.window_x / 2, self.window_y / 4) # type: ignore
        
        self.game_window.blit(game_over_surface, game_over_rect)
        
        # Show restart instruction
        restart_font = pygame.font.SysFont('arial', 30)
        restart_surface = restart_font.render('Press R to restart', True, white)
        restart_rect = restart_surface.get_rect()
        restart_rect.midtop = (self.window_x / 2, self.window_y / 2) # type: ignore
        self.game_window.blit(restart_surface, restart_rect)
        
        pygame.display.flip()
        return True  # Game over
        
    def handle_events(self):
        """Handle keyboard input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit game
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Toggle between AI and manual mode
                    self.game_mode = AI_MODE if self.game_mode == MANUAL_MODE else MANUAL_MODE
                    print(f"Switched to {self.game_mode.upper()} mode")
                    
                elif event.key == pygame.K_r:
                    # Reset game
                    self.reset_game()
                    print("Game reset")
                    
                # Manual controls (only active in manual mode)
                elif self.game_mode == MANUAL_MODE:
                    if event.key == pygame.K_UP:
                        self.change_to = 'UP'
                    elif event.key == pygame.K_DOWN:
                        self.change_to = 'DOWN'
                    elif event.key == pygame.K_LEFT:
                        self.change_to = 'LEFT'
                    elif event.key == pygame.K_RIGHT:
                        self.change_to = 'RIGHT'
        
        return True  # Continue game
    
    def update_direction(self):
        """Update snake direction based on current mode"""
        if self.game_mode == AI_MODE:
            # Get AI decision
            ai_direction = self.snake_ai.get_next_move(
                self.snake_position, 
                self.fruit_position, 
                self.snake_body
            )
            self.change_to = ai_direction
            
            # Get path for visualization
            path = self.snake_ai.pathfinder.find_path(
                self.snake_position, 
                self.fruit_position, 
                self.snake_body
            )
            self.path_visualization = path if path else []
        else:
            # Clear path visualization in manual mode
            self.path_visualization = []
        
        # Validate direction change (prevent 180-degree turns)
        if self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        elif self.change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        elif self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        elif self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'
    
    def move_snake(self):
        """Move snake based on current direction"""
        if self.direction == 'UP':
            self.snake_position[1] -= 10
        elif self.direction == 'DOWN':
            self.snake_position[1] += 10
        elif self.direction == 'LEFT':
            self.snake_position[0] -= 10
        elif self.direction == 'RIGHT':
            self.snake_position[0] += 10
    
    def check_food_collision(self):
        """Check if snake ate food and handle growth"""
        self.snake_body.insert(0, list(self.snake_position))
        
        if (self.snake_position[0] == self.fruit_position[0] and 
            self.snake_position[1] == self.fruit_position[1]):
            self.score += 10
            self.fruit_spawn = False
        else:
            self.snake_body.pop()
        
        # Spawn new food
        if not self.fruit_spawn:
            self.fruit_position = [
                random.randrange(1, (self.window_x // 10)) * 10,
                random.randrange(1, (self.window_y // 10)) * 10
            ]
        self.fruit_spawn = True
    
    def check_collisions(self):
        """Check for wall and self collisions"""
        # Wall collision
        if (self.snake_position[0] < 0 or self.snake_position[0] > self.window_x - 10 or
            self.snake_position[1] < 0 or self.snake_position[1] > self.window_y - 10):
            return True
        
        # Self collision
        for block in self.snake_body[1:]:
            if (self.snake_position[0] == block[0] and 
                self.snake_position[1] == block[1]):
                return True
        
        return False
    
    def render(self):
        """Render the game state"""
        self.game_window.fill(black)
        
        # Draw A* path visualization (only in AI mode)
        if self.game_mode == AI_MODE and self.path_visualization:
            self.visualize_path(self.path_visualization)
        
        # Draw snake
        for pos in self.snake_body:
            pygame.draw.rect(self.game_window, green, 
                           pygame.Rect(pos[0], pos[1], 10, 10))
        
        # Draw food
        pygame.draw.rect(self.game_window, white, 
                        pygame.Rect(self.fruit_position[0], self.fruit_position[1], 10, 10))
        
        # Draw UI
        self.show_score(white, 'times new roman', 20)
        self.show_mode()
        self.show_instructions()
        
        pygame.display.update()
    
    def run(self):
        """Main game loop"""
        running = True
        game_over_state = False
        
        print("Snake AI Game Started!")
        print("Controls:")
        print("- SPACE: Toggle between AI and Manual mode")
        print("- Arrow Keys: Manual control (when in manual mode)")
        print("- R: Reset game")
        print("- Close window to exit")
        
        while running:
            # Handle events
            running = self.handle_events()
            if not running:
                break
            
            if not game_over_state:
                # Update game logic
                self.update_direction()
                self.move_snake()
                self.check_food_collision()
                
                # Check for game over
                if self.check_collisions():
                    game_over_state = True
                
                # Render game
                self.render()
            else:
                # Game over state
                if self.game_over():
                    # Wait for restart
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            self.reset_game()
                            game_over_state = False
                        elif event.type == pygame.QUIT:
                            running = False
            
            # Control frame rate
            self.fps.tick(snake_speed)
        
        pygame.quit()
        quit()


# Demo function to show algorithm in action
def run_ai_demo():
    """Run a demo showing the AI in action"""
    print("Starting AI Snake Demo with A* Pathfinding...")
    print("The snake will automatically navigate to food using A* algorithm.")
    print("Watch the blue path visualization to see the algorithm's decisions!")
    
    game = SnakeGame()
    game.game_mode = AI_MODE  # Start in AI mode
    game.run()


if __name__ == "__main__":
    # You can run either the full game or just the AI demo
    choice = input("Choose mode:\n1. Full Game (with manual/AI toggle)\n2. AI Demo\nEnter 1 or 2: ").strip()
    
    if choice == "2":
        run_ai_demo()
    else:
        game = SnakeGame()
        game.run()