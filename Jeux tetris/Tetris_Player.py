import pygame
import sys
import random
import os

# Initialisation de Pygame
pygame.init()

# Définir les dimensions de la fenêtre et les couleurs
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GAME_WIDTH = 300
GAME_HEIGHT = 600
INFO_WIDTH = 150
INFO_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# Définir les couleurs possibles pour chaque type de forme
SHAPE_COLORS = {
    "line": (0, 255, 255),    # Cyan
    "square": (255, 0, 0),    # Red
    "t": (0, 255, 0),         # Green
    "l": (0, 0, 255),         # Blue
    "l_inv": (255, 255, 0),   # Yellow
    "s": (255, 165, 0),       # Orange
    "z": (128, 0, 128)        # Purple
}

SHAPES = {
    "line": [[1, 1, 1, 1]],
    "square": [[1, 1], [1, 1]],
    "t": [[0, 1, 0], [1, 1, 1]],
    "l": [[1, 0, 0], [1, 1, 1]],
    "l_inv": [[0, 0, 1], [1, 1, 1]],
    "s": [[0, 1, 1], [1, 1, 0]],
    "z": [[1, 1, 0], [0, 1, 1]]
}


# Initialiser l'écran et définir le titre de la fenêtre
SCREEN = pygame.display.set_mode((SCREEN_WIDTH + INFO_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')


# Initialisation de la grille principale et de la grille de couleurs
GRID = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
COLOR_GRID = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


# Chemin du répertoire du script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialisation du mixer Pygame
pygame.mixer.init()
drop_sound = pygame.mixer.Sound(os.path.join(script_dir, 'sounds/block_drop.wav'))
background = pygame.image.load(os.path.join(script_dir, 'background.jpg'))
SCREEN.blit(background, (0, 0))



#_______________Fonctions______________________

def get_shape():
    shape_type = random.choice(list(SHAPES.keys()))
    return SHAPES[shape_type], SHAPE_COLORS[shape_type]

"""
def test(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])): 
            if matrix[i][j] is None:
                print("None, ", end="")
            else:
                print(str(matrix[i][j]) + ", ", end="")
        print("\n")
"""

def draw_shadowed_rect(surface, color, rect):
    x, y, w, h = rect
    shadow_color = (50, 50, 50)  # Shadow color
    pygame.draw.rect(surface, shadow_color, (x+3, y+3, w, h))  # Draw shadow
    pygame.draw.rect(surface, color, rect)  # Draw main rectangle
    pygame.draw.line(surface, (255, 255, 255), (x, y), (x+w, y), 2)  # Top highlight
    pygame.draw.line(surface, (255, 255, 255), (x, y), (x, y+h), 2)  # Left highlight


def draw_shape(matrix, offset, current_color = None):
    off_x, off_y = offset
    for y in range(len(matrix)):
        for x in range(len(matrix[0])):
            if matrix[y][x]:
                grid_x = (off_x // BLOCK_SIZE) + x
                grid_y = (off_y // BLOCK_SIZE) + y

                color = current_color if current_color else WHITE
                draw_shadowed_rect(SCREEN, color, pygame.Rect(grid_x * BLOCK_SIZE, grid_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))


def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if GRID[y][x]:
                color = COLOR_GRID[y][x]
                draw_shadowed_rect(SCREEN, color, pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(SCREEN, GRAY, pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def check_collision(shape, offset):
    off_x, off_y = offset
    for y in range(len(shape)):
        for x in range(len(shape[0])):
            if shape[y][x]:
                grid_x = (off_x // BLOCK_SIZE) + x
                grid_y = (off_y // BLOCK_SIZE) + y
                if (grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT or GRID[grid_y][grid_x]):
                    return True
    return False


def rotate(shape):
    return [ [ shape[y][x]
            for y in range(len(shape)) ]
            for x in range(len(shape[0]) - 1, -1, -1) ]


def remove_line():
    global GRID, COLOR_GRID

    # Liste des indices des lignes pleines
    full_lines = []
    for y in range(GRID_HEIGHT):
        if all(GRID[y][x] != 0 for x in range(GRID_WIDTH)):
            full_lines.append(y)
    
    lines_removed = len(full_lines)

    # Suppression des lignes pleines et ajout de nouvelles lignes vides au début
    new_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(lines_removed)]
    new_color_grid = [[None for _ in range(GRID_WIDTH)] for _ in range(lines_removed)]

    for y in range(GRID_HEIGHT):
        if y not in full_lines:
            new_grid.append(GRID[y])
            new_color_grid.append(COLOR_GRID[y])
    
    GRID = new_grid
    COLOR_GRID = new_color_grid

    return lines_removed


def show_message(line1, line2):
    font1 = pygame.font.SysFont("comicsansms", 48)
    font2 = pygame.font.SysFont("comicsansms", 25)


    label1 = font1.render(line1, True, WHITE)
    label2 = font2.render(line2, True, WHITE)

    message_surface = pygame.Surface((SCREEN_WIDTH, label1.get_height() + label2.get_height()), pygame.SRCALPHA)
    message_surface.fill((0, 0, 0, 180))  # Remplir avec un fond transparent

    message_surface.blit(label1, label1.get_rect(center=(SCREEN_WIDTH // 2, label1.get_height() // 2)).topleft)
    message_surface.blit(label2, label2.get_rect(center=(SCREEN_WIDTH // 2, label1.get_height() + label2.get_height() // 2)).topleft)

    # Afficher la surface du message sur l'écran
    message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    SCREEN.blit(message_surface, message_rect.topleft)
    pygame.display.update()
    pygame.time.delay(2000)  # Afficher le message pendant 2 secondes

def draw_info(score):
    # Créer une surface avec une transparence (alpha)
    info_surface = pygame.Surface((INFO_WIDTH, INFO_HEIGHT), pygame.SRCALPHA)
    info_surface.fill((128, 128, 128, 128))  # Couleur grise avec alpha à 128 (semi-transparent)
    
    font = pygame.font.SysFont('Arial', 24)
    text = font.render(f"Score: {score}", True, WHITE)
    info_surface.blit(text, (20, 20))
    next_text = font.render("Next:", True, WHITE)
    info_surface.blit(next_text, (20, 70))

    SCREEN.blit(info_surface, (GAME_WIDTH, 0))


def calculate_score(lines_removed):
    if lines_removed == 2:
        return 300
    elif lines_removed == 3:
        return 500
    elif lines_removed == 4:
        return 800
    else:
        return lines_removed * 100 

def reset_game():
    global GRID, COLOR_GRID, current_shape, current_color, next_shape, next_color, shape_pos, score, fall_time, game_over
    GRID = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    COLOR_GRID = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_shape, current_color = get_shape()
    next_shape, next_color = get_shape()
    shape_pos = [SCREEN_WIDTH // 2 - BLOCK_SIZE, 0]
    score = 0
    fall_time = 0
    game_over = False

def main():
    global GRID, COLOR_GRID, current_shape, current_color, next_shape, next_color, shape_pos, score, fall_time, game_over
    clock = pygame.time.Clock()
    current_shape, current_color = get_shape()  # Type de la pièce courante et sa couleur
    shape_pos = [SCREEN_WIDTH // 2 - BLOCK_SIZE, 0]     #position départ
    next_shape, next_color = get_shape()
    score = 0
    fall_time = 0
    fall_speed = 0.5
    game_over = False


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN :
                new_pos = list(shape_pos)
                if event.key == pygame.K_LEFT:
                    new_pos[0] -= BLOCK_SIZE
                elif event.key == pygame.K_RIGHT:
                    new_pos[0] += BLOCK_SIZE
                elif event.key == pygame.K_DOWN:
                    new_pos[1] += BLOCK_SIZE
                elif event.key == pygame.K_UP:
                    new_shape = rotate(current_shape)
                    if not check_collision(new_shape, shape_pos):
                        current_shape = new_shape
                if not check_collision(current_shape, new_pos):
                    shape_pos = new_pos

                if event.key == pygame.K_SPACE and game_over:
                    reset_game()
                elif event.key == pygame.K_SPACE and not game_over:
                    show_message("Game Over", "Presse espace to restart")
                    game_over = True

        if not game_over:
            # Temps écoulé depuis le dernier appel de tick() en secondes
            fall_time += clock.get_time() / 1000

            if fall_time >= fall_speed:
                fall_time = 0
                new_pos = [shape_pos[0], shape_pos[1] + BLOCK_SIZE]
                if not check_collision(current_shape, new_pos):
                    shape_pos = new_pos
                else:
                    # Mise à jour de la grille
                    for y in range(len(current_shape)):
                        for x in range(len(current_shape[0])):
                            if current_shape[y][x]:
                                grid_x = (shape_pos[0] // BLOCK_SIZE) + x
                                grid_y = (shape_pos[1] // BLOCK_SIZE) + y
                                GRID[grid_y][grid_x] = 1
                                COLOR_GRID[grid_y][grid_x] = current_color
                                
                    lines_removed = remove_line()
                    score += calculate_score(lines_removed)
                    drop_sound.play()

                    # Générer une nouvelle forme
                    current_shape = next_shape
                    current_color = next_color
                    next_shape, next_color = get_shape()
                    shape_pos = [SCREEN_WIDTH // 2 - BLOCK_SIZE, 0]

                    # Vérifier si le jeu est terminé
                    if check_collision(current_shape, shape_pos):
                        show_message("Game Over", "Presse espace to restart")
                        game_over = True



        if not game_over:
            # Dessiner la grille et la pièce courante
            SCREEN.blit(background, (0, 0)) # Réinitialiser l'écran
            draw_grid()
            draw_shape(current_shape, shape_pos, current_color)
            draw_info(score)
            draw_shape(next_shape, (GAME_WIDTH + 40, GAME_HEIGHT // 4), next_color)  # Positionner la prochaine pièce



        pygame.display.update()
        clock.tick(30)  # Limiter l'actualisation à 30 images par seconde

if __name__ == "__main__":
    main()