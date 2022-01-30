import math
from os import remove
from turtle import color, position
import pygame
import random

pygame.font.init()

s_width = 800
s_height = 700
play_width = 210  
play_height = 300  
circle_size = 3

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

O = [['.....',
      '.....',
      '..0..',
      '.....',
      '.....']]

shapes = [O]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]

class Piece(object):
    rows = 10 
    columns = 7 
    score = 0

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[random.randrange(0, len(shape_colors))]
        self.rotation = 0 

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions

def valid_space(shape, grid):
    accepted_positions = [[(j, i) for j in range(7) if grid[i][j] == (0,0,0)] for i in range(10)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True

def get_shape():
    global shapes, shape_colors

    return Piece(5, 0, random.choice(shapes))

def draw_text_top (text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), play_height/4 - label.get_height()/2))

def draw_text_middle(text, size,color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), play_height/2 - label.get_height()/2))

def draw_text_bottom(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y - label.get_height()/2))

def break_list_consecutive_numbers(lst):
    result = []
    for item in lst:
        if not result or item - result[-1][-1] != 1:
            result.append([item])                  
        else:
            result[-1].append(item)           
    return result    

def consecutive_numbers(lst):
    if len(lst) < 3:
        return False
    result = break_list_consecutive_numbers(lst)
    print(result)
    return True

def clear_columns(grid, locked):
    removed=[]
    columns_affected = []
    result = []
    columns = []
    column = 0
    column_idx = 0
    max_rows = len(grid)
    max_column = len(grid[0])
    for y in range(max_column):
        columns.append(y)
        columns[y] = []
        for x in range(max_rows):
            columns[y].append(grid[x][y])
    for i, col in enumerate(columns):
        for color in shape_colors:
            result = [i for i, x in enumerate(col) if x == color]
            consecutive_results = break_list_consecutive_numbers(result)
            for res in consecutive_results:
                if len(res) >= 3:
                    try:
                        for pos in res:
                            removed.append(pos)
                            if col not in columns_affected:
                                columns_affected.append(col)
                            del locked[(i, pos)]
                    except:
                        continue
    if len(removed) > 0:
        return True
    return False

def clear_rows(grid, locked):
    inc = 0
    removed = []
    ind = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        for color in shape_colors:
            result = [i for i, x in enumerate(row) if x == color]
            consecutive_results = break_list_consecutive_numbers(result)
            for res in consecutive_results:
                if len(res) >= 3:
                    try:
                        for pos in res:
                            removed.append(pos)
                            ind = i
                            del locked[(pos, i)]
                    except:
                        continue

    if len(removed) > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if x in removed and y < ind:
                newKey = (x, y + 1)
                locked[newKey] = locked.pop(key)
        return True
    return False

def create_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(7)] for x in range(10)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid

def draw_window(surface):
    surface.fill((0,0,0))
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Colortris', 1, (255,255,255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))
    
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.circle(surface, grid[i][j], (top_left_x + j* 30 + 14, top_left_y + i * 30 + 14), 14)
            pygame.draw.circle(surface, (0,0,0), (top_left_x + j* 30 + 14, top_left_y + i * 30 + 14), 10)

    (surface, 7, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False
   
def main():
    global grid

    locked_positions = {} 
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0

    while run:
        fall_speed = 0.27

        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            while clear_rows(grid, locked_positions):
                grid = create_grid(locked_positions)
            while clear_columns(grid, locked_positions):
                grid = create_grid(locked_positions)

        draw_window(win)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    draw_text_bottom("Game Over", 40, (255,255,255), win)
    pygame.display.update()
    pygame.time.delay(2000)

def main_menu():
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_top ('Colortris', 80, (255,255,255), win)
        draw_text_middle('Made by Diogo Soares and Tomás Vaz', 20, (255,255,255), win)
        draw_text_bottom('Press any key to begin.', 30, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Colortris')

main_menu() 