import pygame
import random

WIDTH, HEIGHT = 800, 600
ROWS, COLS = 30, 40
BLOCK_SIZE = WIDTH // COLS
FPS = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_RED = (255, 200, 200)

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

def generate_maze(rows, cols):
    maze = [[0 if random.random() > 0.2 else 1 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        maze[i][0] = maze[i][cols - 1] = 1
    for j in range(cols):
        maze[0][j] = maze[rows - 1][j] = 1
    maze[rows - 2][cols - 2] = 0  # Create exit
    return maze

def draw_maze(SCREEN, maze):
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            color = BLACK if tile else WHITE
            pygame.draw.rect(SCREEN, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    # Draw the exit
    pygame.draw.rect(SCREEN, BLUE, ((COLS - 2) * BLOCK_SIZE, (ROWS - 2) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def main():
    clock = pygame.time.Clock()
    maze = generate_maze(ROWS, COLS)
    game_over = False

    player = Player(1, 1)
    soldiers = [Soldier(random.randint(1, COLS-2), random.randint(1, ROWS-2)) for _ in range(5)]
    
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
        
        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
