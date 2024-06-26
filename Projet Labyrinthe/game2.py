import pygame
import random
import heapq

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

# Player Class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = GREEN
        self.size = BLOCK_SIZE // 2
    
    def draw(self, SCREEN):
        pygame.draw.polygon(SCREEN, self.color, [
            (self.x * BLOCK_SIZE + BLOCK_SIZE // 2, self.y * BLOCK_SIZE + 3),
            (self.x * BLOCK_SIZE + 3, self.y * BLOCK_SIZE + BLOCK_SIZE - 3),
            (self.x * BLOCK_SIZE + BLOCK_SIZE - 3, self.y * BLOCK_SIZE + BLOCK_SIZE - 3)
        ])

    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy
        if maze[int(new_y)][int(new_x)] == 0:
            self.x = new_x
            self.y = new_y

# Soldier Class
class Soldier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = RED
        self.vision_range = 5
    
    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, (self.x * BLOCK_SIZE, self.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        self.draw_vision(SCREEN)
    
    def draw_vision(self, SCREEN):
        vision_radius = self.vision_range * BLOCK_SIZE
        pygame.draw.circle(SCREEN, LIGHT_RED, (int(self.x * BLOCK_SIZE + BLOCK_SIZE / 2), int(self.y * BLOCK_SIZE + BLOCK_SIZE / 2)), vision_radius, 1)
    
    def can_see_player(self, player, maze):
        if abs(self.x - player.x) <= self.vision_range and abs(self.y - player.y) <= self.vision_range:
            x0, y0 = int(self.x), int(self.y)
            x1, y1 = int(player.x), int(player.y)
            for x, y in bresenham(x0, y0, x1, y1):
                if maze[y][x] == 1:
                    return False
            return True
        return False

    def move_towards_player(self, player, maze):
        if self.can_see_player(player, maze):
            if self.x < player.x and maze[int(self.y)][int(self.x + 1)] == 0:
                self.x += 1
            elif self.x > player.x and maze[int(self.y)][int(self.x - 1)] == 0:
                self.x -= 1
            elif self.y < player.y and maze[int(self.y + 1)][int(self.x)] == 0:
                self.y += 1
            elif self.y > player.y and maze[int(self.y - 1)][int(self.x)] == 0:
                self.y -= 1

# Bresenham's line algorithm for line of sight
def bresenham(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points

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
        maze = [[0 if random.random() > 0.3 else 1 for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            maze[i][0] = maze[i][cols - 1] = 1
        for j in range(cols):
            maze[0][j] = maze[rows - 1][j] = 1
        maze[rows - 2][cols - 2] = 0  # Create exit

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

def main():
    clock = pygame.time.Clock()
    maze, search_steps, path = generate_maze(ROWS, COLS)
    game_over = False
    player = Player(1, 1)
    soldiers = [Soldier(random.randint(1, COLS-2), random.randint(1, ROWS-2)) for _ in range(5)]

    search_step_index = 0
    show_path = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
        
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1

        player.move(dx, dy, maze)

        for soldier in soldiers:
            soldier.move_towards_player(player, maze)
            if int(soldier.x) == int(player.x) and int(soldier.y) == int(player.y):
                print("Game Over!")
                game_over = True
        
        if int(player.x) == COLS - 2 and int(player.y) == ROWS - 2:
            print("You win!")
            game_over = True

        SCREEN.fill(WHITE)
        draw_maze(SCREEN, maze)
        player.draw(SCREEN)
        for soldier in soldiers:
            soldier.draw(SCREEN)
        
        if not show_path and search_step_index < len(search_steps):
            x, y = search_steps[search_step_index]
            pygame.draw.rect(SCREEN, YELLOW, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            search_step_index += 1
            pygame.display.flip()
            pygame.time.delay(10)  # Delay for visualization

        # Once A* search is complete, show the final path
        if search_step_index >= len(search_steps) and not show_path:
            show_path = True
            if path:
                for x, y in path:
                    pygame.draw.rect(SCREEN, YELLOW, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.display.flip()
                    pygame.time.delay(50)  # Delay to clearly show the path

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
