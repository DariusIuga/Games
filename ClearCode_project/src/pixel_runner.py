from game_state import *
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
    default_font = pygame.font.Font("../fonts/Pixeltype.ttf", 100)
    start_time = 0
    current_score = 0
    highscore = 0
    background_music = pygame.mixer.Sound("../audio/epic.opus")
    background_music.play(loops=-1)

    # Groups
    obstacle_group = pygame.sprite.Group()
    healthup_group = pygame.sprite.Group()
    freeze_group = pygame.sprite.Group()
    player = pygame.sprite.GroupSingle()
    player.add(Player(width, GROUND_LEVEL, PLAYER_DIMS, healthup_group, freeze_group))

    # Textures
    ground = pygame.image.load("../graphics/ground.png").convert()
    ground = pygame.transform.scale(ground, (width, height - GROUND_LEVEL))
    sky = pygame.image.load("../graphics/sky.png").convert()
    sky = pygame.transform.scale(sky, (width, GROUND_LEVEL))
    heart = pygame.image.load("../graphics/heart.png")
    heart = pygame.transform.scale(heart, (width / 16, height / 10))

    # Menu screen
    player_stand_surf = pygame.image.load(
        "../graphics/Player/player_stand.png"
    ).convert_alpha()
    player_stand_surf = pygame.transform.scale(
        player_stand_surf, (width / 8, height / 4)
    )
    player_stand_rect = player_stand_surf.get_rect(midbottom=(width / 2, height / 2))
    player_stand = Surf_Rect(player_stand_surf, player_stand_rect)

    game_name_surf = default_font.render("Pixel runner", None, MESSAGE_COLOR)
    game_name_rect = game_name_surf.get_rect(center=(width / 2, height / 5))
    game_name = Surf_Rect(game_name_surf, game_name_rect)

    # Timers
    spawn_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_timer, 600)

    snail_animation_timer = pygame.USEREVENT + 2
    pygame.time.set_timer(snail_animation_timer, 400)

    fly_animation_timer = pygame.USEREVENT + 3
    pygame.time.set_timer(fly_animation_timer, 200)

    health_up_timer = pygame.USEREVENT + 4
    pygame.time.set_timer(health_up_timer, 5)

    freeze_timer = pygame.USEREVENT + 5
    pygame.time.set_timer(freeze_timer, 5)

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
                # 1/1000 chance for each timer
                if random() > 0.999:
                    if event.type == health_up_timer:
                        healthup_group.add(
                            Consumable(width, height, GROUND_LEVEL, "beer")
                        )
                    if event.type == freeze_timer:
                        freeze_group.add(
                            Consumable(width, height, GROUND_LEVEL, "snowflake")
                        )

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

            score_message_surf = default_font.render(
                f"Your score is: {current_score}", False, MESSAGE_COLOR
            )
            score_message_rect = score_message_surf.get_rect(
                midbottom=(width / 2, 2 * height / 3)
            )
            score_message = Surf_Rect(score_message_surf, score_message_rect)

            highscore_message_surf = default_font.render(
                f"Highscore: {highscore}", False, MESSAGE_COLOR
            )
            highscore_message_rect = highscore_message_surf.get_rect(
                midtop=(width / 2, 2 * height / 3)
            )
            highscore_message = Surf_Rect(
                highscore_message_surf, highscore_message_rect
            )

            # Draw the sprites
            obstacle_group.draw(screen)
            obstacle_group.update(width)
            healthup_group.draw(screen)
            freeze_group.draw(screen)
            player.draw(screen)
            player.update(
                width,
                height,
                GROUND_LEVEL,
                obstacle_group,
                healthup_group,
                freeze_group,
            )

            current_score, highscore = display_score(
                width, height, screen, default_font, start_time, highscore
            )

        else:
            # Game Over screen
            game_over(
                screen,
                player_stand,
                game_name,
                score_message,
                highscore_message,
            )

        pygame.display.update()
        # Cap the refresh rate
        clock.tick(120)


if __name__ == "__main__":
    main()
