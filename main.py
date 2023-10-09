import pygame
import sys
import random

class FlappyBirdGame:
    def __init__(self):
        pygame.init()

        # Screen dimensions
        self.SCREEN_WIDTH = 576
        self.SCREEN_HEIGHT = 1024

        # Create the game screen and clock
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.game_font = pygame.font.Font('./asset/Font.ttf', 40)

        # Constants
        self.gravity = 0.25
        self.bird_movement = 0
        self.floor_speed = 5
        self.pipe_speed = 5
        self.game_active = True
        self.score = 0
        self.high_score = 0

        # Load and scale images
        self.background = self.load_and_scale_image('./asset/sprites/background-day.png')
        self.floor_background = self.load_and_scale_image('./asset/sprites/base.png')
        self.bird_frames = self.load_bird_frames()
        self.bird_index = 0
        self.bird_image = self.bird_frames[self.bird_index]
        self.bird_rect = self.bird_image.get_rect(center=(100, 512))
        self.BIRDFLAP = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BIRDFLAP, 200)
        self.pipe_image = self.load_and_scale_image('./asset/sprites/pipe-green.png')
        self.pipe_list = []
        self.SPAWN_PIPE = pygame.USEREVENT
        self.pipe_height = [400, 600, 800]
        self.game_over_image = self.load_and_scale_image('./asset/sprites/gameover.png')
        self.game_over_rect = self.game_over_image.get_rect(center=(288, 512))
        pygame.time.set_timer(self.SPAWN_PIPE, 1200)
        self.floor_x_position = 0

    def load_and_scale_image(self, image_path, scale=2):
        image = pygame.image.load(image_path).convert_alpha()
        return pygame.transform.scale2x(image)

    def load_bird_frames(self):
        bird_frames = [
            self.load_and_scale_image('./asset/sprites/yellowbird-downflap.png', scale=2),
            self.load_and_scale_image('./asset/sprites/yellowbird-midflap.png', scale=2),
            self.load_and_scale_image('./asset/sprites/yellowbird-upflap.png', scale=2)
        ]
        return bird_frames

    def create_pipe(self):
        random_pipe_pos = random.choice(self.pipe_height)
        bottom_pipe = self.pipe_image.get_rect(midtop=(700, random_pipe_pos))
        top_pipe = self.pipe_image.get_rect(midbottom=(700, random_pipe_pos - 300))
        return bottom_pipe, top_pipe

    def move_pipes(self, pipes):
        return [pipe.move(-self.pipe_speed, 0) for pipe in pipes]

    def draw_pipes(self, pipes):
        for pipe in pipes:
            if pipe.bottom >= 1024:
                self.screen.blit(self.pipe_image, pipe)
            else:
                flip_pipe = pygame.transform.flip(self.pipe_image, False, True)
                self.screen.blit(flip_pipe, pipe)
    
    def draw_floor(self, floor_x_position):
        self.screen.blit(self.floor_background, (floor_x_position, 900))
        self.screen.blit(self.floor_background, (floor_x_position + self.SCREEN_WIDTH, 900))

    def check_collision(self, pipes):
        return any(self.bird_rect.colliderect(pipe) for pipe in pipes) or self.bird_rect.top <= -100 or self.bird_rect.bottom >= 876

    def rotate_bird(self, bird):
        return pygame.transform.rotozoom(bird, -self.bird_movement * 3, 1)

    def bird_animation(self):
        new_bird = self.bird_frames[self.bird_index]
        new_bird_rect = new_bird.get_rect(center=(100, self.bird_rect.centery))
        return new_bird, new_bird_rect

    def score_display(self, game_state):
        if game_state == 'main_game':
            score_surface = self.game_font.render(str(self.score), True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(288, 100))
            self.screen.blit(score_surface, score_rect)
        if game_state == 'game_over':
            score_surface = self.game_font.render(f'Score: {self.score}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(288, 100))
            self.screen.blit(score_surface, score_rect)

            high_score_surface = self.game_font.render(f'High Score: {self.high_score}', True, (255, 255, 255))
            high_score_rect = high_score_surface.get_rect(center=(288, 592))
            self.screen.blit(high_score_surface, high_score_rect)

    def update_score(self):
        if self.score > self.high_score:
            self.high_score = self.score

    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_active:
                            self.bird_movement = 0
                            self.bird_movement -= 9
                        else:
                            self.game_active = True
                            self.pipe_list.clear()
                            self.bird_rect.center = (100, 512)
                            self.bird_movement = 0
                            self.score = 0
                if event.type == self.SPAWN_PIPE and self.game_active:
                    self.score += 1
                    self.pipe_list.extend(self.create_pipe())
                if event.type == self.BIRDFLAP:
                    self.bird_index = (self.bird_index + 1) % len(self.bird_frames)
                    self.bird_image, self.bird_rect = self.bird_animation()

            # Draw the background
            self.screen.blit(self.background, (0, 0))

            if self.game_active:
                self.bird_movement += self.gravity
                rotated_bird = self.rotate_bird(self.bird_image)
                self.bird_rect.centery += self.bird_movement
                self.screen.blit(rotated_bird, self.bird_rect)

                self.pipe_list = self.move_pipes(self.pipe_list)
                self.draw_pipes(self.pipe_list)
                self.game_active = not self.check_collision(self.pipe_list)

                self.score_display('main_game')
            else:
                self.screen.blit(self.game_over_image, self.game_over_rect)
                self.update_score()
                self.score_display('game_over')

            # Move the floor
            self.floor_x_position -= self.floor_speed

            # Draw the floor
            self.draw_floor(self.floor_x_position)

            # Reset the floor position when it goes off the screen
            if self.floor_x_position <= -self.SCREEN_WIDTH:
                self.floor_x_position = 0

            # Update the display
            pygame.display.update()

            # Set the frame rate
            self.clock.tick(120)

if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run_game()
