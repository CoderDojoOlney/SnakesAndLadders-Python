import pygame

class Tile(pygame.sprite.Sprite):

    TILE_SIZE = 80

    def __init__(self, x, y, colour):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((Tile.TILE_SIZE, Tile.TILE_SIZE))
        self.image.fill(colour)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class PlayerPiece(pygame.sprite.Sprite):

    PIECE_SIZE = 20

    def __init__(self, colour):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((PlayerPiece.PIECE_SIZE, PlayerPiece.PIECE_SIZE))
        self.image.fill(colour)
        self.tile_index = 0
        self.rect = self.image.get_rect()

    def set_position(self, tile):
        self.rect.topleft = tile.rect.move(10, 10).topleft

class MainGame():

    CELLS_PER_ROW = 10
    CELLS_PER_COLUMN = 10

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((MainGame.CELLS_PER_COLUMN * Tile.TILE_SIZE, MainGame.CELLS_PER_ROW * Tile.TILE_SIZE))
        self.grid_cells = self.initialise_grid()
        self.players = self.initialise_players()
        for player in self.players:
            player.tile_index = 0
            player.set_position(self.grid_cells[0])

    def initialise_grid(self):
        colors = [pygame.Color(255, 0, 0), pygame.Color(0, 255, 0), pygame.Color(0, 0, 255)]
        group = []
        color_index = 0
        for y in range(0, Tile.TILE_SIZE * MainGame.CELLS_PER_ROW, Tile.TILE_SIZE):
            for x in range(0, Tile.TILE_SIZE * MainGame.CELLS_PER_COLUMN, Tile.TILE_SIZE):
                group.append(Tile(x, y, colors[color_index % len(colors)]))
                color_index += 1
        ordered_group = []
        for y in range(MainGame.CELLS_PER_ROW - 1, -1, -1):
            rng = range(0, MainGame.CELLS_PER_COLUMN)
            if y % 2 == 0:
                rng = reversed(rng)
            for x in rng:
                ordered_group.append(group[y * MainGame.CELLS_PER_ROW + x])

        return ordered_group

    def initialise_players(self):
        group = []
        group.append(PlayerPiece(pygame.Color(128, 128, 128)))
        return group

    def move_player(self, player, steps):
        player.tile_index += steps
        player.set_position(self.grid_cells[player.tile_index])

    def start_game(self):
        grid_cell_sprites = pygame.sprite.Group(self.grid_cells)
        player_sprites = pygame.sprite.Group(self.players)
        while True:
            grid_cell_sprites.draw(self.screen)
            player_sprites.draw(self.screen)
            pygame.display.flip()


            pygame.time.wait(1000)
            self.move_player(self.players[0], 1)

if __name__ == "__main__":
    game = MainGame()
    game.start_game()