import random

import pygame as pg
import sys
from pygame.locals import KEYDOWN, K_q

SCREENSIZE = WIDTH_SCR, HEIGHT_SCR = 1200, 800
GAME_AREA_MULTIPLE = 0.9
LABYRINTH_MULTIPLE = 0.98
GRID_SIZE = [30, 30]
GAME_AREA_BORDER_THICKNESS = 1
CELL_BORDER_THICKNESS = 2
player_speed = 75 / max(GRID_SIZE)
clock = pg.time.Clock()

COLORS = {
    'screen_color': (0, 0, 0),
    'player_color': (255, 200, 0),
    'center_point_color': (255, 99, 71),
    'exit_color': (255, 105, 180),
}

walls = []
center_points = []
tracking_points = []


def get_max_horizontal_coordinate():
    horizontal_points_coordinate = []
    for point in center_points:
        horizontal_points_coordinate.append(point.rect.center[0])
    return max(horizontal_points_coordinate)


class CenterPoints(object):

    def __init__(self, pos):
        center_points.append(self)
        self.rect = pg.Rect(pos[0], pos[1], 1, 1)


class Wall(object):

    def __init__(self, pos, width, height):
        walls.append(self)
        self.rect = pg.Rect(pos[0], pos[1], width, height)

    def kill(self):
        walls.remove(self)


class Exit(object):

    def __init__(self, pos, width, height):
        walls.append(self)
        self.rect = pg.Rect(pos[0], pos[1], width, height)


class Player(object):

    def __init__(self, start_coordinates, size):
        self.rect = pg.Rect(start_coordinates[0], start_coordinates[1], size, size)

    def move(self, dx, dy):
        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0:
            tracking_points.append(self)
            self.move_single_axis(dx, 0)
        if dy != 0:
            tracking_points.append(self)
            self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):

        # Move the rect
        self.rect.x += dx
        self.rect.y += dy

        # If you collide with a wall, move out based on velocity
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0:  # Moving right; Hit the left side of the wall
                    self.rect.right = wall.rect.left
                if dx < 0:  # Moving left; Hit the right side of the wall
                    self.rect.left = wall.rect.right
                if dy > 0:  # Moving down; Hit the top side of the wall
                    self.rect.bottom = wall.rect.top
                if dy < 0:  # Moving up; Hit the bottom side of the wall
                    self.rect.top = wall.rect.bottom


class Labyrinth:

    def __init__(self, area_width, area_height, grid_size):
        self.width = area_width
        self.height = area_height
        self.self_grid_size = self.grid_size_horizontal, self.grid_size_vertical = grid_size[0], grid_size[1]
        self.padding_horizontal = self.width - (self.width * LABYRINTH_MULTIPLE)
        self.padding_vertical = self.height - (self.height * LABYRINTH_MULTIPLE)
        self.cell_width_size = (self.width - (self.padding_horizontal * 2)) / self.grid_size_horizontal
        self.cell_height_size = (self.height - (self.padding_vertical * 2)) / self.grid_size_vertical
        self.cell_border_thickness = CELL_BORDER_THICKNESS
        self.end_rect = None

    def set_center_points(self, start_width, start_height):
        points_center = []
        start_width += self.padding_horizontal
        start_height += self.padding_vertical
        #  TODO rename start_width_y and start_height_x
        start_height_x = start_height

        for _ in range(self.grid_size_vertical):
            vertical_coordinate = start_height_x + self.cell_height_size / 2
            start_height_x += self.cell_height_size
            start_width_y = start_width
            for _ in range(self.grid_size_horizontal):
                horizontal_coordinate = start_width_y + self.cell_width_size / 2
                points_center.append([horizontal_coordinate, vertical_coordinate])
                start_width_y += self.cell_width_size
        return points_center

    def create_grid_coordinates(self, start_width, start_height):
        coordinates = {
            'vertical_line': [],
            'horizontal_line': [],
        }

        start_width += self.padding_horizontal
        start_height += self.padding_vertical
        #  TODO rename start_width_y and start_height_x
        start_width_y = start_width
        start_height_x = start_height
        #  TODO rename y
        for _ in range(self.grid_size_horizontal):
            for y in range(self.grid_size_vertical + 1):
                coordinate_y = int(y * self.cell_height_size)
                coordinates['vertical_line'].append(
                    {
                        'point': [int(start_width_y), int(start_height + coordinate_y)],
                        'width': [int(self.cell_width_size)]
                    }
                )
            start_width_y += self.cell_width_size
        #  TODO rename x
        for _ in range(self.grid_size_vertical):
            for x in range(self.grid_size_horizontal + 1):
                coordinate_x = int(x * self.cell_width_size)
                coordinates['horizontal_line'].append(
                    {
                        'point': [int(start_width + coordinate_x), int(start_height_x)],
                        'height': [int(self.cell_height_size)]
                    }
                )
            start_height_x += self.cell_height_size

        return coordinates

    def set_end_rect(self, points):
        points_length = len(points)
        list_of_possible_end_rect = points[
                                    int(points_length - self.grid_size_horizontal):
                                    points_length - int(self.grid_size_horizontal / 2)]
        return random.choice(list_of_possible_end_rect)


