import pygame
import sys
import random
import os
import numpy as np

pygame.init()

GAME_WIDTH = 300
GAME_HEIGHT = 600
INFO_WIDTH = 200
INFO_HEIGHT = 600
SCREEN_WIDTH =  GAME_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

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


SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')


GRID = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
COLOR_GRID = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


# Chemin du répertoire du script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialisation du mixer Pygame
pygame.mixer.init()
drop_sound = pygame.mixer.Sound(os.path.join(script_dir, 'sounds/block_drop.wav'))
ligne_sound = pygame.mixer.Sound(os.path.join(script_dir, 'sounds/ligne_completed.wav'))
game_over_sound = pygame.mixer.Sound(os.path.join(script_dir, 'sounds/game_over.wav'))
button_sound = pygame.mixer.Sound(os.path.join(script_dir, 'sounds/click_button.wav'))

try:
    pygame.mixer.music.load(os.path.join(script_dir, 'sounds/background_music.wav'))
    # Jouer la musique en boucle
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Impossible de charger la musique : {e}")

background = pygame.image.load(os.path.join(script_dir, 'background.jpg'))
SCREEN.blit(background, (0, 0))

clock = pygame.time.Clock()


#_______________Fonctions______________________

def get_buttons():
    button_rect1 = pygame.Rect(GAME_WIDTH + 30, GAME_HEIGHT // 2, 30, 30)
    button_rect2 = pygame.Rect(GAME_WIDTH + 90, GAME_HEIGHT // 2, 30, 30)

    return button_rect1, button_rect2
    
def get_shape():
    shape_type = random.choice(list(SHAPES.keys()))
    return SHAPES[shape_type], SHAPE_COLORS[shape_type]

def draw_button(button, texte):
    font = pygame.font.Font(None, 36)
    text = font.render(texte, True, BLACK)
    text_rect = text.get_rect(center=button.center)
    pygame.draw.rect(SCREEN, WHITE, button)
    SCREEN.blit(text, text_rect)

def draw_shadowed_rect(surface, color, rect, alpha):
    x, y, w, h = rect
    shadow_color = (50, 50, 50, alpha)  # Couleur de l'ombre avec alpha
    shape_color = color + (alpha,)  # Ajouter alpha à la couleur de la forme

    shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    shadow_surf.fill(shadow_color)
    surface.blit(shadow_surf, (x+3, y+3))

    shape_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    shape_surf.fill(shape_color)
    surface.blit(shape_surf, (x, y))

    pygame.draw.line(surface, (255, 255, 255), (x, y), (x+w, y), 2)
    pygame.draw.line(surface, (255, 255, 255), (x, y), (x, y+h), 2)



def draw_shape(matrix, offset, color = WHITE, alpha = 128):
    off_x, off_y = offset
    for y in range(len(matrix)):
        for x in range(len(matrix[0])):
            if matrix[y][x]:
                grid_x = (off_x // BLOCK_SIZE) + x
                grid_y = (off_y // BLOCK_SIZE) + y

                draw_shadowed_rect(SCREEN, color, pygame.Rect(grid_x * BLOCK_SIZE, grid_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), alpha)


def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if GRID[y][x]:
                color = COLOR_GRID[y][x]
                draw_shadowed_rect(SCREEN, color, pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 128)
            else:
                pygame.draw.rect(SCREEN, GRAY, pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)


def check_collision(grid, shape, offset):
    off_x, off_y = offset
    for y in range(len(shape)):
        for x in range(len(shape[0])):
            if shape[y][x]:
                grid_x = (off_x // BLOCK_SIZE) + x
                grid_y = (off_y // BLOCK_SIZE) + y
                if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT or (grid_y >= 0 and grid[grid_y][grid_x]):
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

    message_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    message_surface.fill((0, 0, 0, 180))  # Remplir avec un fond transparent

    message_surface.blit(label1, label1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))
    message_surface.blit(label2, label2.get_rect(center=(SCREEN_WIDTH // 2, label1.get_height() + SCREEN_HEIGHT // 3)))

    # Afficher la surface du message sur l'écran
    message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    SCREEN.blit(message_surface, message_rect)
    pygame.display.update()
    #pygame.time.delay(2000)  # Afficher le message pendant 2 secondes




def draw_info(score, next_shape, next_color):
    info_surface = pygame.Surface((INFO_WIDTH, INFO_HEIGHT), pygame.SRCALPHA)
    info_surface.fill((128, 128, 128, 128))
    
    font = pygame.font.SysFont('Arial', 24)
    text = font.render(f"Score: {score}", True, WHITE)
    info_surface.blit(text, (20, 20))
    next_text = font.render("Next:", True, WHITE)
    info_surface.blit(next_text, (20, 70))
    SCREEN.blit(info_surface, (GAME_WIDTH, 0))

    draw_shape(next_shape, (INFO_WIDTH //3 + GAME_WIDTH, INFO_HEIGHT // 4), next_color) 



def calculate_score(lines_removed):
    if lines_removed == 2:
        return 300
    elif lines_removed == 3:
        return 500
    elif lines_removed == 4:
        return 800
    else:
        return lines_removed * 100 


def calculate_heights(grid):
    heights = [0] * len(grid[0])
    for x in range(len(grid[0])):
        for y in range(len(grid)):
            if grid[y][x] != 0:
                heights[x] = len(grid) - y
                break
    return heights


def count_holes(grid):
    holes = 0
    for x in range(len(grid[0])):
        block_found = False
        for y in range(len(grid)):
            if grid[y][x] != 0:
                block_found = True
            elif grid[y][x] == 0 and block_found:
                holes += 1
    return holes

def calculate_height_disparity(heights):
    return sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1))

def calculate_lines_cleared(grid):
    lines_cleared = sum(1 for y in range(len(grid)) if all(grid[y][x] != 0 for x in range(len(grid[0]))))
    return lines_cleared

def get_possible_moves(grid, shape):
    # Prends en compte la grille et le type de pièce, et trouve les endroits où elle peut etre placé. Prends en compte les rotations de la pièce 
    # Retourne une liste avec à chaque fois la forme de la pièce (son orientation) et la position (chaque position à une abcisse et un ordonnée)

    possible_moves = []

    # Calculer toutes les rotations possibles de la pièce
    rotations = [shape]
    rotated_shape = shape
    for _ in range(3):
        rotated_shape = rotate(rotated_shape)
        rotations.append(rotated_shape)

    # Parcourir chaque rotation et chaque position possible où la pièce pourrait être placée
    for current_shape in rotations:
        shape_width = len(current_shape[0])
        shape_height = len(current_shape)

        for x in range(GRID_WIDTH - shape_width + 1):
            y = 0
            while y <= GRID_HEIGHT - shape_height:
                if not check_collision(grid, current_shape, (x * BLOCK_SIZE, y * BLOCK_SIZE)):
                    y += 1
                else:
                    break
            
            # Vérifier si la pièce peut être placée à cette position
            if y > 0:
                possible_moves.append((current_shape, (x * BLOCK_SIZE, (y - 1) * BLOCK_SIZE)))

    return possible_moves

'''
max_height : Pénalise les colonnes trop hautes. Poids = ?.
holes : Les trous sont très pénalisants car ils rendent le nettoyage des lignes difficile. Poids = ?.
height_disparity : Pénalise les grandes différences de hauteur entre colonnes adjacentes. Poids = ?.
total_height : Pénalise les hauteurs globales élevées. Poids = ?.
lines_cleared : Favorise énormément la formation de ligne complète car elles permettent de les faire disparaitre . Poids = ?.
'''

def evaluate_move(shape, next_shape):
    #Critères
    weights = {
    'max_height': -0.5,
    'holes': -1.0,
    'height_disparity': -0.2,
    'total_height': -0.3,
    'lines_cleared': 1.0
    }
    best_move = None
    best_score = float('-inf')

    possible_moves = get_possible_moves(GRID, shape)
    for shape, position in possible_moves:
        temp_grid = [row[:] for row in GRID]
        temp_grid = simul_placement(temp_grid, shape, position)

        next_moves = get_possible_moves(temp_grid, next_shape)
        for next_shape, next_position in next_moves:
            temp_grid2 = [row[:] for row in temp_grid]
            temp_grid2 = simul_placement(temp_grid2, next_shape, next_position)
            
    
            heights = calculate_heights(temp_grid2)
            lines_cleared = calculate_lines_cleared(temp_grid2)
            holes = count_holes(temp_grid2)
            height_disparity = calculate_height_disparity(heights)
            total_height = sum(heights)

            # Calculer le score pour cette configuration
            score = (
                weights['max_height'] * max(heights) +
                weights['holes'] * holes +
                weights['height_disparity'] * height_disparity +
                weights['total_height'] * total_height +
                weights['lines_cleared'] * lines_cleared
            )

            if score > best_score:
                best_score = score
                best_move = (shape, position)

    return best_move
    
def simul_placement (temp_grid, shape, position):
    # Simuler le placement de la pièce dans la grille temporaire
    for y in range(len(shape)):
        for x in range(len(shape[0])):
            if shape[y][x]:
                grid_x = (position[0] // BLOCK_SIZE) + x
                grid_y = (position[1] // BLOCK_SIZE) + y
                if grid_y < GRID_HEIGHT:  # Vérifier que la pièce est dans la grille
                    temp_grid[grid_y][grid_x] = 1
    return temp_grid

def screen_updated(button_rect1, button_rect2):
    global GRID, COLOR_GRID, clock, current_shape, current_color, shape_pos, next_shape, next_color, score, best_move, is_moving
    SCREEN.blit(background, (0, 0))  # Réinitialiser l'écran
    draw_grid()
    draw_shape(current_shape, shape_pos, current_color)
    if (is_moving):
        (best_shape, best_position) = best_move
        draw_shape(best_shape, best_position, WHITE, 100)
    draw_info(score, next_shape, next_color)


    draw_button(button_rect1, "-")
    draw_button(button_rect2, "+")
    pygame.display.update()
    clock.tick(240)  # Images par seconde

def reset_game():
    global GRID, COLOR_GRID, current_shape, current_color, next_shape, next_color, shape_pos, score, fall_time, game_over, best_move, is_moving
    GRID = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    COLOR_GRID = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_shape, current_color = get_shape()
    next_shape, next_color = get_shape()
    shape_pos = [GAME_WIDTH // 2 - BLOCK_SIZE, 0]
    score = 0
    fall_time = 0
    game_over = False
    best_move = None
    is_moving = False

def game_Over():
    global game_over
    show_message("Game Over", "Press space to restart")
    game_over = True
    game_over_sound.play()

def main():
    global GRID, COLOR_GRID, clock, current_shape, current_color, shape_pos, next_shape, next_color, score, fall_time, fall_delay, game_over, best_move, is_moving
    current_shape, current_color = get_shape()
    shape_pos = [GAME_WIDTH // 2 - BLOCK_SIZE, 0]
    next_shape, next_color = get_shape()
    button_rect1, button_rect2 = get_buttons()
    
    score = 0
    fall_time = 0
    fall_delay = 0.2
    game_over = False
    best_move = None
    is_moving = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if (game_over):
                    reset_game()
                else:
                    game_Over()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect1.collidepoint(event.pos):
                    fall_delay *= 2
                elif button_rect2.collidepoint(event.pos):
                    fall_delay /= 2
                #print(fall_delay)
                button_sound.play()

        if not game_over:
            fall_time += clock.get_time() / 1000
            if fall_time >= fall_delay:     # Delay atteint
                fall_time = 0

                if check_collision(GRID, current_shape, shape_pos):     # Game Over
                        game_Over()

                if check_collision(GRID, current_shape, (shape_pos[0], shape_pos[1] + BLOCK_SIZE)):   # Pièce placée
                    for y in range(len(current_shape)):
                        for x in range(len(current_shape[0])):
                            if current_shape[y][x]:
                                grid_x = (shape_pos[0] // BLOCK_SIZE) + x
                                grid_y = (shape_pos[1] // BLOCK_SIZE) + y
                                GRID[grid_y][grid_x] = 1
                                COLOR_GRID[grid_y][grid_x] = current_color
                                drop_sound.play()
                                    
                    lines_removed = remove_line()
                    if (lines_removed > 0):
                        score += calculate_score(lines_removed)
                        ligne_sound.play()
                    
                     
                    # Générer une nouvelle forme
                    current_shape = next_shape
                    current_color = next_color
                    next_shape, next_color = get_shape()
                    shape_pos = [GAME_WIDTH // 2 - BLOCK_SIZE, 0]
                    best_move = None
                    is_moving = False

                if not is_moving and best_move is None: 
                    best_move = evaluate_move(current_shape, next_shape) # l'IA choisi le meilleur pos
                    if best_move is not None:
                        is_moving = True

                if is_moving and best_move is not None: # mouv auto vers pos
                    best_shape, best_position = best_move
                    target_x, target_y = best_position

                    if current_shape != best_shape:
                        current_shape = rotate(current_shape)
                    if shape_pos[0] < target_x:
                        shape_pos[0] += BLOCK_SIZE
                    elif shape_pos[0] > target_x:
                        shape_pos[0] -= BLOCK_SIZE
                    elif shape_pos[1] < target_y:
                        shape_pos[1] += BLOCK_SIZE
                    else:
                        is_moving = False
                        best_move = None

            screen_updated(button_rect1, button_rect2)


if __name__ == "__main__":
    main()







