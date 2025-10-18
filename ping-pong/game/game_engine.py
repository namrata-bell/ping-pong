import pygame
from .paddle import Paddle
from .ball import Ball

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

class GameEngine:
    def __init__(self, width, height, paddle_hit_sound=None, wall_bounce_sound=None, score_sound=None):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height,
                         paddle_hit_sound=paddle_hit_sound,
                         wall_bounce_sound=wall_bounce_sound,
                         score_sound=score_sound)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        
        self.winning_score = 5
        self.game_over = False
        self.winner = None
        self.game_over_font = pygame.font.SysFont("Arial", 60)
        self.instruction_font = pygame.font.SysFont("Arial", 24)
        
        self.score_processed_this_frame = False

    def handle_input(self):
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)

    def update(self):
        if self.game_over:
            return
        self.score_processed_this_frame = False
        self.ball.move()
        self.ball.check_collision(self.player, self.ai)
        self.ai.auto_track(self.ball, self.height)

        if not self.score_processed_this_frame:
            if self.ball.x <= 0:
                self.ai_score += 1
                self.score_processed_this_frame = True
                self.check_game_over()
                if not self.game_over:
                    self.ball.reset()
            elif self.ball.x >= self.width:
                self.player_score += 1
                self.score_processed_this_frame = True
                self.check_game_over()
                if not self.game_over:
                    self.ball.reset()

    def check_game_over(self):
        if self.player_score >= self.winning_score:
            self.game_over = True
            self.winner = "Player"
            self.ball.reset()
        elif self.ai_score >= self.winning_score:
            self.game_over = True
            self.winner = "AI"
            self.ball.reset()

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = None
        self.ball.reset()
        self.player.y = self.height // 2 - 50
        self.ai.y = self.height // 2 - 50
        self.score_processed_this_frame = False

    def render(self, screen):
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))

    def render_game_over(self, screen):
        if not self.game_over:
            return False
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        winner_text = f"{self.winner} Wins!"
        text_surface = self.game_over_font.render(winner_text, True, YELLOW)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 40))
        screen.blit(text_surface, text_rect)
        instruction_text = "Press 3, 5, or 7 for Best of X, or ESC to quit"
        instruction_surface = self.instruction_font.render(instruction_text, True, GRAY)
        instruction_rect = instruction_surface.get_rect(center=(self.width // 2, self.height // 2 + 40))
        screen.blit(instruction_surface, instruction_rect)
        pygame.display.flip()
        return True

    def handle_replay_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {'action': 'quit'}
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_3:
                    return {'action': 'restart', 'best_of': 3}
                elif event.key == pygame.K_5:
                    return {'action': 'restart', 'best_of': 5}
                elif event.key == pygame.K_7:
                    return {'action': 'restart', 'best_of': 7}
                elif event.key == pygame.K_ESCAPE:
                    return {'action': 'quit'}
        return None

    def apply_replay_choice(self, best_of):
        self.winning_score = best_of
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = None
        self.ball.reset()
        self.player.y = self.height // 2 - self.paddle_height // 2
        self.ai.y = self.height // 2 - self.paddle_height // 2
        self.score_processed_this_frame = False
