from random import choice, randint
from sys import exit

import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, width, GROUND_LEVEL, PLAYER_DIMS):
        super().__init__()

        walk_1 = pygame.image.load("graphics/Player/player_walk_1.png").convert_alpha()
        walk_1 = pygame.transform.scale(walk_1, PLAYER_DIMS)
        walk_2 = pygame.image.load("graphics/Player/player_walk_2.png").convert_alpha()
        walk_2 = pygame.transform.scale(walk_2, PLAYER_DIMS)
        self.walk = [walk_1, walk_2]
        self.animation_index = 0

        self.jump_frame = pygame.image.load("graphics/Player/jump.png").convert_alpha()
        self.jump_frame = pygame.transform.scale(self.jump_frame, PLAYER_DIMS)

        self.image = self.walk[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(width / 8, GROUND_LEVEL))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound("audio/jump.mp3")
        self.jump_sound.set_volume(0.2)

    def jump(self, GROUND_LEVEL):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= GROUND_LEVEL:
            self.gravity = -50
            self.jump_sound.play()

    def apply_gravity(self, height, GROUND_LEVEL):
        self.gravity += height / 500
        self.rect.y += self.gravity
        if self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL

    def animation_state(self, GROUND_LEVEL):
        if self.rect.bottom < GROUND_LEVEL:
            self.image = self.jump_frame
        else:
            self.animation_index += 0.1
            if self.animation_index >= len(self.walk):
                self.animation_index = 0
            self.image = self.walk[int(self.animation_index)]

    def update(self, height, GROUND_LEVEL):
        self.jump(GROUND_LEVEL)
        self.apply_gravity(height, GROUND_LEVEL)
        self.animation_state(GROUND_LEVEL)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, width, height, GROUND_LEVEL, ENEMY_DIMS, type):
        super().__init__()
        self.type = type
        if self.type == "fly":
            fly_frame_1 = pygame.image.load("graphics/Fly/Fly1.png").convert_alpha()
            fly_frame_1 = pygame.transform.scale(fly_frame_1, ENEMY_DIMS)
            fly_frame_2 = pygame.image.load("graphics/Fly/Fly2.png").convert_alpha()
            fly_frame_2 = pygame.transform.scale(fly_frame_2, ENEMY_DIMS)
            self.frames = [fly_frame_1, fly_frame_2]
            y_pos = randint(height / 4, height / 2)
        elif self.type == "snail":
            snail_frame_1 = pygame.image.load(
                "graphics/snail/snail1.png"
            ).convert_alpha()
            snail_frame_1 = pygame.transform.scale(snail_frame_1, ENEMY_DIMS)
            snail_frame_2 = pygame.image.load(
                "graphics/snail/snail2.png"
            ).convert_alpha()
            snail_frame_2 = pygame.transform.scale(snail_frame_2, ENEMY_DIMS)
            self.frames = [snail_frame_1, snail_frame_2]
            y_pos = GROUND_LEVEL
        else:
            raise ValueError("Invalid enemy type, choose from 'fly' or 'snail'.")

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(randint(width, width * 1.5), y_pos))

    def animation_state(self):
        if self.type == "fly":
            self.animation_index += 0.2
        elif self.type == "snail":
            self.animation_index += 0.1
        else:
            raise ValueError("Invalid enemy type, choose from 'fly' or 'snail'.")

        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

    def update(self, width):
        self.animation_state()
        self.rect.x -= width / 200
        self.destroy()


