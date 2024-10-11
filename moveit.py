import pygame
import spacy
from spacy.matcher import Matcher
import random

nlp = spacy.load("en_core_web_md")
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

jump_sound = pygame.mixer.Sound('jump.wav')
move_sound = pygame.mixer.Sound('move.wav')
color_change_sound = pygame.mixer.Sound('color_change.wav')

WHITE = (255, 255, 255)
circle_color = (0, 0, 255)
circle_radius = 30
circle_x = SCREEN_WIDTH // 2
circle_y = SCREEN_HEIGHT - circle_radius - 50
original_y = circle_y

jumping = False
falling = False
jump_speed = 10
fall_speed = 10
max_jump_height = 120

FPS = 60
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

instructions = "Type a command and press Enter"
commands = "(move left/right, jump, change color, exit)"

matcher = Matcher(nlp.vocab)
patterns = [
    [{"LEMMA": "move"}, {"LOWER": {"IN": ["left", "right"]}}],
    [{"LEMMA": "jump"}],
    [{"LEMMA": "change"}, {"LOWER": "color"}],
    [{"LEMMA": "exit"}],
]
matcher.add("COMMANDS", patterns)

error_message = ""
stored_action = None
input_message = ""


def display_text(text, y_position, color=(0, 0, 0), small=False):
    """Display text on the screen."""
    font_to_use = small_font if small else font
    rendered_text = font_to_use.render(text, True, color)
    text_rect = rendered_text.get_rect(center=(SCREEN_WIDTH // 2, y_position))
    screen.blit(rendered_text, text_rect)


def perform_jump():
    global jumping, falling, circle_y
    if jumping:
        if circle_y > max_jump_height:
            circle_y -= jump_speed
        else:
            jumping = False
            falling = True
    elif falling:
        if circle_y < original_y:
            circle_y += fall_speed
        else:
            falling = False


def handle_action(action, direction=None):
    global circle_x, circle_color, jumping, error_message

    if action == "move":
        if direction == "left":
            circle_x -= 20
            move_sound.play()
        elif direction == "right":
            circle_x += 20
            move_sound.play()
    elif action == "jump":
        if not jumping and not falling:
            jumping = True
            jump_sound.play()
            error_message = ""
    elif action == "color":
        circle_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        color_change_sound.play()
        error_message = ""
    elif action == "exit":
        pygame.quit()
        quit()


def process_command(command):
    global stored_action, error_message
    doc = nlp(command.lower())
    matches = matcher(doc)
    action = None
    direction = None

    for token in doc:
        if token.text in ["left", "right"]:
            direction = token.text

    for match_id, start, end in matches:
        span = doc[start:end]
        if span.text == "move left" or span.text == "move right":
            action = "move"
            direction = span[-1].text
            break
        elif span.text == "jump":
            action = "jump"
            break
        elif span.text == "change color":
            action = "color"
            break
        elif span.text == "exit":
            action = "exit"
            break

    if not action:
        error_message = "Unrecognized action. Try typing 'move left/right', 'jump', or 'change color'."
    else:
        handle_action(action, direction)
        stored_action = None

# Main game loop
running = True
while running:
    screen.fill(WHITE)
    pygame.draw.circle(screen, circle_color, (circle_x, int(circle_y)), circle_radius)
    display_text(instructions, 50)
    display_text(commands, 80, small=True)
    display_text(input_message, 120, color=(100, 100, 100))

    if error_message:
        display_text(error_message, 500, color=(255, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if input_message.strip():
                    process_command(input_message.strip())
                    input_message = ''
                error_message = ''
            elif event.key == pygame.K_BACKSPACE:
                input_message = input_message[:-1]
            else:
                input_message += event.unicode

    if jumping or falling:
        perform_jump()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
