import pygame
import spacy
import random

nlp = spacy.load("en_core_web_sm")
pygame.init()
pygame.mixer.init()

move_sound = pygame.mixer.Sound('move.wav')
jump_sound = pygame.mixer.Sound('jump.wav')
color_change_sound = pygame.mixer.Sound('color_change.wav')
exit_sound = pygame.mixer.Sound('exit.wav')

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("MoveIt!")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]
current_color = colors[0]

# Character settings
char_x, char_y = screen_width // 2, screen_height - 100
char_size = 50
jump_height = 150
gravity = 5
is_jumping = False
jump_count = 10

# FPS settings
clock = pygame.time.Clock()

available_commands = ["move left", "move right", "jump", "change color", "exit"]

def process_command(command):
    global char_x, char_y, current_color, is_jumping, running

    doc = nlp(command.lower())
    for token in doc:
        if token.text in ["left", "right", "jump", "color", "exit"]:
            if token.text == "left":
                char_x -= 50
                move_sound.play()
            elif token.text == "right":
                char_x += 50
                move_sound.play()
            elif token.text == "jump" and not is_jumping:
                is_jumping = True
                jump_sound.play()
            elif token.text == "color":
                current_color = random.choice(colors)
                color_change_sound.play()
            elif token.text == "exit":
                exit_sound.play()
                pygame.time.wait(300)
                running = False

def display_available_commands():
    font = pygame.font.Font(None, 24)
    commands_text = "Commands: " + ", ".join(available_commands)
    text = font.render(f"({commands_text})", True, BLACK)
    text_rect = text.get_rect(center=(screen_width // 2, 100))
    screen.blit(text, text_rect)

def display_prompt():
    font = pygame.font.Font(None, 36)
    prompt_text = "Type a command and press Enter:"
    text = font.render(prompt_text, True, BLACK)
    text_rect = text.get_rect(center=(screen_width // 2, 50))
    screen.blit(text, text_rect)

# Main
def game_loop():
    global char_x, char_y, is_jumping, jump_count, running
    running = True
    input_command = ""
    cursor_visible = True
    cursor_counter = 0

    while running:
        screen.fill(WHITE)

        pygame.draw.circle(screen, current_color, (char_x, char_y), char_size)
        display_prompt()
        display_available_commands()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    process_command(input_command)
                    input_command = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_command = input_command[:-1]
                else:
                    input_command += event.unicode

        if is_jumping:
            if jump_count >= -10:
                neg = 1
                if jump_count < 0:
                    neg = -1
                char_y -= (jump_count ** 2) * 0.5 * neg
                jump_count -= 1
            else:
                jump_count = 10
                is_jumping = False

        font = pygame.font.Font(None, 36)
        text = font.render(input_command, True, BLACK)
        text_rect = text.get_rect(center=(screen_width // 2, 150))
        screen.blit(text, text_rect)

        cursor_counter += 1
        if cursor_counter % 60 < 30:
            cursor_visible = True
        else:
            cursor_visible = False

        if cursor_visible:
            cursor = font.render("|", True, BLACK)
            screen.blit(cursor, (text_rect.right + 5, text_rect.top))

        pygame.display.flip()
        clock.tick(30)

game_loop()
pygame.quit()
