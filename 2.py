import pygame
import sys
import heapq

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800 
GRID_COLOR = (200, 200, 200)
WALL_COLOR = (0, 0, 0)
PATH_COLOR = (0, 0, 255)
START_COLOR = (0, 255, 0)
END_COLOR = (255, 0, 0) 
BACKGROUND_COLOR = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)

class Node():
    def __init__(self, state, parent, action, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class PriorityFrontier():
    def __init__(self):
        self.frontier = []
        self.counter = 0  

    def add(self, node):
        heapq.heappush(self.frontier, (node.cost + node.heuristic, self.counter, node))
        self.counter += 1

    def contains_state(self, state):
        return any(node.state == state for _, _, node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            return heapq.heappop(self.frontier)[2]

class Maze:
    def __init__(self, filename):
        self.grid = self.load_maze(filename)
        self.start = self.find_position('A')
        self.end = self.find_position('B')
        self.width = len(self.grid[0])
        self.height = len(self.grid)

    def load_maze(self, filename):
        with open(filename, 'r') as f:
            return [list(line.strip()) for line in f]

    def find_position(self, char):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == char:
                    return (x, y)
        return None

    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and self.grid[y][x] != '#'

    def neighbors(self, state):
        x, y = state
        candidates = [
            ("up", (x, y - 1)),
            ("down", (x, y + 1)),
            ("left", (x - 1, y)),
            ("right", (x + 1, y))
        ]
        return [(action, (x, y)) for action, (x, y) in candidates if self.is_valid(x, y)]

    def heuristic(self, state):
        x1, y1 = state
        x2, y2 = self.end
        return abs(x1 - x2) + abs(y1 - y2)

    def solve(self, algorithm):
        start = Node(state=self.start, parent=None, action=None, cost=0, heuristic=self.heuristic(self.start))
        
        if algorithm == 'bfs':
            frontier = QueueFrontier()
        elif algorithm == 'dfs':
            frontier = StackFrontier()
        elif algorithm in ['greedy', 'astar']:
            frontier = PriorityFrontier()
        else:
            raise ValueError("Algoritmo no válido")
        
        frontier.add(start)
        explored = set()

        while not frontier.empty():
            node = frontier.remove()

            if node.state == self.end:
                cells = []
                while node.parent is not None:
                    cells.append(node.state)
                    node = node.parent
                cells.reverse()
                return cells

            explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if state not in explored and not frontier.contains_state(state):
                    cost = node.cost + 1
                    if algorithm == 'greedy':
                        heuristic = self.heuristic(state)
                        child = Node(state=state, parent=node, action=action, cost=0, heuristic=heuristic)
                    elif algorithm == 'astar':
                        heuristic = self.heuristic(state)
                        child = Node(state=state, parent=node, action=action, cost=cost, heuristic=heuristic)
                    else:
                        child = Node(state=state, parent=node, action=action, cost=cost, heuristic=0)
                    frontier.add(child)

        return None

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class MazeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Solver")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.state = 'menu'
        self.maze = None
        self.solution = None
        self.current_step = 0
        self.setup_menu()
        self.setup_algorithm_buttons()

    def setup_menu(self):
        button_width, button_height = 200, 50
        x = (SCREEN_WIDTH - button_width) // 2
        self.easy_button = Button(x, 200, button_width, button_height, "Fácil", BUTTON_COLOR, BUTTON_TEXT_COLOR)
        self.medium_button = Button(x, 300, button_width, button_height, "Medio", BUTTON_COLOR, BUTTON_TEXT_COLOR)
        self.hard_button = Button(x, 400, button_width, button_height, "Difícil", BUTTON_COLOR, BUTTON_TEXT_COLOR)

    def setup_algorithm_buttons(self):
        button_width, button_height = 100, 50
        self.bfs_button = Button(SCREEN_WIDTH - 120, 50, button_width, button_height, "BFS", BUTTON_COLOR, BUTTON_TEXT_COLOR)
        self.dfs_button = Button(SCREEN_WIDTH - 120, 120, button_width, button_height, "DFS", BUTTON_COLOR, BUTTON_TEXT_COLOR)
        self.greedy_button = Button(SCREEN_WIDTH - 120, 190, button_width, button_height, "Greedy", BUTTON_COLOR, BUTTON_TEXT_COLOR)
        self.astar_button = Button(SCREEN_WIDTH - 120, 260, button_width, button_height, "A*", BUTTON_COLOR, BUTTON_TEXT_COLOR)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == 'menu':
                    self.handle_menu_click(event.pos)
                elif self.state == 'solving':
                    self.handle_solving_click(event.pos)
        return True

    def handle_menu_click(self, pos):
        if self.easy_button.is_clicked(pos):
            self.start_game("lab1.txt")
        elif self.medium_button.is_clicked(pos):
            self.start_game("lab3.txt")
        elif self.hard_button.is_clicked(pos):
            self.start_game("lab5.txt")

    def handle_solving_click(self, pos):
        if self.bfs_button.is_clicked(pos):
            self.solution = self.maze.solve('bfs')
        elif self.dfs_button.is_clicked(pos):
            self.solution = self.maze.solve('dfs')
        elif self.greedy_button.is_clicked(pos):
            self.solution = self.maze.solve('greedy')
        elif self.astar_button.is_clicked(pos):
            self.solution = self.maze.solve('astar')
        else:
            self.state = 'menu'
            self.maze = None
            self.solution = None
        self.current_step = 0

    def start_game(self, filename):
        try:
            self.maze = Maze(filename)
            self.solution = None
            self.current_step = 0
            self.state = 'solving'
            self.calculate_cell_size()
        except Exception as e:
            print(f"Error al cargar el laberinto: {str(e)}")

    def calculate_cell_size(self):
        max_width = SCREEN_WIDTH - 200  
        max_height = SCREEN_HEIGHT - 100  
        self.cell_size = min(max_width // self.maze.width, max_height // self.maze.height)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'solving':
            self.draw_maze()
            self.bfs_button.draw(self.screen)
            self.dfs_button.draw(self.screen)
            self.greedy_button.draw(self.screen)
            self.astar_button.draw(self.screen)
        pygame.display.flip()

    def draw_menu(self):
        title = self.font.render("Elige el Nivel", True, (0, 0, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        self.easy_button.draw(self.screen)
        self.medium_button.draw(self.screen)
        self.hard_button.draw(self.screen)

    def draw_maze(self):
        if not self.maze:
            return
        
        offset_x = (SCREEN_WIDTH - self.maze.width * self.cell_size) // 2 - 50
        offset_y = (SCREEN_HEIGHT - self.maze.height * self.cell_size) // 2

        for y, row in enumerate(self.maze.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(offset_x + x * self.cell_size, offset_y + y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
                if cell == '#':
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                elif (x, y) == self.maze.start:
                    pygame.draw.rect(self.screen, START_COLOR, rect)
                elif (x, y) == self.maze.end:
                    pygame.draw.rect(self.screen, END_COLOR, rect)

        if self.solution:
            for i, (x, y) in enumerate(self.solution[:self.current_step+1]):
                rect = pygame.Rect(offset_x + x * self.cell_size, offset_y + y * self.cell_size, self.cell_size, self.cell_size)
                color = pygame.Color('blue')
                color.hsva = (240 * i / len(self.solution), 100, 100, 100)
                pygame.draw.rect(self.screen, color, rect)

            if self.current_step < len(self.solution) - 1:
                self.current_step += 1
            else:
                text = self.font.render("Presiona para volver al menú", True, (0, 0, 0))
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
                self.screen.blit(text, text_rect)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)  #limitar a 10 FPS para una animacion mas lenta
        pygame.quit()

if __name__ == "__main__":
    game = MazeGame()
    game.run()