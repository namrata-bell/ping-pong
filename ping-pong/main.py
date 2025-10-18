import pygame
import os
from game.game_engine import GameEngine

os.environ.setdefault("SDL_AUDIODRIVER", "directsound")

# Initialize pygame/Start application
pygame.init()
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"⚠️ Audio system not initialized: {e}")

# Screen dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong - Pygame Version")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Load sound effects with error handling
def load_sound(filename):
    """Load sound file with fallback for missing files"""
    try:
        sound_path = os.path.join("sounds", filename)
        sound = pygame.mixer.Sound(sound_path)
        return sound
    except FileNotFoundError:
        print(f"Warning: Sound file '{filename}' not found. Game will continue without this sound.")
        return None
    except pygame.error as e:
        print(f"Warning: Could not load sound '{filename}': {e}. Game will continue.")
        return None

# Load all sounds
SOUND_PADDLE_HIT = load_sound("paddle_hit.wav")
SOUND_WALL_BOUNCE = load_sound("wall_bounce.wav")
SOUND_SCORE = load_sound("score.wav")

# Set volume levels (adjust as needed)
if SOUND_PADDLE_HIT:
    SOUND_PADDLE_HIT.set_volume(0.5)
if SOUND_WALL_BOUNCE:
    SOUND_WALL_BOUNCE.set_volume(0.3)
if SOUND_SCORE:
    SOUND_SCORE.set_volume(0.7)

# Create game engine with sounds
engine = GameEngine(WIDTH, HEIGHT,
                   paddle_hit_sound=SOUND_PADDLE_HIT,
                   wall_bounce_sound=SOUND_WALL_BOUNCE,
                   score_sound=SOUND_SCORE)

def main():
    running = True
    while running:
        SCREEN.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Only handle player input if game is active
        if not engine.game_over:
            engine.handle_input()
            engine.update()
            engine.render(SCREEN)
            pygame.display.flip()
        else:
            # Game over state: show replay screen and handle replay input
            engine.render(SCREEN)  # Render final game state
            pygame.display.flip()
            engine.render_game_over(SCREEN)  # Show overlay with replay options
            
            # Handle replay input (non-blocking)
            replay_choice = engine.handle_replay_input()
            
            if replay_choice:
                if replay_choice['action'] == 'quit':
                    running = False
                elif replay_choice['action'] == 'restart':
                    engine.apply_replay_choice(replay_choice['best_of'])

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