def check_events():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_q:
            pg.quit()
            sys.exit()


def check_move_events(key, player, end_rect):
    if key[pg.K_LEFT]:
        player.move(-player_speed, 0)
    if key[pg.K_RIGHT]:
        player.move(player_speed, 0)
    if key[pg.K_UP]:
        player.move(0, -player_speed)
    if key[pg.K_DOWN]:
        player.move(0, player_speed)

    if player.rect.colliderect(end_rect):
        pg.quit()
        sys.exit()


def set_game_area(screen):
    width_game_area = screen.get_width() * GAME_AREA_MULTIPLE
    height_game_area = screen.get_height() * GAME_AREA_MULTIPLE
    padding_width_area = (screen.get_width() - width_game_area) / 2
    padding_height_area = (screen.get_height() - height_game_area) / 2
    return padding_width_area, padding_height_area, width_game_area, height_game_area


def list_of_lengths_chunks(list_to_chunk, numbers_of_chunks):
    length_of_list = len(list_to_chunk)
    if numbers_of_chunks <= 1:
        return [length_of_list]
    elif numbers_of_chunks >= length_of_list:
        return [1] * length_of_list
    else:
        list_of_chunks_length = []
        max_partition_length = length_of_list - (numbers_of_chunks - 1)
        for _ in range(numbers_of_chunks):
            if _ != numbers_of_chunks - 1:
                list_of_chunks_length.append(random.randint(1, max_partition_length))
                max_partition_length = (length_of_list - sum(list_of_chunks_length)) - (numbers_of_chunks - _ - 2)
            else:
                list_of_chunks_length.append(length_of_list - sum(list_of_chunks_length))
    return list_of_chunks_length


def make_list_of_chunks(list_to_chunk, numbers_of_chunks):
    result = []
    list_to_chunk_new = list_to_chunk.copy()
    lengths_list = list_of_lengths_chunks(list_to_chunk, numbers_of_chunks)
    random.shuffle(lengths_list)
    for count, value in enumerate(lengths_list):
        result.append([])
        for _ in range(value):
            pop_element = list_to_chunk_new.pop(0)
            result[count].append(pop_element)
    return result


