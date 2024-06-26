import pygame
import random
import heapq
import math

WIDTH, HEIGHT = 800, 600
ROWS, COLS = 30, 40
BLOCK_SIZE = WIDTH // COLS
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_RED = (255, 200, 200)
YELLOW = (255, 255, 0)

# Initialization of Pygame
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labyrinthe")


def distance(p1, p2):
    """Calculates the Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = GREEN
        self.size = BLOCK_SIZE // 2
        self.move_counter = 0
        self.move_delay = 10  # Nombre de ticks entre les mouvements
        self.direction = (0, 1)  # Initial direction pointing upwards

    
    def get_triangle_points(self):
        cx = self.x * BLOCK_SIZE + BLOCK_SIZE // 2
        cy = self.y * BLOCK_SIZE + BLOCK_SIZE // 2
        dx, dy = self.direction

        if dx == 0 and dy == -1:  # Up
            points = [(cx, cy - self.size), (cx - self.size, cy + self.size), (cx + self.size, cy + self.size)]
        elif dx == 0 and dy == 1:  # Down
            points = [(cx, cy + self.size), (cx - self.size, cy - self.size), (cx + self.size, cy - self.size)]
        elif dx == -1 and dy == 0:  # Left
            points = [(cx - self.size, cy), (cx + self.size, cy - self.size), (cx + self.size, cy + self.size)]
        elif dx == 1 and dy == 0:  # Right
            points = [(cx + self.size, cy), (cx - self.size, cy - self.size), (cx - self.size, cy + self.size)]
        else:
            points = [(cx, cy - self.size), (cx - self.size, cy + self.size), (cx + self.size, cy + self.size)]

        return points

    def draw(self, SCREEN):
        pygame.draw.polygon(SCREEN, self.color, self.get_triangle_points())

    def move(self, dx, dy, maze):
        self.move_counter += 1
        if self.move_counter > self.move_delay:
            self.move_counter = 0

            new_x = self.x + dx
            new_y = self.y + dy
            if maze[int(new_y)][int(new_x)] == 0:
                self.x = new_x
                self.y = new_y
                if dx != 0 or dy != 0:
                    self.direction = (dx, dy)


class Soldier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = RED
        self.vision_range = 5
        self.path = []
        self.target = None
        self.move_counter = 0
        self.move_delay = 30
    
    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, (self.x * BLOCK_SIZE, self.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        #self.draw_vision(SCREEN)
    
    def draw_vision(self, SCREEN):
        vision_radius = self.vision_range * BLOCK_SIZE
        pygame.draw.circle(SCREEN, LIGHT_RED, (int(self.x * BLOCK_SIZE + BLOCK_SIZE / 2), int(self.y * BLOCK_SIZE + BLOCK_SIZE / 2)), vision_radius, 1)
    
    def is_position_valid(self, maze, player, soldiers):
        # Check distance to all existing soldiers
        for soldier in soldiers:
            if distance((self.x, self.y), (soldier.x, soldier.y)) < self.vision_range * 2:
                return False
        
        # Check distance to player
        if distance((self.x, self.y), (player.x, player.y)) < self.vision_range * 2:
            return False
        
        # Check if the position is on a free cell in the maze
        if maze[self.y][self.x] != 0:
            return False
        
        return True
    
    def choose_random_target(self, maze):
        while True:
            target_x = random.randint(1, COLS - 2)  #pas les contours de l'arène
            target_y = random.randint(1, ROWS - 2)
            if maze[target_y][target_x] == 0:
                self.target = (target_x, target_y)
                path_found, _, path = a_star(maze, (self.x, self.y), self.target)
                if path_found:
                    self.path = path[1:]  # Exclude the current position
                    break

    def move_towards_player(self, player, maze):
        self.move_counter += 1
        if self.move_counter > self.move_delay:
            self.move_counter = 0

            if abs(self.x - player.x) <= self.vision_range and abs(self.y - player.y) <= self.vision_range: 
                path_found, _, path = a_star(maze, (self.x, self.y), (player.x, player.y))
                if path_found:
                    self.path = path[1:]  # Exclude the current position
                self.target = None
                #print("en chasse")
            else:
                if self.target is None or (self.x, self.y) == self.target:
                    self.choose_random_target(maze)

            if self.path:
                next_move = self.path.pop(0)
                self.x, self.y = next_move

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

def a_star(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    closed_set = set()
    search_steps = []

    while open_set:
        current = heapq.heappop(open_set)[1]
        search_steps.append(current)
        closed_set.add(current)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            return True, search_steps, path

        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows:
                if maze[neighbor[1]][neighbor[0]] == 1:
                    continue
                tentative_g_score = g_score[current] + 1

                if neighbor in closed_set:
                    continue

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return False, search_steps, None

def generate_maze(rows, cols):
    while True:
        maze = [[0 if random.random() > 0.35 else 1 for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            maze[i][0] = maze[i][cols - 1] = 1
        for j in range(cols):
            maze[0][j] = maze[rows - 1][j] = 1
        maze[1][1] = 0
        maze[rows - 2][cols - 2] = 0  # Create exit

        #Vérifie qu'un chemin est possible
        path_exists, search_steps, path = a_star(maze, (1, 1), (COLS - 2, ROWS - 2))
        if path_exists:
            return maze, search_steps, path

def draw_maze(SCREEN, maze):
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            color = BLACK if tile else WHITE
            pygame.draw.rect(SCREEN, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    # Draw the exit
    pygame.draw.rect(SCREEN, BLUE, ((COLS - 2) * BLOCK_SIZE, (ROWS - 2) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def display_message(message):
    font1 = pygame.font.SysFont("comicsansms", 48)
    label1 = font1.render(message, True, WHITE)

    message_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    message_surface.fill((0, 0, 0, 180))  # Remplir avec un fond transparent
    message_surface.blit(label1, label1.get_rect(center=(WIDTH // 2, HEIGHT // 3)))

    # Afficher la surface du message sur l'écran
    message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    SCREEN.blit(message_surface, message_rect)
    pygame.display.update()
    pygame.time.delay(5000)



def main():
    clock = pygame.time.Clock()
    maze, search_steps, path = generate_maze(ROWS, COLS)
    game_over = False
    player = Player(1, 1)
    pygame.time.delay(3000)


    soldiers = []
    for _ in range(5):
        while True:
            x = random.randint(1, COLS-2)
            y = random.randint(1, ROWS-2)
            soldier = Soldier(x, y)
            if soldier.is_position_valid(maze, player, soldiers):
                soldiers.append(soldier)
                break

    search_step_index = 0

    while search_step_index < len(search_steps):
        x, y = search_steps[search_step_index]
        pygame.draw.rect(SCREEN, YELLOW, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        search_step_index += 1
        pygame.display.flip()
        pygame.time.delay(10)  # Delay to clearly show the path

    # Once A* search is complete, show the final path
    if path:
        for x, y in path:
            pygame.draw.rect(SCREEN, GREEN, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            pygame.display.flip()
            pygame.time.delay(10)  # Delay to clearly show the path
    pygame.time.delay(1000)  # Delay to clearly show the path

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
        
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1

        player.move(dx, dy, maze)

        for soldier in soldiers:
            soldier.move_towards_player(player, maze)
            if int(soldier.x) == int(player.x) and int(soldier.y) == int(player.y):
                display_message("Game Over !")
                game_over = True
        
        if int(player.x) == COLS - 2 and int(player.y) == ROWS - 2:
            display_message("You win !")
            game_over = True

        SCREEN.fill(WHITE)
        draw_maze(SCREEN, maze)
        player.draw(SCREEN)
        for soldier in soldiers:
            soldier.draw(SCREEN)

        pygame.display.update()
        clock.tick(FPS)
   
    pygame.quit()

if __name__ == "__main__":
    main()