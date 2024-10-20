import pygame
import sys
from utils import draw_text
from constants import BLACK, WHITE, GRAY, DARK_GRAY, BLUE, screen_width, screen_height
from quiz import quiz_ui

def menu(screen, username):
    pygame.init()
    clock = pygame.time.Clock()

    # Load fonts
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    label_font = pygame.font.SysFont('Arial', 24)
    input_font = pygame.font.SysFont('Arial', 22)
    button_font = pygame.font.SysFont('Arial', 24)

    # Load background image (optional)
    try:
        background_image = pygame.image.load('background_menu.jpg')
        background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    except FileNotFoundError:
        background_image = None

    # Colors
    INPUT_BOX_COLOR = pygame.Color('#d3d3d3')
    ACTIVE_BOX_COLOR = pygame.Color('#a9a9a9')
    BUTTON_COLOR = pygame.Color('#1E90FF')
    BUTTON_HOVER_COLOR = pygame.Color('#63B8FF')
    TEXT_COLOR = pygame.Color('white')

    # Default parameters
    num_particles = 50
    box_size = 600
    particle_radius = 5
    temperature = 1.0
    dt = 0.5
    total_steps = 2000

    input_boxes = [
        {'label': 'Number of Particles:', 'value': str(num_particles), 'rect': None},
        {'label': 'Box Size (pixels):', 'value': str(box_size), 'rect': None},
        {'label': 'Particle Radius (pixels):', 'value': str(particle_radius), 'rect': None},
        {'label': 'Initial Temperature:', 'value': str(temperature), 'rect': None},
        {'label': 'Time Step:', 'value': str(dt), 'rect': None},
        {'label': 'Total Steps:', 'value': str(total_steps), 'rect': None},
    ]

    active_input = None
    run = True
    while run:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)

        # Draw header
        header_rect = pygame.Rect(0, 0, screen_width, 80)
        pygame.draw.rect(screen, DARK_GRAY, header_rect)
        draw_text('Ideal Gas Simulation', title_font, TEXT_COLOR, screen, screen_width // 2, 40, center=True)

        # Draw footer with username
        footer_rect = pygame.Rect(0, screen_height - 40, screen_width, 40)
        pygame.draw.rect(screen, DARK_GRAY, footer_rect)
        draw_text(f'Logged in as: {username}', label_font, TEXT_COLOR, screen, 10, screen_height - 30)

        mx, my = pygame.mouse.get_pos()

        # Render input boxes
        y_offset = 100
        box_width = 300
        box_height = 40
        box_gap = 50
        input_box_rects = []
        for i, box in enumerate(input_boxes):
            # Label
            label_surface = label_font.render(box['label'], True, WHITE)
            label_rect = label_surface.get_rect(topleft=(50, y_offset + 10))
            screen.blit(label_surface, label_rect)

            # Input box
            rect = pygame.Rect(350, y_offset, box_width, box_height)
            color = ACTIVE_BOX_COLOR if active_input == i else INPUT_BOX_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=5)
            # Text inside input box
            text_surface = input_font.render(box['value'], True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
            box['rect'] = rect
            y_offset += box_gap

        # Start button
        start_button_rect = pygame.Rect(150, y_offset + 50, 150, 50)
        start_button_color = BUTTON_HOVER_COLOR if start_button_rect.collidepoint((mx, my)) else BUTTON_COLOR
        pygame.draw.rect(screen, start_button_color, start_button_rect, border_radius=10)
        draw_text('Start', button_font, WHITE, screen, start_button_rect.centerx, start_button_rect.centery, center=True)

        # Quiz button
        quiz_button_rect = pygame.Rect(350, y_offset + 50, 150, 50)
        quiz_button_color = BUTTON_HOVER_COLOR if quiz_button_rect.collidepoint((mx, my)) else BUTTON_COLOR
        pygame.draw.rect(screen, quiz_button_color, quiz_button_rect, border_radius=10)
        draw_text('Quiz', button_font, WHITE, screen, quiz_button_rect.centerx, quiz_button_rect.centery, center=True)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check if any input box is clicked
                    for i, box in enumerate(input_boxes):
                        if box['rect'].collidepoint((mx, my)):
                            active_input = i
                            break
                    else:
                        active_input = None

                    # Check if start button is clicked
                    if start_button_rect.collidepoint((mx, my)):
                        # Parse input values
                        try:
                            num_particles = int(input_boxes[0]['value'])
                            box_size = int(input_boxes[1]['value'])
                            particle_radius = int(input_boxes[2]['value'])
                            temperature = float(input_boxes[3]['value'])
                            dt = float(input_boxes[4]['value'])
                            total_steps = int(input_boxes[5]['value'])
                        except ValueError:
                            # Invalid input handling
                            error_message = "Please enter valid numerical values."
                            error_surface = label_font.render(error_message, True, pygame.Color('red'))
                            screen.blit(error_surface, (50, y_offset))
                            pygame.display.flip()
                            pygame.time.wait(2000)
                        else:
                            return num_particles, box_size, particle_radius, temperature, dt, total_steps

                    # Check if quiz button is clicked
                    if quiz_button_rect.collidepoint((mx, my)):
                        quiz_ui(screen, username)

            elif event.type == pygame.KEYDOWN:
                if active_input is not None:
                    if event.key == pygame.K_BACKSPACE:
                        input_boxes[active_input]['value'] = input_boxes[active_input]['value'][:-1]
                    elif event.key == pygame.K_RETURN:
                        active_input = None
                    else:
                        input_boxes[active_input]['value'] += event.unicode

        pygame.display.flip()
        clock.tick(60)

