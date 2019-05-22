import pygame
import random
import serial

USE_SERIAL = False
SERIAL_PORT = 'COM7'
SERIAL_BAUD = 115200

PLAYER_COUNT = 2
TILE_SIZE = 80
PLAYER_SIZE = 10
CELLS_PER_ROW = 10
ROWS_PER_COLUMN = 10

class Tile(pygame.sprite.Sprite):

    def __init__(self, x, y, colour):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect =  self.image.get_rect().move(x, y) 

        self.image.fill(colour)
        black = pygame.Color(0, 0, 0)
        image_rect = self.image.get_rect()
        pygame.draw.rect(self.image, black, image_rect, 1)

        self.index = 0

class PlayerPiece(pygame.sprite.Sprite):

    def __init__(self, index, colour):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(colour)
        self.tile_index = 0
        self.rect = self.image.get_rect()
        self.offset = (10, 10 + (PLAYER_SIZE + 5) * index)

    def set_position(self, tile):
        self.rect.topleft = tile.rect.move(self.offset).topleft

class Obstacle(pygame.sprite.Sprite):

    def __init__(self, entry_tile, exit_tile):
        pygame.sprite.Sprite.__init__(self)

        self.entry_index = entry_tile.index
        self.exit_index = exit_tile.index

        top = min(entry_tile.rect.top, exit_tile.rect.top)
        bottom = max(entry_tile.rect.bottom, exit_tile.rect.bottom)
        left = min(entry_tile.rect.left, exit_tile.rect.left)
        right = max(entry_tile.rect.right, exit_tile.rect.right)

        self.image = pygame.Surface((right - left, bottom - top), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        self.rect.topleft = (left, top)

        start_center = Ladder.calculate_relative_point(entry_tile.rect.center, self.rect.topleft)
        end_center = Ladder.calculate_relative_point(exit_tile.rect.center, self.rect.topleft)
        self.draw_obstacle(start_center, end_center)

    def calculate_relative_point(point, origin):
        return (point[0] - origin[0], point[1] - origin[1])

    def draw_obstacle(self, start_center, end_center):
        pass

class Ladder(Obstacle):

    def draw_obstacle(self, start_center, end_center):
        pygame.draw.line(self.image, pygame.Color(0, 255, 0), start_center, end_center, 5)
        pygame.draw.circle(self.image, pygame.Color(0, 255, 0), start_center, 10)
        pygame.draw.circle(self.image, pygame.Color(255, 0, 0), end_center, 10)

class Snake(Obstacle):

    def draw_obstacle(self, start_center, end_center):
        pygame.draw.line(self.image, pygame.Color(255, 0, 0), start_center, end_center, 5)
        pygame.draw.circle(self.image, pygame.Color(0, 255, 0), start_center, 10)
        pygame.draw.circle(self.image, pygame.Color(255, 0, 0), end_center, 10)

class MainGame():

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ROWS_PER_COLUMN * TILE_SIZE, CELLS_PER_ROW * TILE_SIZE))
        self.grid_cells = self.initialise_grid()
        self.players = self.initialise_players()
        self.obstacles = self.initialise_obstacles()
        if USE_SERIAL:
            self.serial = serial.Serial(SERIAL_PORT)
            self.serial.baudrate = SERIAL_BAUD
            self.controllers = [45, 46]

    def initialise_grid(self):
        colors = [pygame.Color(255, 200, 200), pygame.Color(200, 255, 200), pygame.Color(200, 200, 255)]
        group = []
        color_index = 0
        for row in range(0, ROWS_PER_COLUMN):
            for column in range(0, CELLS_PER_ROW):
                group.append(Tile(column * TILE_SIZE, row * TILE_SIZE, colors[color_index % len(colors)]))
                color_index += 1
        ordered_group = []
        current_index = 0
        for row in range(ROWS_PER_COLUMN - 1, -1, -1):
            rng = range(0, CELLS_PER_ROW)
            if row % 2 == 0:
                rng = reversed(rng)
            for column in rng:
                this_tile = group[row * CELLS_PER_ROW + column]
                this_tile.index = current_index
                ordered_group.append(this_tile)
                current_index += 1

        return ordered_group

    def initialise_players(self):
        group = []
        colors = [pygame.Color(128, 128, 128), pygame.Color(0, 128, 128), pygame.Color(128, 0, 128), pygame.Color(128, 128, 0)]
        for i in range(PLAYER_COUNT):
            player = PlayerPiece(i, colors[i % len(colors)])
            player.tile_index = 0
            player.set_position(self.grid_cells[0])
            group.append(player)
        return group

    def initialise_obstacles(self):
        obstacles = []
        obstacles.append(Ladder(self.grid_cells[3], self.grid_cells[25]))
        obstacles.append(Ladder(self.grid_cells[14], self.grid_cells[43]))
        obstacles.append(Ladder(self.grid_cells[34], self.grid_cells[72]))
        obstacles.append(Ladder(self.grid_cells[66], self.grid_cells[96]))
        obstacles.append(Snake(self.grid_cells[30], self.grid_cells[6]))
        obstacles.append(Snake(self.grid_cells[61], self.grid_cells[19]))
        obstacles.append(Snake(self.grid_cells[87], self.grid_cells[51]))
        obstacles.append(Snake(self.grid_cells[91], self.grid_cells[78]))
        return obstacles

    def move_player_steps(self, player, steps):
        player.tile_index += steps
        player.set_position(self.grid_cells[player.tile_index])

    def start_game(self):
        grid_cell_sprites = pygame.sprite.Group(self.grid_cells)
        player_sprites = pygame.sprite.Group(self.players)
        obstacle_sprites = pygame.sprite.Group(self.obstacles)

        seq = 0
        while True:
            grid_cell_sprites.draw(self.screen)
            player_sprites.draw(self.screen)
            obstacle_sprites.draw(self.screen)
            pygame.display.flip()

            player_index = seq % len(self.players)
            current_player = self.players[player_index]

            if USE_SERIAL:
                id = -1
                while id != self.controllers[player_index]:
                    res = self.serial.read(3)
                    id = int(res[0])
                    turn = int(res[1])
                    roll = int(res[2])
            else:
                pygame.time.wait(1000)
                roll = player_index + 1

            self.move_player_steps(current_player, roll)
            for o in self.obstacles:
                if current_player.tile_index == o.entry_index:
                    current_player.tile_index = o.exit_index
                    self.move_player_steps(current_player, 0)

            seq += 1

if __name__ == "__main__":
    game = MainGame()
    game.start_game()