def main():
    pg.init()
    screen = pg.display.set_mode(SCREENSIZE)
    game_area = pg.Rect(set_game_area(screen))
    labyrinth = Labyrinth(game_area.width, game_area.height, GRID_SIZE)
    coordinates_for_center = labyrinth.set_center_points(game_area.topleft[0], game_area.topleft[1])
    coordinates_for_walls = labyrinth.create_grid_coordinates(game_area.topleft[0], game_area.topleft[1])
    border_thickness = labyrinth.cell_border_thickness

    for point in coordinates_for_walls['vertical_line']:
        Wall(point['point'], point['width'][0], border_thickness)

    for point in coordinates_for_walls['horizontal_line']:
        Wall(point['point'], border_thickness, point['height'][0])

    for point in coordinates_for_center:
        CenterPoints(point)

    #  TODO refactor Player
    size_of_player = min([labyrinth.cell_width_size, labyrinth.cell_height_size]) / 2
    start_player_coordinates = [
        coordinates_for_center[0][0] - (size_of_player / 2),
        coordinates_for_center[0][1] - (size_of_player / 2)
    ]
    player = Player(start_player_coordinates,
                    size_of_player)
    end = labyrinth.set_end_rect(center_points).rect.inflate(size_of_player, size_of_player)

    # start labyrinth
    rect_union = []

    for vertical in range(labyrinth.grid_size_vertical):
        rect_union.append([])
        for horizontal in range(vertical * labyrinth.grid_size_horizontal,
                                labyrinth.grid_size_horizontal + (vertical * labyrinth.grid_size_horizontal)):
            rect_union[vertical].append(center_points[horizontal].rect)

    for rect_count, rect_value in enumerate(rect_union):
        if rect_count == 0:
            rect_union_new = pg.Rect.unionall(rect_value[0], rect_value)
            pg.draw.rect(screen, pg.Color('blanchedalmond'), rect_union_new, 6)
            some_thing = rect_union_new.collidelistall(walls)
            for index in reversed(some_thing):
                walls[index].kill()
        else:
            #  TODO rename ALL, this is terrible
            chunks_list = make_list_of_chunks(rect_value, random.randint(1, labyrinth.grid_size_horizontal))
            for chunk_count, chunks_value in enumerate(chunks_list):
                rect_union_new = pg.Rect.unionall(chunks_value[0], chunks_value)
                points_collidelistall = rect_union_new.collidelistall(center_points)
                flip_coin = random.randint(0, 1)
                if flip_coin == 0:
                    random_point = random.choice(points_collidelistall)
                    random_point_in_rect = center_points[random_point].rect
                    random_point_on_top = center_points[random_point - labyrinth.grid_size_horizontal].rect
                    rect_up = pg.Rect.union(random_point_in_rect, random_point_on_top)
                    collidelistall_with_up = rect_up.collidelistall(walls)
                    for index in reversed(collidelistall_with_up):
                        walls[index].kill()
                else:
                    # TODO refactor if/else
                    last_point = points_collidelistall[-1]
                    if center_points[last_point].rect.center[0] == get_max_horizontal_coordinate():
                        random_point = random.choice(points_collidelistall)
                        random_point_in_rect = center_points[random_point].rect
                        random_point_on_top = center_points[random_point - labyrinth.grid_size_horizontal].rect
                        rect_up = pg.Rect.union(random_point_in_rect, random_point_on_top)
                        collidelistall_with_up = rect_up.collidelistall(walls)
                        for index in reversed(collidelistall_with_up):
                            walls[index].kill()
                    else:
                        random_point_in_rect = center_points[last_point].rect
                        random_point_on_top = center_points[last_point + 1].rect
                        rect_up = pg.Rect.union(random_point_in_rect, random_point_on_top)
                        collidelistall_with_up = rect_up.collidelistall(walls)
                        for index in reversed(collidelistall_with_up):
                            walls[index].kill()
                some_thing = rect_union_new.collidelistall(walls)
                for index in reversed(some_thing):
                    walls[index].kill()

        # labyrinth formation disappears

    while True:
        clock.tick(100)
        check_events()
        key = pg.key.get_pressed()
        check_move_events(key, player, end)

        game_area_color = pg.Color('aquamarine2')
        lines_color = pg.Color('azure')
        screen.fill(COLORS['screen_color'])

        for wall in walls:
            pg.draw.rect(screen, lines_color, wall.rect)

        # for center_point in center_points:
        #     pg.draw.rect(screen, COLORS['center_point_color'], center_point.rect)

        pg.draw.rect(screen, game_area_color, game_area, GAME_AREA_BORDER_THICKNESS)
        pg.draw.rect(screen, COLORS['player_color'], player.rect)
        pg.draw.rect(screen, COLORS['exit_color'], end)
        for track in tracking_points:
            pg.draw.rect(screen, COLORS['center_point_color'], track)
        pg.display.flip()
        clock.tick(360)


if __name__ == '__main__':
    main()
