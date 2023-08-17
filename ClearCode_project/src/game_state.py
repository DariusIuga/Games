import pygame



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


def game_over(
    screen,
    player_stand,
    game_name,
    score_message,
    highscore_message,
):
    screen.fill((94, 129, 162))
    screen.blit(player_stand.surf, player_stand.rect)
    screen.blit(game_name.surf, game_name.rect)
    screen.blit(score_message.surf, score_message.rect)
    screen.blit(highscore_message.surf, highscore_message.rect)
