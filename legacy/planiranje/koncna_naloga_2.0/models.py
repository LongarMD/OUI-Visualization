import pygame
import copy

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
colors = [
    (217, 67, 67),
    (217, 157, 67),
    (130, 217, 67),
    (67, 217, 109),
    (67, 217, 197),
    (67, 145, 217),
    (215, 67, 217),
]
algorithm_stack = []
all_past_algorithms = []
current_algorithm_index = 0


# Color Constants class
class ColorConstants:
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    GREEN = (0, 191, 0)
    WHITE = (255, 255, 255)
    BACKGROUND = (240, 248, 255)
    BOARD_COLOR = (172, 163, 166)
    PILLAR_COLOR = (180, 180, 180, 0)
    PLATFORM_COLOR = (202, 197, 199)
    ACTIONS_COLOR = (255, 217, 102)
    PLAN_COLOR = (189, 215, 238)
    INFO_COLOR = (250, 250, 125)
    BUTTON_COLOR = (189, 215, 238)
    PLAN_CURSOR_COLOR = (100, 100, 100)
    ACTION_INFO_COLOR = (245, 186, 233)
    HISTORY_ALG_COLOR = (215, 238, 189)


# Generic Block class
class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def is_clicked(self):
        return pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos())


# Game positions class
class Position(Block):
    def __init__(self, pos_index, color, width, height):
        Block.__init__(self, color, width, height)
        self.pos_index = pos_index
        self.discs = []
        self.image.set_alpha(128)


# Game discs class
class Disc(Block):
    def __init__(self, current_pos, id, color, width, height):
        super().__init__(color, width, height)
        self.current_pos = current_pos
        self.id = id
        self.render_id()

    def render_id(self):
        font = pygame.font.SysFont(None, 40, False, False)
        id_text = font.render(str(alphabet[self.id]), True, (0, 0, 0))
        text_x = (self.width - id_text.get_width()) / 2
        text_y = (self.height - id_text.get_height()) / 2
        self.image.blit(id_text, (text_x, text_y))

    # def draw(self, screen):
    #     super().draw(screen)  # Call the parent's draw method to draw the outer rectangle
    #     if self.inner_rect:
    #         pygame.draw.rect(screen, self.inner_rect_color, self.inner_rect)


# Buttons class
class Button(Block):
    def __init__(self, text, text_color, text_size, text_font, color, width, height):
        Block.__init__(self, color, width, height)
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.SysFont(text_font, text_size, False, False)
        self.text_render = self.font.render(text, 1, text_color)
        self.value = None

    def set_value(self, value):
        self.value = value

    def render_text(self):
        w = self.width / 2 - (self.text_render.get_width() / 2)
        h = self.height / 2 - (self.text_render.get_height() / 2)
        self.image.blit(self.text_render, [w, h])


# Main Menu
class MainMenu(ColorConstants):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.sprites_list = pygame.sprite.Group()
        self.btn_discs = []
        self.btn_positions = []
        self.btn_gamemodes = []
        self.label = Button("Izberite število kock: ", self.BLACK, 30, None, self.BACKGROUND, 500, 30)
        self.label.rect.x = self.SCREEN_WIDTH / 2 - self.label.rect.width / 2
        self.label.rect.y = self.SCREEN_HEIGHT / 2 - 100
        self.label.render_text()
        self.sprites_list.add(self.label)
        self.spacing = 20
        for i in range(3, 6):
            btn = Button(str(i), self.BLACK, 30, None, self.BACKGROUND, 20, 30)
            btn.rect.x = (
                (self.SCREEN_WIDTH - (5 * (btn.rect.width + self.spacing) - self.spacing)) / 2
                + (i - 3) * (btn.rect.width + self.spacing)
                + 30
            )
            btn.rect.y = self.SCREEN_HEIGHT / 2 - 50
            btn.render_text()
            btn.set_value(i)
            self.btn_discs.append(btn)
        self.sprites_list.add(self.btn_discs)

        # Game over buttons
        self.start_position_button = Button(
            "Izberite kot začetno stanje",
            self.BLACK,
            30,
            None,
            self.BUTTON_COLOR,
            300,
            30,
        )
        self.start_position_button.rect.x = 20
        self.start_position_button.rect.y = 150
        self.start_position_button.render_text()
        self.end_position_button = Button(
            "Izberite kot končno stanje",
            self.BLACK,
            30,
            None,
            self.BUTTON_COLOR,
            300,
            30,
        )
        self.end_position_button.rect.x = 20
        self.end_position_button.rect.y = 180
        self.end_position_button.render_text()

    def choose_number_of_positions(self):
        self.sprites_list.empty()
        self.label = Button("Izberite število pozicij: ", self.BLACK, 30, None, self.BACKGROUND, 500, 30)
        self.label.rect.x = self.SCREEN_WIDTH / 2 - self.label.rect.width / 2
        self.label.rect.y = self.SCREEN_HEIGHT / 2 - 100
        self.label.render_text()
        self.sprites_list.add(self.label)
        for i in range(3, 6):
            btn = Button(str(i), self.BLACK, 30, None, self.BACKGROUND, 20, 30)
            btn.rect.x = (
                (self.SCREEN_WIDTH - (5 * (btn.rect.width + self.spacing) - self.spacing)) / 2
                + (i - 3) * (btn.rect.width + self.spacing)
                + 30
            )
            btn.rect.y = self.SCREEN_HEIGHT / 2 - 50
            btn.render_text()
            btn.set_value(i)
            self.btn_positions.append(btn)
        self.sprites_list.add(self.btn_positions)

    def choose_gamemode(self):
        self.sprites_list.empty()
        self.label = Button("Izberite algoritem: ", self.BLACK, 30, None, self.BACKGROUND, 500, 30)
        self.label.rect.x = self.SCREEN_WIDTH / 2 - self.label.rect.width / 2
        self.label.rect.y = self.SCREEN_HEIGHT / 2 - 100
        self.label.render_text()
        self.sprites_list.add(self.label)

        font = pygame.font.Font(None, 36)

        button_texts = [
            "Preiskovanje v globino",
            "Preiskovanje z iterativnim poglabljanjem",
        ]
        button_height = 30
        spacing = 20
        total_width = sum([font.size(text)[0] for text in button_texts]) + (len(button_texts) - 1) * spacing
        start_x = (self.SCREEN_WIDTH - total_width) / 2 + 100

        for text in button_texts:
            btn_width, btn_height = font.size(text)
            btn = Button(
                text,
                self.BLACK,
                button_height,
                None,
                self.BACKGROUND,
                btn_width,
                btn_height,
            )
            btn.rect.x = start_x
            btn.rect.y = self.SCREEN_HEIGHT / 2 - 50
            btn.render_text()
            self.btn_gamemodes.append(btn)

            start_x += btn_width + spacing
        self.sprites_list.add(self.btn_gamemodes)


