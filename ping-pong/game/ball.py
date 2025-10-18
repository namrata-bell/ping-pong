
import pygame
import random

class Ball:
    def __init__(self, x, y, width, height, screen_width, screen_height,
                 paddle_hit_sound=None, wall_bounce_sound=None, score_sound=None):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Store previous position for swept collision checks
        self.prev_x = x
        self.prev_y = y
        
        # Collision cooldown to prevent double-hits
        self.last_collision_time = 0
        self.collision_cooldown_ms = 100  # 100ms cooldown between paddle hits
        
        # Wall bounce cooldown to prevent double wall bounces in same frame
        self.last_wall_bounce_time = 0
        self.wall_bounce_cooldown_ms = 50
        
        # Sound references
        self.paddle_hit_sound = paddle_hit_sound
        self.wall_bounce_sound = wall_bounce_sound
        self.score_sound = score_sound
        
        # Initialize velocity with proper randomization
        self.reset_velocity()
        
    def reset_velocity(self):
        """Reset ball velocity with proper angle constraints"""
        # Ensure minimum vertical component to avoid purely horizontal movement
        self.velocity_x = random.choice([-5, 5])
        # Use larger vertical values to ensure interesting angles
        self.velocity_y = random.choice([-4, -3, 3, 4])
        
        # Enforce minimum angle (avoid near-horizontal shots)
        if abs(self.velocity_y) < 2:
            self.velocity_y = 2 * (1 if self.velocity_y > 0 else -1)
    
    def reset(self):
        """Reset ball to center with new random velocity and play score sound"""
        self.x = self.original_x
        self.y = self.original_y
        self.prev_x = self.x
        self.prev_y = self.y
        self.reset_velocity()
        
        # Reset collision cooldowns
        self.last_collision_time = 0
        self.last_wall_bounce_time = 0
        
        # Play score sound (async, non-blocking)
        if self.score_sound:
            self.score_sound.play()
    
    def move(self):
        """Move ball and handle wall collisions with sound"""
        # Store previous position (used by swept collision detection)
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Apply velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        current_time = pygame.time.get_ticks()
        
        # Bounce off top/bottom walls with sound and cooldown
        if self.y <= 0:
            self.y = 0
            self.velocity_y = abs(self.velocity_y)  # Force positive (downward)
            
            # Play wall bounce sound with cooldown to prevent double-trigger
            if self.wall_bounce_sound and (current_time - self.last_wall_bounce_time) >= self.wall_bounce_cooldown_ms:
                self.wall_bounce_sound.play()
                self.last_wall_bounce_time = current_time
                
        elif self.y + self.height >= self.screen_height:
            self.y = self.screen_height - self.height
            self.velocity_y = -abs(self.velocity_y)  # Force negative (upward)
            
            # Play wall bounce sound with cooldown
            if self.wall_bounce_sound and (current_time - self.last_wall_bounce_time) >= self.wall_bounce_cooldown_ms:
                self.wall_bounce_sound.play()
                self.last_wall_bounce_time = current_time
        
        # Clamp ball position within screen bounds (prevent wall tunneling)
        self.x = max(0, min(self.x, self.screen_width - self.width))
        self.y = max(0, min(self.y, self.screen_height - self.height))
    
    def check_collision(self, player, ai):
        """
        Use a swept rectangle (bounding box between previous and current ball positions)
        to detect collisions even when the ball moves fast.
        Includes edge case handling for:
        - Double-hit prevention (cooldown)
        - Overlap/sticking mitigation
        - Collision order priority
        - Sound effects on paddle hit
        """
        current_time = pygame.time.get_ticks()
        
        # Collision cooldown: prevent rapid double-hits
        if current_time - self.last_collision_time < self.collision_cooldown_ms:
            return
        
        # Current ball rect and previous ball rect
        curr = self.rect()
        prev = pygame.Rect(self.prev_x, self.prev_y, self.width, self.height)
        
        # Swept rect covers both prev and curr positions (prevents tunneling)
        swept_x = min(prev.x, curr.x)
        swept_y = min(prev.y, curr.y)
        swept_w = max(prev.right, curr.right) - swept_x
        swept_h = max(prev.bottom, curr.bottom) - swept_y
        swept = pygame.Rect(swept_x, swept_y, swept_w, swept_h)
        
        # Check paddle collisions using swept rect
        # Priority: Check player paddle first, then AI (prevents ambiguous double-collision)
        
        # Left paddle (player)
        if swept.colliderect(player.rect()) or curr.colliderect(player.rect()):
            # Only process if ball is moving toward the paddle
            if self.velocity_x < 0:
                # Reverse horizontal direction
                self.velocity_x = abs(self.velocity_x)  # Force positive (rightward)
                
                # Nudge ball outside paddle with safety margin (prevents sticking)
                self.x = player.x + player.width + 1
                
                # Adaptive vertical angle based on hit position
                paddle_center = player.y + player.height / 2
                ball_center = self.y + self.height / 2
                relative_intersect = (ball_center - paddle_center) / (player.height / 2)
                self.velocity_y += relative_intersect * 0.5
                
                # Play paddle hit sound
                if self.paddle_hit_sound:
                    self.paddle_hit_sound.play()
                
                # Record collision time
                self.last_collision_time = current_time
                
                # Clamp position to prevent wall overlap
                self.x = max(0, min(self.x, self.screen_width - self.width))
                return  # Exit early to prevent double-collision in same frame
        
        # Right paddle (AI)
        if swept.colliderect(ai.rect()) or curr.colliderect(ai.rect()):
            # Only process if ball is moving toward the paddle
            if self.velocity_x > 0:
                # Reverse horizontal direction
                self.velocity_x = -abs(self.velocity_x)  # Force negative (leftward)
                
                # Nudge ball to be left of the AI paddle with safety margin
                self.x = ai.x - self.width - 1
                
                # Adaptive vertical angle
                paddle_center = ai.y + ai.height / 2
                ball_center = self.y + self.height / 2
                relative_intersect = (ball_center - paddle_center) / (ai.height / 2)
                self.velocity_y += relative_intersect * 0.5
                
                # Play paddle hit sound
                if self.paddle_hit_sound:
                    self.paddle_hit_sound.play()
                
                # Record collision time
                self.last_collision_time = current_time
                
                # Clamp position to prevent wall overlap
                self.x = max(0, min(self.x, self.screen_width - self.width))
                return  # Exit early
    
    def rect(self):
        """Return pygame Rect for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen, color=(255, 255, 255)):
        """Draw the ball on screen"""
        pygame.draw.ellipse(screen, color, self.rect())
    
    def is_out_of_bounds(self):
        """Check if ball has gone past paddles (scoring condition)"""
        return self.x <= 0 or self.x + self.width >= self.screen_width 