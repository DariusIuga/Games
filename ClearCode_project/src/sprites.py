from dataclasses import dataclass
from random import choice, randint, random
from sys import exit

import pygame


# This is a simple dataclass used for grouping surfaces and rectangles.
# It is useful for simple sprites that don't need methods for movement, input, checking collisions etc.
@dataclass(frozen=True, order=True)
class Surf_Rect(pygame.sprite.Sprite):
    surf: pygame.Surface
    rect: pygame.Rect


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        width,
        GROUND_LEVEL,
        PLAYER_DIMS,
        healthup_group,
        freeze_group,
        reverse_group,
    ):
        super().__init__()

        walk_1 = pygame.image.load(
            "../graphics/Player/player_walk_1.png"
        ).convert_alpha()
        walk_1 = pygame.transform.scale(walk_1, PLAYER_DIMS)
        walk_2 = pygame.image.load(
            "../graphics/Player/player_walk_2.png"
        ).convert_alpha()
        walk_2 = pygame.transform.scale(walk_2, PLAYER_DIMS)
        self.walk = [walk_1, walk_2]
        self.animation_index = 0

        self.jump_frame = pygame.image.load(
            "../graphics/Player/jump.png"
        ).convert_alpha()
        self.jump_frame = pygame.transform.scale(self.jump_frame, PLAYER_DIMS)

        self.image = self.walk[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(width / 8, GROUND_LEVEL))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound("../audio/jump.mp3")
        self.jump_sound.set_volume(0.2)

        self.hit_sound = pygame.mixer.Sound("../audio/vine-boom.mp3")
        self.hit_sound.set_volume(0.3)
        
        self.drink_sound = pygame.mixer.Sound("../audio/minecraft-drinking-sound-effect.mp3")
        self.drink_sound.set_volume(0.3)
        
        self.time_stop_sound = pygame.mixer.Sound("../audio/za_warudo.mp3")
        self.time_stop_sound.set_volume(0.2)
        
        self.reverse_sound = pygame.mixer.SoundType("../audio/swoosh.wav")
        self.reverse_sound.set_volume(0.5)

        self._starting_health = 3
        self.lives = self._starting_health
        self.drunkennes = 0

    def move(self, width, height, GROUND_LEVEL):
        # Control the player
        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        ) and self.rect.bottom >= GROUND_LEVEL:
            self.gravity = -height * (1 / 20 - self.drunkennes / 50)
            self.jump_sound.play()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= width / 200 * (1 - self.drunkennes / 2)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += width / 200 * (1 - self.drunkennes / 2)

        # Prevent player from going out of bounds
        if self.rect.left <= 0:
            self.rect.left = 20
        elif self.rect.right >= width:
            self.rect.right = width - 20

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

    def check_collision(
        self, obstacle_group, healthup_group, freeze_group, reverse_group, GROUND_LEVEL
    ):
        if pygame.sprite.spritecollide(self, obstacle_group, True):
            self.hit_sound.play()
            self.lives -= 1
            if self.lives == 0:
                self.rect.bottom = GROUND_LEVEL
                self.rect.left = 0
                obstacle_group.empty()
                healthup_group.empty()
                freeze_group.empty()
                reverse_group.empty()

    def heal(self, healthup_group):
        if pygame.sprite.spritecollide(self, healthup_group, True):
            self.lives += 1
            self.drink_sound.play()
            if self.drunkennes < 1:
                self.drunkennes += 0.1

    def revive(self):
        self.lives = self._starting_health
        self.drunkennes = 0

    def freeze(self, obstacle_group, freeze_group):
        if pygame.sprite.spritecollide(self, freeze_group, True):
            self.time_stop_sound.play()
            for obstacle in obstacle_group:
                obstacle.freeze()

    def reverse(self, obstacle_group, reverse_group):
        if pygame.sprite.spritecollide(self, reverse_group, True):
            self.reverse_sound.play()
            for obstacle in obstacle_group:
                obstacle.reverse()

    def update(
        self,
        width,
        height,
        GROUND_LEVEL,
        obstacle_group,
        healthup_group,
        freeze_group,
        reverse_group,
    ):
        self.move(width, height, GROUND_LEVEL)
        self.apply_gravity(height, GROUND_LEVEL)
        self.animation_state(GROUND_LEVEL)
        self.check_collision(
            obstacle_group, healthup_group, freeze_group, reverse_group, GROUND_LEVEL
        )
        self.heal(healthup_group)
        self.freeze(obstacle_group, freeze_group)
        self.reverse(obstacle_group, reverse_group)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, width, height, GROUND_LEVEL, ENEMY_DIMS, type):
        super().__init__()
        self.type = type

        self.is_frozen = False
        self.freeze_start_time = 0
        self.direction_vector = 1

        if self.type == "fly":
            fly_frame_1 = pygame.image.load("../graphics/Fly/Fly1.png").convert_alpha()
            fly_frame_1 = pygame.transform.scale(fly_frame_1, ENEMY_DIMS)
            fly_frame_2 = pygame.image.load("../graphics/Fly/Fly2.png").convert_alpha()
            fly_frame_2 = pygame.transform.scale(fly_frame_2, ENEMY_DIMS)
            self.frames = [fly_frame_1, fly_frame_2]
            y_pos = randint(height / 5, height / 2)

        elif self.type == "snail":
            snail_frame_1 = pygame.image.load(
                "../graphics/snail/snail1.png"
            ).convert_alpha()
            snail_frame_1 = pygame.transform.scale(snail_frame_1, ENEMY_DIMS)
            snail_frame_2 = pygame.image.load(
                "../graphics/snail/snail2.png"
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

    def move(self, width):
        if not self.is_frozen:
            self.rect.x -= (width / 200) * self.direction_vector

        elif pygame.time.get_ticks() - self.freeze_start_time >= 2000:
            # Unfreeze this enemy after 2000ms
            self.is_frozen = False
            self.freeze_start_time = 0

    def freeze(self):
        self.is_frozen = True
        self.freeze_start_time = pygame.time.get_ticks()

    def reverse(self):
        # Should change direction every time the arrows are touched
        self.direction_vector = -self.direction_vector

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

    def update(self, width):
        self.animation_state()
        self.move(width)
        self.destroy()


class Consumable(pygame.sprite.Sprite):
    def __init__(self, width, height, GROUND_LEVEL, type):
        super().__init__()
        if type == "beer":
            image_path = "../graphics/beer.png"
        elif type == "hourglass":
            image_path = "../graphics/hourglass.png"
        elif type == "arrows":
            image_path = "../graphics/arrows.png"
        else:
            raise ValueError("Invalid consumable type")
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width / 10, height / 10))
        self.rect = self.image.get_rect(
            center=(randint(0, width), randint(0, GROUND_LEVEL))
        )
