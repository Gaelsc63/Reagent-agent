import pygame as pg
import sys
import random as rdm
import math as mt
from collections import deque

# Dimensiones de la ventana y crear
width = 1000
height = 700
square = 10
window = pg.display.set_mode((width, height))
pg.display.set_caption('Agente reactivo')

# Color de fondo (RGB)
backColor = (255, 255, 255)  
lineColor = (0, 0, 0)

width_cell = width//square
height_cell = height//square    

forbidden_zone = set((x, y) for x in range(2) for y in range(2))    

X_spaceship = 0
Y_spaceship = 0
S0 = 1

X_base = 10
Y_base = 10

def cuadricula(window):
    for x in range(0, width, width_cell):
        pg.draw.line(window, lineColor, (x, 0), (x, height))

    for y in range(0, height, height_cell):
        pg.draw.line(window, lineColor, (0, y), (width, y))

def generate_obstacles(num_obstacles, width_cells, height_cells):
    obstacles = set()
    while len(obstacles) < num_obstacles:
        x = rdm.randint(0, width_cells - 1)
        y = rdm.randint(0, height_cells - 1)
        if (x, y) != (width_cells // 2, height_cells // 2) and (x, y) not in forbidden_zone:
            obstacles.add((x, y))
    return obstacles

def generate_objects(num_objects, width_cells, height_cells, obstacles, agent_position):
    objects = set()
    while len(objects) < num_objects:
        x = rdm.randint(0, width_cells - 1)
        y = rdm.randint(0, height_cells - 1)
        
        if(x, y) not in obstacles and (x, y) != agent_position and (x, y) not in forbidden_zone:
            objects.add((x, y))
    return objects

#Cargar imagenes 
def load_images():
    agent_image = pg.image.load('images/towelie.webp')
    obstacle_image = pg.image.load('images/policeman.png')
    object_image = pg.image.load('images/porro.png')
    background_image = pg.image.load('images/background.jpeg')
    casabonita_image = pg.image.load('images/casabonita.webp')

    agent_image = pg.transform.scale(agent_image, (width_cell // 1.2, height_cell // 0.9))
    obstacle_image = pg.transform.scale(obstacle_image, (width_cell // 0.8, height_cell // 0.8))
    object_image = pg.transform.scale(object_image, (width_cell // 1.5, height_cell // 1.5))
    background_image = pg.transform.scale(background_image, (width, height))
    casabonita_image = pg.transform.scale(casabonita_image, (width_cell // 0.5, height_cell // 0.5))

    return agent_image, obstacle_image, object_image, background_image, casabonita_image

pg.init()
pg.font.init()

agent_image, obstacle_image, object_image, background_image, casabonita_image = load_images()

def bfs(start, goal, obstacles):
    queue = deque([(start, [])])
    visited = set()
    visited.add(start)

    while queue:
        (current, path) = queue.popleft()
        if current == goal:
            return path

        for direction in ['north', 'south', 'east', 'west']:
            next_x, next_y = current
            if direction == 'north':
                next_y -= 1
            elif direction == 'south':
                next_y += 1
            elif direction == 'east':
                next_x += 1
            elif direction == 'west':
                next_x -= 1

            if (0 <= next_x < width // width_cell and 0 <= next_y < height // height_cell and 
                (next_x, next_y) not in obstacles and 
                (next_x, next_y) not in visited):
                visited.add((next_x, next_y))
                queue.append(((next_x, next_y), path + [direction]))

    return []

class object:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False

    def is_at_position(self, x, y):
        return self.x == x and self.y == y

import random as rdm

class agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = agent_image
        self.direction = self.random_direction()
        self.carrying_objects = False
        self.stuck_counter = 0  # Contador para rastrear cuántas veces el agente está estancado

    def random_direction(self):
        return rdm.choice(['north', 'south', 'east', 'west'])
    
    def drop_objects(self):
        if self.carrying_objects:
            self.carrying_objects = False
            return True  # Indica que se ha dejado un objeto
        return False

    def pickup_objects(self, objects):
        for obj in list(objects):
            if (self.x, self.y) == obj:
                self.carrying_objects = True
                objects.remove(obj)
                break

    def get_direction_base(self, spaceship_position):
        if self.x < spaceship_position[0]:
            return 'east'
        elif self.x > spaceship_position[0]:
            return 'west'
        elif self.y < spaceship_position[1]:
            return 'south'
        elif self.y > spaceship_position[1]:
            return 'north'
        return self.random_direction()

    def detect_objects(self, objects):
        adjacent_positions = {
            'north': (self.x, self.y - 1),
            'south': (self.x, self.y + 1),
            'east': (self.x + 1, self.y),
            'west': (self.x - 1, self.y)
        }
        for direction, position in adjacent_positions.items():
            if position in objects:
                return direction
        return None
    
    def move(self, obstacles, objects, spaceship_position):
        if self.carrying_objects and (self.x, self.y) == spaceship_position:
            if self.drop_objects():
                return True  # Indica que el contador de objetos debe aumentar

        if self.carrying_objects:
            path = bfs((self.x, self.y), spaceship_position, obstacles)
            if path:
                self.direction = path[0]
            else:
                self.direction = self.random_direction() 
        else:
            object_direction = self.detect_objects(objects)
            if object_direction:
                self.direction = object_direction
            else:
                self.direction = self.random_direction()

        next_x, next_y = self.x, self.y
        if self.direction == 'north':
            next_y -= 1
        elif self.direction == 'south':
            next_y += 1
        elif self.direction == 'east':
            next_x += 1
        elif self.direction == 'west':
            next_x -= 1

        if (next_x, next_y) not in obstacles and (next_x, next_y) not in forbidden_zone:
            self.x, self.y = next_x, next_y
            self.stuck_counter = 0
        else:
            self.stuck_counter += 1
            if self.stuck_counter > 10:  
                self.direction = self.random_direction()

        self.x = max(0, min(self.x, width // width_cell - 1))
        self.y = max(0, min(self.y, height // height_cell - 1))

        if (self.x, self.y) in objects:
            self.pickup_objects(objects)

        if self.carrying_objects and (self.x, self.y) == spaceship_position:
            if self.drop_objects():
                return True  # Indica que el contador de objetos debe aumentar

        return False

    def get_direction_base(self, spaceship_position):
        if self.x < spaceship_position[0]:
            return 'east'
        elif self.x > spaceship_position[0]:
             return 'west'
        elif self.y < spaceship_position[1]:
            return 'south'
        elif self.y > spaceship_position[1]:
            return 'north'
        return self.random_direction()


    def is_at_edge(self):
        if self.x == 0 or self.x == (width // width_cell - 1) or self.y == 0 or self.y == (height // height_cell - 1):
            return True
        return False
    
    def calcular_gradiente(self):
        distancia = mt.sqrt((self.x - X_spaceship)**2 + (self.y - Y_spaceship)**2)

        if distancia == 0:
            return S0 
        else:
            return S0 / distancia
    
    def draw(self, window):
        window.blit(self.image, (self.x * width_cell, self.y * height_cell))

class game:
    def __init__(self):
        num_obstacles = rdm.randint(10, 15)
        num_objects = rdm.randint(8, 12)
        self.obstacles = generate_obstacles(num_obstacles, width // width_cell, height // height_cell)
        while True:
             agent_position = (width // (2 * width_cell), height // (2 * height_cell))
             if agent_position not in self.obstacles:
                 break
             
        self.objects = generate_objects(num_objects, width // width_cell, height // height_cell, self.obstacles, agent_position)
        self.Agent = agent(agent_position[0], agent_position[1])
        self.spaceship_position = agent_position 
        self.objects_collected = 0

    def draw(self, window): 
        window.blit(background_image, (0, 0))
        self.draw_obstacles(window)
        self.draw_spaceship(window)
        self.draw_objects(window)
        self.Agent.draw(window)
    
    def draw_spaceship(self, window):
        window.blit(casabonita_image, (self.spaceship_position[0] * width_cell, self.spaceship_position[1] * height_cell))

    def draw_obstacles(self, window):
        for obstacle in self.obstacles:
            window.blit(obstacle_image, (obstacle[0] * width_cell, obstacle[1] * height_cell))
    
    def draw_objects(self, window):
        for obj in self.objects:
            window.blit(object_image, (obj[0] * width_cell, obj[1] * height_cell))
    
    def move_agent(self):
        if self.Agent.move(self.obstacles, self.objects, self.spaceship_position):
            self.objects_collected += 1  # Incrementar el contador solo si el agente dejó un objeto en la nave

    def show_object_counter(self, window):
        font = pg.font.SysFont('Arial', 40)
        text = font.render(f"Porros recolectados: {self.objects_collected}", True, (0, 0, 0))
        window.blit(text, (10, 10))
    
    def show_gradient(self, window):
        gradient = self.Agent.calcular_gradiente()
        font = pg.font.SysFont('Arial', 40)
        text = font.render(f'Gradient: {gradient:.2f}', True, (0, 0, 0))
        window.blit(text, (10, 50))

def show_start_screen(window):
    font = pg.font.SysFont(None, 55)
    window.fill(backColor)
    text_lines = ["Presiona ENTER",
                  "para que Towelie empiece a recolectar porros"
    ]

    y_offset = height // 2
    for i, line  in enumerate(text_lines):
        text = font.render(line, True, (0, 0, 0))
        text_rect = text.get_rect(center=(width // 2, y_offset + i *60))
        window.blit(text, text_rect)

    pg.display.flip()

def main():
    pg.init()
    global window, backColor, width, width_cell, height, height_cell, X_base, Y_base, X_spaceship, Y_spaceship, obstacles, forbidden_zone
    game_instance = game()

    # Mostrar pantalla de inicio
    show_start_screen(window)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    game_loop(game_instance)

def game_loop(game_instance):
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        
        game_instance.move_agent()

        window.fill(backColor)
        
        cuadricula(window)
        game_instance.draw(window)

        game_instance.show_gradient (window)
        game_instance.show_object_counter(window)

        pg.display.flip()

        # Controlar la velocidad de fotogramas
        clock.tick(5)  # Ajusta la velocidad según sea necesario

if __name__ == "__main__":
    main()
