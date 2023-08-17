from sprites import *


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
    start_time = 0
    current_score = 0
    highscore = 0
    background_music = pygame.mixer.Sound("audio/epic.opus")
    background_music.play(loops=-1)

    # Groups
    obstacle_group = pygame.sprite.Group()
    consumable_group = pygame.sprite.Group()
    player = pygame.sprite.GroupSingle()
    player.add(Player(width, GROUND_LEVEL, PLAYER_DIMS, consumable_group))

    # Textures
    ground = pygame.image.load("graphics/ground.png").convert()
    ground = pygame.transform.scale(ground, (width, height - GROUND_LEVEL))
    sky = pygame.image.load("graphics/sky.png").convert()
    sky = pygame.transform.scale(sky, (width, GROUND_LEVEL))
    heart = pygame.image.load("graphics/heart.png")
    heart = pygame.transform.scale(heart, (width / 16, height / 10))

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

    bonus_chance_timer = pygame.USEREVENT + 4
    pygame.time.set_timer(bonus_chance_timer, 5)

    while True:
        # Process user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if player.sprite.lives > 0:
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
                # 1/1000 chance of spawning a beer
                if event.type == bonus_chance_timer and random() > 0.999:
                    consumable_group.add(Consumable(width, height, GROUND_LEVEL))

            else:
                # Press any button to continue
                if event.type == pygame.KEYDOWN:
                    player.sprite.revive()
                    start_time = pygame.time.get_ticks()

        if player.sprite.lives > 0:
            # Render screen
            screen.blit(sky, (0, 0))
            screen.blit(ground, (0, GROUND_LEVEL))
            # Draw current lives
            for i in range(player.sprite.lives):
                screen.blit(heart, (width * (0.94 - i / 20), 0))

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

            # Draw the sprites
            player.draw(screen)
            player.update(width, height, GROUND_LEVEL, obstacle_group, consumable_group)
            obstacle_group.draw(screen)
            obstacle_group.update(width)
            consumable_group.draw(screen)

        else:
            # Game Over screen
            screen.fill((94, 129, 162))
            screen.blit(player_stand, player_stand_rect)
            screen.blit(game_name, game_name_rect)
            if current_score == 0:
                screen.blit(game_message, game_message_rect)
            else:
                screen.blit(score_message, score_message_rect)
                screen.blit(highscore_message, highscore_message_rect)

        pygame.display.update()
        # Cap the refresh rate
        clock.tick(120)


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
            score_rect.left - width / 80,
            score_rect.top - height / 100,
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


if __name__ == "__main__":
    main()