class MoveAction:
    def __init__(self, element, start, end):
        self.element = element
        self.start = start
        self.end = end
        self.completed = False
        self.show = True

        self.preconditions = [
            State("clear", element),
            State("on", element, start),
            State("clear", end),
        ]
        self.add_effects = [State("on", element, end), State("clear", start)]
        self.delete_effect = [State("on", element, start), State("clear", end)]
        self.limitations = [
            State("block", element),
            State("not_equal", start, end),
            State("not_equal", start, element),
            State("not_equal", end, element),
        ]

    def do_action(self, positions):
        if len([x for x in self.preconditions if not x.is_true(positions)]) > 0:
            return
        selected_disc_object = None
        for pos in positions:
            for disc in pos.discs:
                if alphabet[disc.id] == self.element:
                    selected_disc_object = disc
                    pos.discs.remove(disc)
        if isinstance(self.end, str):
            for pos in positions:
                for disc in pos.discs:
                    if alphabet[disc.id] == self.end:
                        pos.discs.append(selected_disc_object)
                        selected_disc_object.current_pos = disc.current_pos
                        self.completed = True
        else:
            for pos in positions:
                if pos.pos_index + 1 == self.end:
                    pos.discs.append(selected_disc_object)
                    selected_disc_object.current_pos = pos.pos_index
                    self.completed = True


class State:
    def __init__(self, name, a, b=None):
        self.name = name
        self.a = a
        self.b = b

    def is_true(self, positions):
        match self.name:
            case "clear":
                return self.clear(self.a, positions)
            case "on":
                return self.on(self.a, self.b, positions)
            case "block":
                return self.a in alphabet
            case "not_equal":
                return self.a != self.b
            case _:
                return False

    def clear(self, e, positions):
        for position in positions:
            if position.pos_index + 1 == e:
                return len(position.discs) == 0

            for i in range(len(position.discs)):
                if alphabet[position.discs[i].id] == e:
                    return i + 1 == len(position.discs)
        return False

    def on(self, a, b, positions):
        for position in positions:
            for i in range(len(position.discs)):
                if alphabet[position.discs[i].id] == b:
                    return i + 1 != len(position.discs) and alphabet[position.discs[i + 1].id] == a
                if position.pos_index + 1 == b and i == 0 and a == alphabet[position.discs[i].id]:
                    return True
        return False


