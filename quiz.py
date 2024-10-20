# quiz.py
import pygame
import sys
from database import save_quiz_result  # Import your function to save results

def quiz_ui(screen, username):
    pygame.init()
    clock = pygame.time.Clock()

    # Load fonts
    font = pygame.font.SysFont('Arial', 24)
    small_font = pygame.font.SysFont('Arial', 18)

    # Define quiz questions and answers
    questions = [
        {
            'question': 'What is the ideal gas law?',
            'options': ['PV = nRT', 'E = mc^2', 'F = ma', 'V = IR'],
            'answer': 0
        },
        {
            'question': 'In the ideal gas law, what does "n" represent?',
            'options': ['Number of particles', 'Number of moles', 'Newton', 'Nano'],
            'answer': 1
        },
        # Add more questions here
    ]

    # Quiz variables
    current_question = 0
    selected_option = None
    score = 0

    run = True
    while run:
        screen.fill((0, 0, 0))  # Clear screen with black

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    # Check if an option is clicked
                    for i, option_rect in enumerate(option_rects):
                        if option_rect.collidepoint((mx, my)):
                            selected_option = i
                    # Check if 'Next' button is clicked
                    if next_button_rect.collidepoint((mx, my)):
                        if selected_option is not None:
                            if selected_option == questions[current_question]['answer']:
                                score += 1
                            current_question += 1
                            selected_option = None
                            if current_question >= len(questions):
                                run = False  # End quiz

        if current_question < len(questions):
            # Draw question
            question_text = font.render(questions[current_question]['question'], True, (255, 255, 255))
            screen.blit(question_text, (50, 50))

            # Draw options
            option_rects = []
            y_offset = 150
            for i, option in enumerate(questions[current_question]['options']):
                color = (200, 200, 200)
                if selected_option == i:
                    color = (100, 100, 255)
                option_text = small_font.render(f"{i + 1}. {option}", True, color)
                option_rect = option_text.get_rect(topleft=(70, y_offset))
                screen.blit(option_text, option_rect)
                option_rects.append(option_rect)
                y_offset += 40

            # Draw 'Next' button
            next_button_rect = pygame.Rect(300, 500, 100, 50)
            pygame.draw.rect(screen, (0, 128, 255), next_button_rect)
            next_text = font.render("Next", True, (255, 255, 255))
            screen.blit(next_text, (next_button_rect.x + 15, next_button_rect.y + 10))
        else:
            # Quiz is over, display final score
            screen.fill((0, 0, 0))
            final_text = font.render(f"Your score: {score}/{len(questions)}", True, (255, 255, 255))
            screen.blit(final_text, (200, 300))
            pygame.display.flip()
            pygame.time.wait(3000)  # Wait for 3 seconds before exiting
            break

        pygame.display.flip()
        clock.tick(60)

    # Save the quiz result
    save_quiz_result(username, score)
