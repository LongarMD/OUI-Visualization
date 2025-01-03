import pygame
import models

alphabet = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
]

# Define screen constants (default = 1800x1400)
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000
# scaling_factor = 0.25
# Color constants object
color = models.ColorConstants()
# Init pygame
pygame.init()
# Define the screen (and it's properties)
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Planiranje opravil s sredstvi in cilji")
# Create main menu object
menu = models.MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
# Create game object
game = None
# Create algorithm object
algorithm = models.Algorithm(SCREEN_WIDTH, SCREEN_HEIGHT, game)
# Discs' move variables
done = False
drag = False
drop = False
move = False
begin_game = False
init_game = False
discs_chosen = False
positions_chosen = False
disc_index = None
last_pos = [0, 0]

arranging_start = True
arranging_end = False
algorithm_running = False
algorithm_started = False

first_algorithm_saved = False
first_algorithm = None

added_first_history_algorithm = False

# Moves counter
moves_counter = 0
# Manage how fast the screen updates
clock = pygame.time.Clock()
# -------- Main Game Loop -----------
while not done:
    if algorithm_running and algorithm.search_by_width and algorithm.go_one_step_back:
        if not first_algorithm_saved and len(models.algorithm_stack) > 0:
            first_algorithm = models.algorithm_stack[0].get_algorithm_copy()
        if len(models.algorithm_stack) > 1:
            info_text = ""
            if algorithm.actions_index_too_close_to_limit:
                info_text = "Ne splača se več preiskovati akcij, ker nobena nova nima izpolnjenih predpogojev in smo preblizu limite. Gremo korak nazaj"
            else:
                info_text = "Presegli smo limit pri preiskovanju. Vrnemo se korak nazaj in preverimo, če obstaja še kakšna akcija"
            algorithm = models.algorithm_stack.pop()
            algorithm.actions_index += 1
            algorithm.actions_index_too_close_to_limit = False
            algorithm.info_text = info_text
        else:
            info_text = ""
            if algorithm.actions_index_too_close_to_limit:
                info_text = (
                    "Ne splača se več preiskovati akcij, ker nobena nova nima izpolnjenih predpogojev in smo preblizu limite. Zvišamo limito na "
                    + str(algorithm.limit + 1)
                )
            else:
                info_text = (
                    "Šli smo čez vse akcije. Limito moramo povečati za 1. Vrnemo se na začetno stanje in preiskujemo od začetka z limito "
                    + str(algorithm.limit + 1)
                )
            # algorithm = models.algorithm_stack[0]
            # models.algorithm_stack = models.algorithm_stack[:1]
            first_algorithm.limit += 1
            algorithm = first_algorithm
            models.algorithm_stack = [algorithm.get_algorithm_copy()]
            algorithm.actions_index_too_close_to_limit = False
            algorithm.go_one_step_back = False
            algorithm.goals = algorithm.goals[:1]
            algorithm.plan = []
            algorithm.possible_actions = []
            algorithm.current_action = None
            algorithm.current_goal = None
            algorithm.info_text = info_text
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drag = True
            drop = False
            if init_game:
                if not algorithm_running:
                    for i in range(0, game.number_of_discs):
                        if game.discs[i].is_clicked():
                            current_pos = game.discs[i].current_pos
                            pos_length = len(game.positions[current_pos].discs)
                            if (
                                game.discs[i]
                                == game.positions[current_pos].discs[pos_length - 1]
                            ):
                                disc_index = i
                                last_pos = [game.discs[i].rect.x, game.discs[i].rect.y]
                                move = True
                if menu.start_position_button.is_clicked():
                    # game.start_positions = game.positions
                    start_positions = []
                    for i in range(len(game.positions)):
                        pos = models.Position(
                            i, game.PILLAR_COLOR, game.POS_WIDTH, game.POS_HEIGHT
                        )
                        pos.rect.x = (
                            game.BOARD_X + game.POS_WIDTH * i + game.POS_SPACING * i
                        )
                        pos.rect.y = game.BOARD_Y - game.POS_HEIGHT
                        start_positions.append(pos)
                    # game.start_discs = game.discs
                    for i in range(game.number_of_discs):
                        disc = models.Disc(
                            game.discs[i].current_pos,
                            i,
                            models.colors[i],
                            game.DISC_WIDTH,
                            game.DISC_HEIGHT,
                        )
                        game.start_discs.append(disc)
                    for i in range(len(game.positions)):
                        pos = game.positions[i]
                        for disc in pos.discs:
                            new_disc = [d for d in game.start_discs if d.id == disc.id][
                                0
                            ]
                            start_positions[i].discs.append(new_disc)
                    # start_positions[disc.current_pos].discs.append(disc)
                    game.start_positions = start_positions
                    game.sprites_list.remove(game.discs)
                    game.discs = []
                    game.set_new_positions()
                    game.set_start_discs()
                    arranging_start = False
                    arranging_end = True
                elif menu.end_position_button.is_clicked():
                    game.end_positions = game.positions
                    game.end_discs = game.discs
                    game.sprites_list.remove(game.discs)
                    game.discs = game.start_discs
                    game.positions = game.start_positions
                    # game.set_discs_to_starting_pos()
                    algorithm.game = game
                    arranging_end = False
                    algorithm_running = True
                    algorithm_started = True
                elif algorithm.next_button.is_clicked():
                    algorithm.do_next()
                    # if models.current_algorithm_index > 0:
                    #     models.current_algorithm_index -= 1
                    #     algorithm = models.all_past_algorithms[models.current_algorithm_index]
                    # elif models.current_algorithm_index == 0:
                    # algorithm.do_next()
                # elif algorithm.prev_button.is_clicked():
                #     if models.current_algorithm_index + 1 == len(models.all_past_algorithms) or models.current_algorithm_index == 0 and len(models.all_past_algorithms) == 0:
                #         break
                #     models.current_algorithm_index += 1
                #     algorithm = models.all_past_algorithms[models.current_algorithm_index]
                elif algorithm.retry_button.is_clicked():
                    menu = models.MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
                    # Create game object
                    game = None
                    # Create algorithm object
                    algorithm = models.Algorithm(SCREEN_WIDTH, SCREEN_HEIGHT, game)
                    # Discs' move variables
                    done = False
                    drag = False
                    drop = False
                    move = False
                    begin_game = False
                    init_game = False
                    discs_chosen = False
                    positions_chosen = False
                    disc_index = None
                    last_pos = [0, 0]

                    arranging_start = True
                    arranging_end = False
                    algorithm_running = False
                    algorithm_started = False

                    first_algorithm_saved = False
                    first_algorithm = None
                    models.algorithm_stack = []
                    all_past_algorithms = []
                    current_algorithm_index = 0
                    added_first_history_algorithm = False

                for i in range(len(algorithm.algorithm_rectangles)):
                    btn = algorithm.algorithm_rectangles[i]
                    if btn.is_clicked():
                        algorithm.showAlgorithm = i
                        break
                    else:
                        algorithm.showAlgorithm = -1
            else:
                if not discs_chosen:
                    for i in range(0, len(menu.btn_discs)):
                        if menu.btn_discs[i].is_clicked():
                            game = models.Game(
                                SCREEN_WIDTH, SCREEN_HEIGHT, menu.btn_discs[i].value
                            )
                            discs_chosen = True
                            menu.choose_number_of_positions()
                            break
                elif not positions_chosen:
                    for i in range(0, len(menu.btn_positions)):
                        if menu.btn_positions[i].is_clicked():
                            game.number_of_positions = menu.btn_positions[i].value
                            game.set_new_positions()
                            game.set_start_discs()
                            positions_chosen = True
                            menu.choose_gamemode()
                            break
                else:
                    for i in range(0, 2):
                        if menu.btn_gamemodes[i].is_clicked():
                            game.search_by_width = i == 1
                            init_game = True
                            menu.sprites_list.empty()
                            algorithm.search_by_width = i == 1
                            if algorithm.game != None:
                                algorithm.game.search_by_width = i == 1
                            break
        elif event.type == pygame.MOUSEBUTTONUP:
            drag = False
            drop = True
    if init_game:
        screen.fill(game.BACKGROUND)
    else:
        screen.fill(menu.BACKGROUND)
    # Text font,size, bold and italic
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 36)
    # Info Texts
    game_title = None
    if algorithm_running:
        game_title = title_font.render("", True, color.BLACK)
    else:
        game_title = title_font.render(
            "Planiranje opravil s sredstvi in cilji", True, color.BLACK
        )
    screen.blit(game_title, [((SCREEN_WIDTH / 2) - (game_title.get_width() / 2)), 20])
    if init_game:
        if arranging_start:
            menu.sprites_list.empty()
            menu.sprites_list.add([menu.start_position_button])
            menu.start_position_button.rect.x = 20
            menu.start_position_button.rect.y = 150
            menu.end_position_button.rect.x = 3000
            menu.end_position_button.rect.y = 3000
            menu.sprites_list.draw(screen)

        if arranging_end:
            menu.sprites_list.empty()
            menu.sprites_list.add([menu.end_position_button])
            menu.start_position_button.rect.x = 3000
            menu.start_position_button.rect.y = 3000
            menu.end_position_button.rect.x = 20
            menu.end_position_button.rect.y = 150
            menu.sprites_list.draw(screen)

        if drag:
            if move:
                pos = pygame.mouse.get_pos()
                game.discs[disc_index].rect.x = pos[0] - (
                    game.discs[disc_index].width / 2
                )
                game.discs[disc_index].rect.y = pos[1] - (
                    game.discs[disc_index].height / 2
                )
        elif drop:
            if move:
                current_pos = game.discs[disc_index].current_pos
                new_pos = None
                change = False
                turn_back = True
                position = pygame.sprite.spritecollideany(
                    game.discs[disc_index], game.pos_sprites_list
                )
                if position != None:
                    new_pos = position.pos_index
                    if new_pos != current_pos:
                        disc_length = len(position.discs)
                        turn_back = False
                        change = True
                if change:
                    moves_counter = moves_counter + 1
                    game.positions[current_pos].discs.remove(game.discs[disc_index])
                    game.discs[disc_index].current_pos = new_pos
                    game.positions[new_pos].discs.append(game.discs[disc_index])
                    new_pos_length = len(game.positions[new_pos].discs)
                    game.discs[disc_index].rect.x = (
                        game.positions[new_pos].rect.x
                        - (game.DISC_WIDTH / 2)
                        + game.POS_WIDTH / 2
                    )
                    game.discs[disc_index].rect.y = (
                        game.BOARD_Y - game.DISC_HEIGHT
                    ) - (game.DISC_HEIGHT * (new_pos_length - 1))
                    # Check if the game is over
                    if len(game.positions[2].discs) == game.number_of_discs:
                        menu.sprites_list.add(
                            [menu.btn_play_again, menu.btn_quit, menu.btn_return]
                        )
                        menu.sprites_list.remove([menu.label, menu.btn_discs])
                if turn_back:
                    game.discs[disc_index].rect.x = last_pos[0]
                    game.discs[disc_index].rect.y = last_pos[1]
                move = False

        if algorithm_running:
            algorithm.game.sprites_list.draw(screen)
            algorithm.draw_algorithm(screen)
            algorithm.game.refresh_discs()
            if not added_first_history_algorithm:
                models.all_past_algorithms.insert(0, algorithm.get_algorithm_copy())
                added_first_history_algorithm = True
        else:
            game.sprites_list.draw(screen)

    else:
        menu.sprites_list.draw(screen)

    # --- update  screen.
    # scaled_screen = pygame.transform.scale(screen, (SCREEN_WIDTH*scaling_factor, SCREEN_HEIGHT*scaling_factor))
    # screen.blit(scaled_screen, (0,0))
    # pygame.image.save(screen, "screenshot.png")
    pygame.display.flip()
    # --- Limit to 60 frames per second
    clock.tick(60)
pygame.quit()


# DONE vizualizacija za korake nazaj stack
# DONE okno za info gre dol
# DONE stevilke na pozicijah
# DONE 7 -> 5
# DONE bug pri pozicijah in diskih
# DONE preimenuj v preiskovanje z iterativnim poglabljanjem