class Algorithm(ColorConstants):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, game):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.BUTTON_WIDTH = 100
        self.BUTTON_HEIGHT = 50
        self.TEXT_LEFT_MARGIN = 50

        self.PLAN_WIDTH = SCREEN_WIDTH // 4
        self.PLAN_HEIGHT = SCREEN_HEIGHT // 2 - self.BUTTON_HEIGHT

        self.set_goals = True

        self.font_size = 24

        self.algorithm_rectangles = []
        self.showAlgorithm = -1

        self.game = game
        self.ignore_exact_positions = True
        self.info_text = ""
        self.show_info = True
        self.info_x = 0
        self.info_y = self.SCREEN_HEIGHT - 850

        self.limit = 1
        self.limit_reached = False
        self.go_one_step_back = False
        self.actions_index_too_close_to_limit = False
        self.search_by_width = game.search_by_width if game != None else False
        self.actions_index = 0
        self.previous_algorithm = None
        self.plan = []
        self.check_limit = False
        self.plan_pointer = 0
        self.possible_actions = []
        self.current_state = []
        self.goals = []  # 2D array (used like a stack)
        self.current_goal = None
        self.current_actions_table = []
        self.current_action = None

        self.next_button = Button(
            ">",
            self.BLACK,
            30,
            None,
            self.GREEN,
            self.BUTTON_WIDTH + 10 * 2,
            self.BUTTON_HEIGHT + 10 * 2,
        )
        self.next_button.rect.x = SCREEN_WIDTH - 50 - self.BUTTON_WIDTH
        self.next_button.rect.y = SCREEN_HEIGHT / 2 - self.BUTTON_HEIGHT / 2

        # self.prev_button = Button(">", self.BLACK, 30, None, self.GREEN, self.BUTTON_WIDTH + 10 * 2, self.BUTTON_HEIGHT + 10 * 2)
        # self.prev_button.rect.x = 50
        # self.prev_button.rect.y = SCREEN_HEIGHT / 2 - self.BUTTON_HEIGHT / 2

        self.retry_button = Button(
            "Retry",
            self.BLACK,
            30,
            None,
            self.GREEN,
            self.BUTTON_WIDTH + 10 * 4,
            self.BUTTON_HEIGHT + 10 * 2,
        )
        self.retry_button.rect.x = 50
        self.retry_button.rect.y = SCREEN_HEIGHT - (self.BUTTON_WIDTH + 10 * 2) - 150

        self.plan_rect = Block(self.PLAN_COLOR, self.PLAN_WIDTH, self.PLAN_HEIGHT)
        self.plan_rect.rect.x = SCREEN_WIDTH - self.PLAN_WIDTH
        self.plan_rect.rect.y = 0

        self.plan_cursor_x = 30 + self.SCREEN_WIDTH - self.PLAN_WIDTH - 25
        self.plan_cursor_y = 50 + 36 * (self.plan_pointer + 1) + 10 * (self.plan_pointer + 1) - 5
        self.plan_cursor = ((25, 75), (320, 125), (250, 375))
        self.plan_cursor = (
            (self.plan_cursor_x, self.plan_cursor_y),
            (self.plan_cursor_x, self.plan_cursor_y + 16),
            (self.plan_cursor_x + 16, self.plan_cursor_y + 8),
        )

        self.action_info_rect = Block(self.ACTION_INFO_COLOR, self.PLAN_WIDTH + 100, self.PLAN_HEIGHT // 2.8)
        self.action_info_rect.rect.x = SCREEN_WIDTH - self.PLAN_WIDTH - 100
        self.action_info_rect.rect.y = self.PLAN_HEIGHT + 150

    def draw_algorithm(self, screen):
        self.refresh_current_state()

        if len(self.goals) > 0:
            if len(self.goals[-1]) == len([x for x in self.goals[-1] if x.is_true(self.game.positions)]):
                self.goals.pop()
                if len(self.goals) == 0:
                    print("Konec")

        if self.set_goals:
            self.add_goals(self.game.end_positions)
            self.set_goals = False
            algorithm_stack.append(self.get_algorithm_copy())

        # pygame.draw.rect(screen, self.RED, self.prev_button)
        pygame.draw.rect(screen, self.BUTTON_COLOR, self.next_button)
        # pygame.draw.rect(screen, self.BUTTON_COLOR, self.prev_button)
        pygame.draw.rect(screen, self.BUTTON_COLOR, self.retry_button)
        pygame.draw.rect(screen, self.PLAN_COLOR, self.plan_rect)
        pygame.draw.rect(screen, self.ACTION_INFO_COLOR, self.action_info_rect)

        text_margin = 10

        font = pygame.font.Font(None, self.font_size)

        # Render next button
        next_text = pygame.font.Font(None, 36).render("Naprej", True, self.BLACK)
        next_text_rect = next_text.get_rect()
        next_text_rect.x = self.next_button.rect.x + text_margin
        next_text_rect.y = self.next_button.rect.y + text_margin

        # prev_text = pygame.font.Font(None, 36).render("Nazaj", True, self.BLACK)
        # prev_text_rect = prev_text.get_rect()
        # prev_text_rect.x = self.prev_button.rect.x + text_margin
        # prev_text_rect.y = self.prev_button.rect.y + text_margin

        retry_text = pygame.font.Font(None, 36).render("Ponastavi", True, self.BLACK)
        retry_text_rect = retry_text.get_rect()
        retry_text_rect.x = self.retry_button.rect.x + text_margin
        retry_text_rect.y = self.retry_button.rect.y + text_margin

        screen.blit(next_text, next_text_rect)
        # screen.blit(prev_text, prev_text_rect)
        screen.blit(retry_text, retry_text_rect)

        # Render current state
        current_state_text = font.render("Trenutno stanje: " + self.get_states_text(), True, (0, 0, 0))
        current_state_text_rect = current_state_text.get_rect()
        current_state_text_rect.x = self.TEXT_LEFT_MARGIN
        current_state_text_rect.y = 50
        screen.blit(current_state_text, current_state_text_rect)

        # Render current goals
        if len(self.goals) > 0:
            goals_text_rect = None
            init_goals_text = font.render("Cilji: ", True, self.BLACK)
            init_goals_text_rect = init_goals_text.get_rect()
            init_goals_text_rect.x = self.TEXT_LEFT_MARGIN
            init_goals_text_rect.y = 50 + init_goals_text_rect.height + text_margin
            screen.blit(init_goals_text, init_goals_text_rect)
            value_x_for_next_goal = self.TEXT_LEFT_MARGIN + init_goals_text_rect.width
            for i in range(len(self.goals[-1])):
                comma_text = font.render(", ", True, self.BLACK)
                comma_text_rect = comma_text.get_rect()
                goal_color = self.GREEN if self.goals[-1][i].is_true(self.game.positions) else self.RED
                current_goals_text = font.render(self.get_states_text([self.goals[-1][i]]), True, goal_color)
                goals_text_rect = current_goals_text.get_rect()
                goals_text_rect.x = value_x_for_next_goal + comma_text_rect.width * i
                value_x_for_next_goal += goals_text_rect.width
                goals_text_rect.y = 50 + goals_text_rect.height + text_margin
                comma_text_rect.x = value_x_for_next_goal + comma_text_rect.width * i
                comma_text_rect.y = goals_text_rect.y
                if i + 1 != len(self.goals[-1]):
                    screen.blit(comma_text, comma_text_rect)
                screen.blit(current_goals_text, goals_text_rect)

        else:
            goals_text_rect = None
            init_goals_text = font.render("Vsi cilji doseženi!", True, self.BLACK)
            init_goals_text_rect = init_goals_text.get_rect()
            init_goals_text_rect.x = self.TEXT_LEFT_MARGIN
            init_goals_text_rect.y = 50 + init_goals_text_rect.height + text_margin
            screen.blit(init_goals_text, init_goals_text_rect)

        # Render selected goal
        selected_goal = "" if self.current_goal == None else self.get_states_text([self.current_goal])
        selected_goal_text = selected_goal if selected_goal != "" else ""
        if selected_goal_text != "":
            selected_goal_text = "Izberemo cilj: " + selected_goal_text
        current_goal_text = font.render(selected_goal_text, True, (0, 0, 0))
        current_goal_text_rect = current_goal_text.get_rect()
        current_goal_text_rect.x = self.TEXT_LEFT_MARGIN
        current_goal_text_rect.y = 50 + current_goal_text_rect.height * 2 + text_margin * 2
        screen.blit(current_goal_text, current_goal_text_rect)

        # Render selected action
        if self.current_action != None and self.current_action.show:
            current_action_text = font.render(
                "Izberemo akcijo: " + self.get_action_text(self.current_action),
                True,
                (0, 0, 0),
            )
            current_action_rect = current_action_text.get_rect()
            current_action_rect.x = self.TEXT_LEFT_MARGIN
            current_action_rect.y = 50 + current_action_rect.height * 3 + text_margin * 3
            screen.blit(current_action_text, current_action_rect)

        # Render plan
        plan_text = font.render("Plan:", True, (0, 0, 0))
        plan_rect = plan_text.get_rect()
        plan_rect.x = 30 + self.SCREEN_WIDTH - self.PLAN_WIDTH
        plan_rect.y = 50
        screen.blit(plan_text, plan_rect)
        for i in range(len(self.plan)):
            action = self.plan[i]
            if action != None:
                action_color = (
                    self.BLACK
                    if action.completed
                    else (
                        self.GREEN
                        if len(
                            [
                                precondition
                                for precondition in action.preconditions
                                if not precondition.is_true(self.game.positions)
                            ]
                        )
                        == 0
                        else self.RED
                    )
                )
                plan_action_text = font.render(self.get_action_text(self.plan[i]), True, action_color)
                plan_action_text_rect = plan_action_text.get_rect()
                plan_action_text_rect.x = 30 + self.SCREEN_WIDTH - self.PLAN_WIDTH
                plan_action_text_rect.y = 50 + plan_action_text_rect.height * (i + 1) + text_margin * (i + 1)
                screen.blit(plan_action_text, plan_action_text_rect)

        # Render possible actions
        if self.possible_actions != None and len(self.possible_actions) > 0:
            for i in range(len(self.possible_actions)):
                action = self.possible_actions[i]
                action_text = font.render(self.get_action_text(action) + " - ", True, self.BLACK)
                action_text_rect = action_text.get_rect()
                action_text_rect.x = 80
                action_text_rect.y = (
                    50
                    + action_text_rect.height * 3
                    + text_margin * (3 + 1)
                    + action_text_rect.height * (i + 1)
                    + text_margin * (i + 1)
                    + 30
                )
                screen.blit(action_text, action_text_rect)
                value_x_for_next_goal = action_text_rect.x + action_text_rect.width
                for j in range(len(action.preconditions)):
                    comma_text = font.render(", ", True, self.BLACK)
                    comma_text_rect = comma_text.get_rect()
                    precondition = action.preconditions[j]
                    goal_color = self.GREEN if precondition.is_true(self.game.positions) else self.RED
                    current_precondition_text = font.render(self.get_states_text([precondition]), True, goal_color)
                    current_precondition_text_rect = current_precondition_text.get_rect()
                    current_precondition_text_rect.x = value_x_for_next_goal + comma_text_rect.width * j
                    value_x_for_next_goal += current_precondition_text_rect.width
                    current_precondition_text_rect.y = action_text_rect.y
                    # comma_text = font.render(", ", True, self.BLACK)
                    comma_text_rect.x = value_x_for_next_goal + comma_text_rect.width * j
                    comma_text_rect.y = action_text_rect.y
                    screen.blit(current_precondition_text, current_precondition_text_rect)
                    if j + 1 != len(action.preconditions):
                        screen.blit(comma_text, comma_text_rect)

        # Render limit if search_by_width == True
        if self.search_by_width:
            limit_text = font.render("Limit: " + str(self.limit), True, self.BLACK)
            limit_text_rect = limit_text.get_rect()
            limit_text_rect.x = self.plan_rect.rect.x - limit_text_rect.width - text_margin
            limit_text_rect.y = 50
            screen.blit(limit_text, limit_text_rect)

        # Render info text
        if self.show_info and self.info_text != "":
            info_text = font.render(self.info_text, True, self.BLACK)
            info_text_rect = info_text.get_rect()
            info_text_rect.x = self.info_x + text_margin
            info_text_rect.y = self.info_y + text_margin

            info_box = Block(
                self.INFO_COLOR,
                info_text_rect.width + text_margin * 2,
                info_text_rect.height + text_margin * 2,
            )
            info_box.rect.x = self.info_x
            info_box.rect.y = self.info_y

            pygame.draw.rect(screen, self.INFO_COLOR, info_box)
            screen.blit(info_text, info_text_rect)

        # Render plan cursor
        self.plan_cursor_x = 30 + self.SCREEN_WIDTH - self.PLAN_WIDTH - 25
        self.plan_cursor_y = (
            50
            + plan_rect.height * (self.plan_pointer + 1)
            + text_margin * (self.plan_pointer + 2)
            + ((1 / 2) * self.font_size - 22)
        )
        self.plan_cursor = ((25, 75), (320, 125), (250, 375))
        self.plan_cursor = (
            (self.plan_cursor_x, self.plan_cursor_y),
            (self.plan_cursor_x, self.plan_cursor_y + 16),
            (self.plan_cursor_x + 16, self.plan_cursor_y + 8),
        )
        pygame.draw.polygon(screen, self.PLAN_CURSOR_COLOR, self.plan_cursor)

        # Render move action info box
        move_info_text = font.render("move(Block, From, To):", True, (0, 0, 0))
        move_info_text_rect = move_info_text.get_rect()
        move_info_text_rect.x = self.SCREEN_WIDTH - self.PLAN_WIDTH - 70
        move_info_text_rect.y = self.PLAN_HEIGHT + 200
        screen.blit(move_info_text, move_info_text_rect)
        for i in range(4):
            text = font.render(
                [
                    "predpogoji: [clear(Block), on(Block,From), clear(To)]",
                    "učinki-add [on(Block,To), clear(From)]",
                    "učinki-del: [on(Block,From), clear(To)]",
                    "omejitve: [block(Block), To≠From, To≠Block, From≠Block]",
                ][i],
                True,
                self.BLACK,
            )
            text_rect = text.get_rect()
            text_rect.x = self.SCREEN_WIDTH - self.PLAN_WIDTH - 20
            text_rect.y = self.PLAN_HEIGHT + 200 + text_rect.height * (i + 1) + text_margin * (i + 1)
            screen.blit(text, text_rect)

        # Render History Stuff

        self.algorithm_rectangles = []

        if self.search_by_width:
            # Init text
            history_init_text = font.render("Pregled stanj za nazaj:", True, (0, 0, 0))
            history_init_text_rect = history_init_text.get_rect()
            history_init_text_rect.x = 50
            history_init_text_rect.y = (
                self.PLAN_HEIGHT
                + 100
                + (i * 3) * text_margin
                + i * pygame.font.Font(None, self.font_size).render("x", True, self.BLACK).get_rect().height
                - 200
                + history_init_text_rect.height
            )
            screen.blit(history_init_text, history_init_text_rect)

            for i in range(len(algorithm_stack)):
                alg_rect = Block(
                    self.ACTION_INFO_COLOR,
                    100,
                    10 * 2 + pygame.font.Font(None, self.font_size).render("x", True, self.BLACK).get_rect().height,
                )
                alg_rect.rect.x = 50
                alg_rect.rect.y = (
                    self.PLAN_HEIGHT
                    + 100
                    + (i * 3) * text_margin
                    + i * pygame.font.Font(None, self.font_size).render("x", True, self.BLACK).get_rect().height
                )
                self.algorithm_rectangles.append(alg_rect)

        for i in range(len(self.algorithm_rectangles)):
            pygame.draw.rect(screen, self.ACTION_INFO_COLOR, self.algorithm_rectangles[i])

            alg_text = font.render("Nivo " + str(i + 1) + ": ", True, (0, 0, 0))
            alg_text_rect = alg_text.get_rect()
            alg_text_rect.x = 50 + text_margin
            alg_text_rect.y = self.PLAN_HEIGHT + 100 + (i * 3 + 1) * text_margin + i * alg_text_rect.height
            screen.blit(alg_text, alg_text_rect)

        if self.showAlgorithm >= 0:  # goals, selected goal, actions, plan, current_state
            history_algorithm_rect = Block(self.HISTORY_ALG_COLOR, self.PLAN_HEIGHT * 2, self.PLAN_HEIGHT)
            history_algorithm_rect.rect.x = self.SCREEN_WIDTH // 2 - (self.PLAN_WIDTH * 2) // 2
            history_algorithm_rect.rect.y = self.SCREEN_HEIGHT // 2 - self.PLAN_HEIGHT // 2

            pygame.draw.rect(screen, self.HISTORY_ALG_COLOR, history_algorithm_rect)

            left_margin = history_algorithm_rect.rect.x + text_margin
            top_margin = history_algorithm_rect.rect.y + text_margin

            plan_left_margin = history_algorithm_rect.rect.y + text_margin + 1000

            alg = algorithm_stack[self.showAlgorithm]

            # State
            current_state_text = font.render("Stanje: " + alg.get_states_text(alg.current_state), True, (0, 0, 0))
            current_state_text_rect = current_state_text.get_rect()
            current_state_text_rect.x = left_margin
            current_state_text_rect.y = top_margin
            screen.blit(current_state_text, current_state_text_rect)

            # Goals
            if len(alg.goals) > 0:
                goals_text_rect = None
                init_goals_text = font.render("Cilji: ", True, self.BLACK)
                init_goals_text_rect = init_goals_text.get_rect()
                init_goals_text_rect.x = left_margin
                init_goals_text_rect.y = top_margin + init_goals_text_rect.height * 1 + text_margin * 1
                screen.blit(init_goals_text, init_goals_text_rect)
                value_x_for_next_goal = left_margin + init_goals_text_rect.width
                for i in range(len(alg.goals[-1])):
                    comma_text = font.render(", ", True, self.BLACK)
                    comma_text_rect = comma_text.get_rect()
                    goal_color = self.GREEN if alg.goals[-1][i].is_true(alg.game.positions) else self.RED
                    current_goals_text = font.render(alg.get_states_text([alg.goals[-1][i]]), True, goal_color)
                    goals_text_rect = current_goals_text.get_rect()
                    goals_text_rect.x = value_x_for_next_goal + comma_text_rect.width * i
                    value_x_for_next_goal += goals_text_rect.width
                    goals_text_rect.y = top_margin + init_goals_text_rect.height * 1 + text_margin * 1
                    comma_text_rect.x = value_x_for_next_goal + comma_text_rect.width * i
                    comma_text_rect.y = goals_text_rect.y
                    if i + 1 != len(alg.goals[-1]):
                        screen.blit(comma_text, comma_text_rect)
                    screen.blit(current_goals_text, goals_text_rect)

            # Selected goal
            selected_goal = "" if alg.current_goal == None else alg.get_states_text([alg.current_goal])
            selected_goal_text = selected_goal if selected_goal != "" else ""
            if selected_goal_text != "":
                selected_goal_text = "Izbrani cilj: " + selected_goal_text
            current_goal_text = font.render(selected_goal_text, True, (0, 0, 0))
            current_goal_text_rect = current_goal_text.get_rect()
            current_goal_text_rect.x = left_margin
            current_goal_text_rect.y = top_margin + current_goal_text_rect.height * 2 + text_margin * 2
            screen.blit(current_goal_text, current_goal_text_rect)

            # Possible actions
            if alg.possible_actions != None and len(alg.possible_actions) > 0:
                possible_actions_text = font.render("Možne akcije:", True, (0, 0, 0))
                possible_actions_text_rect = possible_actions_text.get_rect()
                possible_actions_text_rect.x = left_margin
                possible_actions_text_rect.y = top_margin + possible_actions_text_rect.height * 3 + text_margin * 3
                screen.blit(possible_actions_text, possible_actions_text_rect)

                for i in range(len(alg.possible_actions)):
                    action = alg.possible_actions[i]
                    action_text = font.render(alg.get_action_text(action) + " - ", True, self.BLACK)
                    action_text_rect = action_text.get_rect()
                    action_text_rect.x = left_margin + 30
                    action_text_rect.y = top_margin + current_goal_text_rect.height * (4 + i) + text_margin * (4 + i)
                    # action_text_rect.y = 50 + action_text_rect.height * 3 + text_margin * (3 + 1) + \
                    #                     action_text_rect.height * (i + 1) + text_margin * (i + 1) + 30
                    screen.blit(action_text, action_text_rect)
                    value_x_for_next_goal = action_text_rect.x + action_text_rect.width
                    for j in range(len(action.preconditions)):
                        comma_text = font.render(", ", True, self.BLACK)
                        comma_text_rect = comma_text.get_rect()
                        precondition = action.preconditions[j]
                        goal_color = self.GREEN if precondition.is_true(alg.game.positions) else self.RED
                        current_precondition_text = font.render(alg.get_states_text([precondition]), True, goal_color)
                        current_precondition_text_rect = current_precondition_text.get_rect()
                        current_precondition_text_rect.x = value_x_for_next_goal + comma_text_rect.width * j
                        value_x_for_next_goal += current_precondition_text_rect.width
                        current_precondition_text_rect.y = action_text_rect.y
                        comma_text_rect.x = value_x_for_next_goal + comma_text_rect.width * j
                        comma_text_rect.y = action_text_rect.y
                        screen.blit(current_precondition_text, current_precondition_text_rect)
                        if j + 1 != len(action.preconditions):
                            screen.blit(comma_text, comma_text_rect)

            # Plan
            plan_text = font.render("Plan:", True, (0, 0, 0))
            plan_rect = plan_text.get_rect()
            plan_rect.x = plan_left_margin
            plan_rect.y = top_margin
            screen.blit(plan_text, plan_rect)
            for i in range(len(alg.plan)):
                action = alg.plan[i]
                if action != None:
                    action_color = (
                        self.BLACK
                        if action.completed
                        else (
                            self.GREEN
                            if len(
                                [
                                    precondition
                                    for precondition in action.preconditions
                                    if not precondition.is_true(alg.game.positions)
                                ]
                            )
                            == 0
                            else self.RED
                        )
                    )
                    plan_action_text = font.render(alg.get_action_text(alg.plan[i]), True, action_color)
                    plan_action_text_rect = plan_action_text.get_rect()
                    plan_action_text_rect.x = plan_left_margin
                    plan_action_text_rect.y = (
                        top_margin + plan_action_text_rect.height * (i + 1) + text_margin * (i + 1)
                    )
                    screen.blit(plan_action_text, plan_action_text_rect)

    def do_next(self):
        # go through plan and check for loops
        if len(list({(action.element, action.start, action.end): action for action in self.plan}.values())) + 1 < len(
            self.plan
        ):
            self.info_text = "Algoritem se je zaciklal. Za rešitev tega problema bi potrebovali preiskovanje v širino."
            return
        all_past_algorithms.insert(0, self.get_algorithm_copy())
        # check if current state is equal to end position:
        if len(self.goals) == 0 or [goal for goal in self.goals[0] if not goal.is_true(self.game.positions)] == 0:
            self.set_info_box("Dosegli smo končno stanje", 0, 0)
            return
        if self.search_by_width:
            if self.actions_index >= len(self.possible_actions) and len(self.possible_actions) != 0:
                self.limit_reached = True
                self.go_one_step_back = True
                return
            if len(self.plan) == self.limit and len(
                [
                    action
                    for action in self.plan
                    if action.completed
                    or len(
                        [
                            precondition
                            for precondition in action.preconditions
                            if not precondition.is_true(self.game.positions)
                        ]
                    )
                    > 0
                ]
            ) == len(self.plan):
                self.limit_reached = True
                self.go_one_step_back = True
                return
            self.limit_reached = False
        do_action = True
        not_completed_actions = [x for x in self.plan if x != None and x.completed == False]
        next_action = not_completed_actions[0] if len(not_completed_actions) > 0 else None
        if next_action != None and not self.equals(self.goals[-1], next_action.preconditions):
            for precondition in next_action.preconditions:
                if not precondition.is_true(self.game.positions):
                    do_action = False
                    self.goals.append(next_action.preconditions)
                    self.current_action = None
                    self.possible_actions = []
                    self.current_goal = None
        if len(self.plan) > 0 and self.current_action != None and self.current_action == next_action and do_action:
            self.current_action.do_action(self.game.positions)
            self.info_text = "Izvedemo akcijo"
            self.plan_pointer += 1
            self.current_action = None
            self.possible_actions = []
            self.current_goal = None
            # Choose next action from plan if its preconditions are met
            not_completed_actions = [x for x in self.plan if not x.completed]
            next_action = not_completed_actions[0] if len(not_completed_actions) > 0 else None
            if next_action != None:
                preconditions_met = (
                    len([x for x in next_action.preconditions if not x.is_true(self.game.positions)]) == 0
                )
                if preconditions_met:
                    next_action.show = False
                    self.current_action = next_action
        else:
            if self.current_goal == None:
                self.choose_goal()
                self.info_text = "Izberemo prvi neizpolnjeni cilj"
            else:
                if self.current_action == None and (self.possible_actions == None or len(self.possible_actions) == 0):
                    self.get_possible_actions()
                    self.info_text = "Pogledamo katere akcije izpolnijo naš cilj"
                elif self.current_action == None and self.possible_actions != None:
                    # preveri ce je brez veze da sploh probava naprej possible actions
                    if (
                        self.search_by_width
                        and len(self.plan) + 1 == self.limit
                        and self.possible_actions != None
                        and len(self.possible_actions) > 0
                        and self.count_true_preconditions(self.possible_actions[self.actions_index])
                        != len(self.possible_actions[self.actions_index].preconditions)
                    ):
                        self.go_one_step_back = True
                        self.actions_index_too_close_to_limit = True
                        return
                    if (
                        self.actions_index == len(self.possible_actions)
                    ):  # preveri ali smo na koncu vseh možnih akcij ali pa je tako ali tako brez veze probavat ker smo 1 od limite in nima več vseh predpogojev izpolnjenih
                        self.go_one_step_back = True
                    else:
                        new_algorithm = self.get_algorithm_copy()
                        algorithm_stack.append(new_algorithm)
                        self.choose_action(self.actions_index)
                        self.info_text = (
                            "Izberemo akcijo z največ izpolnjenimi predpogoji"
                            if self.actions_index == 0
                            else "Izberemo naslednjo akcijo po vrsti"
                        )
                else:
                    self.info_text = "Akcijo dodamo v plan"
                    self.actions_index = 0
                    self.plan[self.plan_pointer : self.plan_pointer] = [self.current_action]
                    self.check_limit = True

    def count_true_preconditions(self, action):
        return sum(state.is_true(self.game.positions) for state in action.preconditions)

    def get_possible_actions(self):
        all_actions = []
        for el in alphabet[: self.game.number_of_discs]:
            for a in alphabet[: self.game.number_of_discs] + list(range(1, self.game.number_of_positions + 1)):
                for b in alphabet[: self.game.number_of_discs] + list(range(1, self.game.number_of_positions + 1)):
                    all_actions.append(MoveAction(el, a, b))
        # for a in all_actions:
        #     print("move(" + str(a.element) + ", " + str(a.start) + ", " + str(a.end) + ")")
        all_actions = list({(action.element, action.start, action.end): action for action in all_actions}.values())

        # print("divider")
        # for a in all_actions:
        #     print("move(" + str(a.element) + ", " + str(a.start) + ", " + str(a.end) + ")")

        filtered_actions = []
        for a in all_actions:
            adds_correct_effect = False
            for e in a.add_effects:
                if (
                    e.name == self.current_goal.name
                    and e.a == self.current_goal.a
                    and e.b == self.current_goal.b
                    and a.element != a.end
                    and a.start != a.end
                    and a.element != a.start
                ):
                    adds_correct_effect = True
                    break
            if adds_correct_effect:
                filtered_actions.append(a)
        self.possible_actions = sorted(
            filtered_actions,
            key=lambda action: (
                -self.count_true_preconditions(action),
                str(action.element),
                str(action.start),
                str(action.end),
            ),
        )

    def choose_action(self, choose_index):
        self.current_action = self.possible_actions[choose_index]

    def implement_action(self):
        disc_position = None
        disc_before = None
        for pos in self.game.positions:
            for disc in pos.discs:
                if self.current_action.element == alphabet[disc.id]:
                    disc = 0
                else:
                    disc_before = disc

    def get_states_text(self, states_arr=None):
        states_arr = states_arr if states_arr != None else self.current_state
        current_state_text = ""
        for i in range(len(states_arr)):
            state = states_arr[i]
            current_state_text += (
                state.name + "(" + str(state.a) + ((", " + str(state.b)) if state.b is not None else "") + ")"
            )
            if i + 1 < len(states_arr):
                current_state_text += ", "
        return current_state_text

    def get_action_text(self, action, preconditions=False):
        if action == None:
            return ""
        if preconditions:
            return (
                "move("
                + str(action.element)
                + ", "
                + str(action.start)
                + ", "
                + str(action.end)
                + ") -> "
                + self.get_states_text(action.preconditions)
            )
        return "move(" + str(action.element) + ", " + str(action.start) + ", " + str(action.end) + ")"

    def move(self, e, start, end):
        for position in self.game.positions:
            for i in range(len(position.discs)):
                if alphabet[position.discs[i].id] == e:  # Find the correct element to move
                    if (start not in alphabet and position.pos_index == start - 1 and i == 0) or (
                        i != 0 and alphabet[position.discs[i - 1].id] == start
                    ):  # If the start variable holds up
                        if i + 1 == len(position.discs):  # Element is the top one
                            if end in alphabet:  # Putting it on top of another
                                for end_position in self.game.positions:
                                    for j in range(len(end_position.discs)):
                                        if alphabet[end_position.discs[j].id] == end:  # Find correct
                                            if j + 1 == len(end_position.discs):  # Is clear
                                                # Perform move
                                                disc = position.discs.pop()
                                                disc.current_pos = end_position.pos_index
                                                end_position.discs.append(disc)
                                                return "-1"
                                            return "6"
                            else:  # Putting it on empty position
                                for end_position in self.game.positions:
                                    if end_position.pos_index + 1 == end:
                                        if self.clear(end_position.pos_index + 1):  # Correct and clear position
                                            # Perform move
                                            disc = position.discs.pop()
                                            disc.current_pos = end_position.pos_index
                                            end_position.discs.append(disc)
                                            return "0"
                                        return "5"
                            return "4"
                        return "3"
                    return "2"
        return "1"

    def refresh_current_state(self):
        self.current_state = []
        for pos in self.game.positions:
            if len(pos.discs) == 0:
                self.current_state.append(State("clear", pos.pos_index + 1))
            else:
                for i in range(len(pos.discs)):
                    if i == 0:
                        self.current_state.append(State("on", alphabet[pos.discs[i].id], pos.pos_index + 1))
                    if i + 1 == len(pos.discs):
                        self.current_state.append(State("clear", alphabet[pos.discs[i].id]))
                    else:
                        self.current_state.append(
                            State(
                                "on",
                                alphabet[pos.discs[i + 1].id],
                                alphabet[pos.discs[i].id],
                            )
                        )

    def add_goals(self, positions):
        self.goals.append([])
        for pos in positions:
            if len(pos.discs) == 0:
                self.goals[-1].append(State("clear", pos.pos_index + 1))
            else:
                for i in range(len(pos.discs)):
                    if i + 1 == len(pos.discs):
                        self.goals[-1].append(State("clear", alphabet[pos.discs[i].id]))
                    else:
                        self.goals[-1].append(
                            State(
                                "on",
                                alphabet[pos.discs[i + 1].id],
                                alphabet[pos.discs[i].id],
                            )
                        )

    def choose_goal(self):
        if len(self.goals) > 0:
            self.current_goal = self.goals[-1][0]
            i = 0
            while self.current_goal.is_true(self.game.positions):
                self.current_goal = self.goals[-1][i]
                if i + 1 == len(self.goals[-1]):
                    break
                i += 1

        else:
            None

    def equals(self, arr1, arr2):
        for s1 in arr1:
            hasEqual = False
            for s2 in arr2:
                if s1.name == s2.name and s1.a == s2.a and s1.b == s2.b:
                    hasEqual = True
            if not hasEqual:
                return False
        return len(arr1) == len(arr2)

    def get_algorithm_copy(self):
        game = self.game.get_game_copy()
        # game = self.game
        algorithm = Algorithm(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, game)
        algorithm.search_by_width = game.search_by_width
        algorithm.plan = copy.deepcopy(self.plan)
        algorithm.possible_actions = copy.deepcopy(self.possible_actions)
        algorithm.current_action = copy.deepcopy(self.current_action)
        algorithm.current_goal = copy.deepcopy(self.current_goal)
        algorithm.goals = copy.deepcopy(self.goals)
        algorithm.actions_index = copy.deepcopy(self.actions_index)
        algorithm.plan_pointer = copy.deepcopy(self.plan_pointer)
        algorithm.limit = copy.deepcopy(self.limit)
        algorithm.limit_reached = copy.deepcopy(self.limit_reached)
        algorithm.current_state = copy.deepcopy(self.current_state)
        algorithm.set_goals = self.set_goals
        algorithm.plan_pointer = self.plan_pointer

        return algorithm

    def set_info_box(self, text, x, y):
        self.info_text = text
        self.info_x = x
        self.info_y = y


# Game main class
class Game(ColorConstants):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, number_of_discs):
        # Game sprites groups
        self.sprites_list = pygame.sprite.Group()
        self.pos_sprites_list = pygame.sprite.Group()
        self.search_by_width = False

        self.positions = []
        self.platforms = []
        self.platform_numbers = []
        self.discs = []
        self.number_of_discs = number_of_discs
        self.number_of_positions = number_of_discs

        self.SCREEN_WIDTH = SCREEN_WIDTH / 2
        self.SCREEN_HEIGHT = SCREEN_HEIGHT / 2

        self.BOARD_WIDTH = SCREEN_WIDTH / 3
        self.BOARD_HEIGHT = 50

        self.POS_SPACING = SCREEN_WIDTH / (number_of_discs * 7)
        self.POS_WIDTH = (self.BOARD_WIDTH - (number_of_discs - 1) * self.POS_SPACING) / number_of_discs
        self.POS_HEIGHT = 600

        self.PLATFORM_HEIGHT = 10

        self.DISC_WIDTH = self.POS_WIDTH
        self.DISC_HEIGHT = self.DISC_WIDTH

        # Draw the game board and it's positions
        self.game_board = Block(self.BOARD_COLOR, self.BOARD_WIDTH, self.BOARD_HEIGHT)
        self.game_board.rect.center = (
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + SCREEN_HEIGHT * 0.25,
        )
        self.BOARD_X = self.game_board.rect.x
        self.BOARD_Y = self.game_board.rect.y

        # self.set_new_positions()

        self.sprites_list.add([self.game_board, self.positions, self.platforms])
        self.pos_sprites_list.add(self.positions, self.platforms)

        self.start_positions = []
        self.end_positions = []

        self.start_discs = []
        self.end_discs = []

    def get_game_copy(self):
        game = Game(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.number_of_discs)
        game.number_of_positions = self.number_of_positions
        game.set_new_positions()
        game.discs = []
        for pos in game.positions:
            pos.discs = []
        for i in range(len(self.positions)):
            pos = self.positions[i]
            for disc in pos.discs:
                new_disc = Disc(0, disc.id, colors[disc.id], self.DISC_WIDTH, self.DISC_HEIGHT)
                new_disc.current_pos = i
                game.discs.append(new_disc)
                game.positions[i].discs.append(new_disc)
        game.search_by_width = self.search_by_width
        return game

    def set_new_positions(self):
        self.POS_SPACING = self.SCREEN_WIDTH / (self.number_of_positions * 7)
        self.POS_WIDTH = (
            self.BOARD_WIDTH - (self.number_of_positions - 1) * self.POS_SPACING
        ) / self.number_of_positions
        self.POS_HEIGHT = 400

        self.PLATFORM_HEIGHT = 10

        self.DISC_WIDTH = self.POS_WIDTH
        self.DISC_HEIGHT = self.DISC_WIDTH

        self.positions = []
        btn_discs = []
        for i in range(self.number_of_positions):
            pos = Position(i, self.PILLAR_COLOR, self.POS_WIDTH, self.POS_HEIGHT)
            pos.rect.x = self.BOARD_X + self.POS_WIDTH * i + self.POS_SPACING * i
            pos.rect.y = self.BOARD_Y - self.POS_HEIGHT

            btn = Button(str(i + 1), self.BLACK, 30, None, self.BOARD_COLOR, 20, 30)
            btn.rect.x = pos.rect.x + self.POS_WIDTH // 2 - btn.rect.width // 2
            btn.rect.y = pos.rect.y + self.POS_HEIGHT + self.PLATFORM_HEIGHT
            btn.render_text()
            btn.set_value(i + 1)
            btn_discs.append(btn)

            # self.start_position_button = Button("Izberite kot začetno stanje", self.BLACK, 30, None, self.BUTTON_COLOR, 300, 30)
            # self.start_position_button.rect.x = 20
            # self.start_position_button.rect.y = 150
            # self.start_position_button.render_text()

            platform = Block(self.PLATFORM_COLOR, self.POS_WIDTH, self.PLATFORM_HEIGHT)
            platform.rect.x = self.BOARD_X + self.POS_WIDTH * i + self.POS_SPACING * i
            platform.rect.y = self.BOARD_Y

            self.positions.append(pos)
            self.platforms.append(platform)

        self.sprites_list.add([self.positions, self.platforms])
        self.pos_sprites_list.add(self.positions, self.platforms)
        self.sprites_list.add(btn_discs)

    # Draw discs method
    def set_start_discs(self, set_sprites=True):
        DISC_WIDTH = self.DISC_HEIGHT
        DISC_HEIGHT = self.DISC_WIDTH
        for i in range(0, self.number_of_discs):
            disc = Disc(0, i, colors[i], DISC_WIDTH, DISC_HEIGHT)
            disc.rect.x = self.BOARD_X - (DISC_WIDTH) / 2 + self.POS_WIDTH / 2
            disc.rect.y = (self.BOARD_Y - DISC_HEIGHT) - (DISC_HEIGHT * i)
            self.discs.append(disc)
            self.positions[0].discs.append(disc)
        if set_sprites:
            self.sprites_list.add(self.discs)

    def set_discs_to_starting_pos(self):
        self.discs = []
        for pos in self.positions:
            pos.discs = []
        for disc in self.start_discs:
            self.discs.append(disc)
        self.discs = self.start_discs
        self.positions = self.start_positions
        self.sprites_list.add(self.discs)

    def refresh_discs(self):
        self.sprites_list.remove(self.discs)
        for i in range(len(self.discs)):
            disc = self.discs[i]
            disc.rect.x = self.positions[disc.current_pos].rect.x - (self.DISC_WIDTH) / 2 + self.POS_WIDTH / 2
            disc.rect.y = (self.BOARD_Y - self.DISC_HEIGHT) - self.DISC_HEIGHT * self.positions[
                disc.current_pos
            ].discs.index(disc)
        self.sprites_list.add(self.discs)