def main():
    pygame.init()

    # If the dimensions are set to 0, the game runs in fullscreen
    screen = pygame.display.set_mode((0, 0))
    width, height = screen.get_size()
    GROUND_LEVEL = 3 * height / 4
    MESSAGE_COLOR = (111, 196, 169)
    PLAYER_DIMS = (width / 16, height / 6)
    ENEMY_DIMS = (width / 16, height / 16)

    pygame.display.set_caption("Pixel Runner")
    clock = pygame.time.Clock()
    default_font = pygame.font.Font("fonts/Pixeltype.ttf", 100)
    game_active = False
    start_time = 0
    current_score = 0
    highscore = 0
    background_music = pygame.mixer.Sound("audio/secret.opus")
    background_music.play(loops=-1)

    # Groups
    player = pygame.sprite.GroupSingle()
    player.add(Player(width, GROUND_LEVEL, PLAYER_DIMS))

    obstacle_group = pygame.sprite.Group()

    # Textures
    ground = pygame.image.load("graphics/ground.png").convert()
    ground = pygame.transform.scale(ground, (width, height - GROUND_LEVEL))
    sky = pygame.image.load("graphics/sky.png").convert()
    sky = pygame.transform.scale(sky, (width, GROUND_LEVEL))

    # Menu screen
    player_stand = pygame.image.load("graphics/Player/player_stand.png").convert_alpha()
    player_stand = pygame.transform.scale(player_stand, (width / 8, height / 4))
    player_stand_rect = player_stand.get_rect(midbottom=(width / 2, height / 2))

    game_name = default_font.render("Pixel runner", None, MESSAGE_COLOR)
    game_name_rect = game_name.get_rect(center=(width / 2, height / 5))

    game_message = default_font.render("Press any key", None, MESSAGE_COLOR)
    game_message_rect = game_message.get_rect(center=(width / 2, 2 * height / 3))

    # Timers
    spawn_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_timer, 600)

    snail_animation_timer = pygame.USEREVENT + 2
    pygame.time.set_timer(snail_animation_timer, 400)

    fly_animation_timer = pygame.USEREVENT + 3
    pygame.time.set_timer(fly_animation_timer, 200)

    while True:
        # Process user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if game_active:
                if event.type == spawn_timer:
                    # Chance of spawning either a snail or fly
                    obstacle_group.add(
                        Obstacle(
                            width,
                            height,
                            GROUND_LEVEL,
                            ENEMY_DIMS,
                            choice(["fly", "snail"]),
                        )
                    )

            else:
                # Press any button to continue
                if event.type == pygame.KEYDOWN:
                    game_active = True
                    start_time = pygame.time.get_ticks()

        if game_active:
            # Render screen
            screen.blit(sky, (0, 0))
            screen.blit(ground, (0, GROUND_LEVEL))

            screen.blit(
                default_font.render(str(int(clock.get_fps())), False, "green"), (0, 0)
            )

            current_score, highscore = display_score(
                width, height, screen, default_font, start_time, highscore
            )

            score_message = default_font.render(
                f"Your score is: {current_score}", False, MESSAGE_COLOR
            )
            score_message_rect = score_message.get_rect(
                midbottom=(width / 2, 2 * height / 3)
            )
            highscore_message = default_font.render(
                f"Highscore: {highscore}", False, MESSAGE_COLOR
            )
            highscore_message_rect = highscore_message.get_rect(
                midtop=(width / 2, 2 * height / 3)
            )

            game_active = collision_sprite(player, obstacle_group, GROUND_LEVEL)

            # Draw the sprites
            player.draw(screen)
            player.update(height, GROUND_LEVEL)
            obstacle_group.draw(screen)
            obstacle_group.update(width)

        else:
            # Game Over screen
            # player_rect.midbottom = (width / 8, GROUND_LEVEL)
            screen.fill((94, 129, 162))
            screen.blit(player_stand, player_stand_rect)
            screen.blit(game_name, game_name_rect)
            if current_score == 0:
                screen.blit(game_message, game_message_rect)
            else:
                screen.blit(score_message, score_message_rect)
                screen.blit(highscore_message, highscore_message_rect)
                if current_score == 69 or highscore == 69:
                    raise ValueError("Nice")

        pygame.display.update()
        # Cap the refresh rate to 60fps
        clock.tick(60)


def display_score(width, height, screen, default_font, start_time, highscore):
    current_score = pygame.time.get_ticks() - start_time
    current_score //= 1000
    score_surf = default_font.render(f"Score: {current_score}", False, (128, 128, 128))
    score_rect = score_surf.get_rect(center=(width / 2, height / 16))
    pygame.draw.rect(
        screen,
        "#9ad6c3",
        pygame.Rect(
            # Centering the title box
            score_rect.left - 30,
            score_rect.top - 15,
            score_rect.width * 1.2,
            score_rect.height * 1.2,
        ),
        0,
        20,
    )
    screen.blit(score_surf, score_rect)

    if highscore < current_score:
        highscore = current_score

    return current_score, highscore


def collision_sprite(player, obstacle_group, GROUND_LEVEL):
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        player.sprite.rect.bottom = GROUND_LEVEL
        return False
    return True


if __name__ == "__main__":
    main()
