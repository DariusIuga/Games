from sys import exit

import pygame


def main():
    # If the dimensions are set to 0, the game runs in fullscreen
    pygame.init()

    # The window is resizable, and all surfaces should mantain their shape relative to the window size
    screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

    pygame.display.set_caption("Körgull the Exterminator")
    clock = pygame.time.Clock()
    default_font = pygame.font.Font("fonts/Pixeltype.ttf", 100)

    ground = pygame.image.load("graphics/ground.png").convert()
    sky = pygame.image.load("graphics/sky.png").convert()

    snail_surf = pygame.image.load("graphics/snail/snail1.png").convert_alpha()
    snail_speed = 0

    player_surf = pygame.image.load("graphics/Player/player_walk_1.png").convert_alpha()
    player_fall_speed = 0
    player_fall_acceleration = 0

    # Main event loop
    while True:
        width, height = screen.get_size()
        GROUND_LEVEL = 3 * height / 4

        sky = pygame.transform.scale(sky, (width, GROUND_LEVEL))
        ground = pygame.transform.scale(ground, (width, height - GROUND_LEVEL))

        snail_surf = pygame.transform.scale(snail_surf, (width / 16, height / 16))
        snail_rect = snail_surf.get_rect(midbottom=(width, GROUND_LEVEL))

        player_surf = pygame.transform.scale(player_surf, (width / 16, height / 6))
        player_rect = player_surf.get_rect(midbottom=(width / 8, GROUND_LEVEL))

        title_surf = default_font.render("KORGULL", False, (128, 128, 128))
        title_rect = title_surf.get_rect(midtop=(width / 2, height / 16))

        fps = default_font.render(str(int(clock.get_fps())), False, "green")

        snail_speed += width / 200
        snail_rect.left -= snail_speed
        if snail_rect.left < 0:
            snail_rect.left = width

        # Process user input
        player_fall_acceleration = handle_input(
            screen, player_rect, player_fall_acceleration, GROUND_LEVEL
        )

        # Because the screen is refreshed, the rectangle starts in the same position on each frame
        player_fall_acceleration += 1
        player_fall_speed += player_fall_acceleration
        player_rect.y += player_fall_speed

        if player_rect.bottom >= GROUND_LEVEL:
            player_rect.bottom = GROUND_LEVEL
            player_fall_acceleration = 0
            player_fall_speed = 0

        screen.fill((0, 0, 0))

        screen.blit(sky, (0, 0))
        screen.blit(ground, (0, GROUND_LEVEL))
        screen.blit(fps, (0, 0))
        pygame.draw.rect(
            screen,
            "#ced249",
            pygame.Rect(
                title_rect.left - 30,
                title_rect.top - 15,
                title_rect.width * 1.2,
                title_rect.height * 1.2,
            ),
            0,
            20,
        )
        screen.blit(title_surf, title_rect)
        screen.blit(snail_surf, snail_rect)
        screen.blit(player_surf, player_rect)

        pygame.display.update()
        # Cap the refresh rate to 60fps
        clock.tick(60)


def handle_input(screen, player_rect, player_fall_acceleration, GROUND_LEVEL):
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.VIDEORESIZE:
            # If the window is resized (VIDEORESIZE event), scale and update the picture
            pygame.display.update()
        elif event.type == pygame.VIDEOEXPOSE:
            # If the window is exposed (e.g., after being minimized or covered),
            # redraw the picture to prevent artifacts and update the display
            screen.fill((0, 0, 0))  # Fill the screen with black
            pygame.display.update()
        if (
            (
                event.type == pygame.MOUSEBUTTONDOWN
                and player_rect.collidepoint(event.pos)
            )
            or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
        ) and player_rect.bottom == GROUND_LEVEL:
            player_fall_acceleration = -25

    return player_fall_acceleration


if __name__ == "__main__":
    main()
