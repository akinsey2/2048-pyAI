from numpy.random import default_rng
from copy import copy, deepcopy

import gameUIpyqt

SIZE = 4

class Game(object):

    def __init__(self, ui_main):

        self.ui_main = ui_main
        self.current_game = True
        self.is_paused = False
        self.raw_tiles = [[0] * SIZE for i in range(SIZE)]
        self.next_raw_tiles = [[0] * SIZE for i in range(SIZE)]
        self.num_empty = SIZE * SIZE
        self.tile_widgets = [[None] * SIZE for i in range(SIZE)]
        self.next_tile_widgets = [[None] * SIZE for i in range(SIZE)]
        self.rand = default_rng()
        self.tiles_to_delete = []
        self.score = 0


    def move_vert(self, direction):

        if not isinstance(direction, int): raise TypeError("Ui_MainWindow.move_vert() direction is not int.")

        tile_move_vect = [[[0, 0] for i in range(SIZE)] for j in range(SIZE)]
        self.next_raw_tiles = deepcopy(self.raw_tiles)
        self.next_tile_widgets = [[None] * SIZE for i in range(SIZE)]
        for row in range(SIZE):
            for col in range(SIZE):
                self.next_tile_widgets[row][col] = self.tile_widgets[row][col]
        valid_move = False

        # Method 1

        for col in range(SIZE):

            if direction == 0:  # Up
                place_row = 0
                eval_row = 1
                inc = 1
            else:  # Down
                place_row = SIZE - 1
                eval_row = SIZE - 2
                inc = -1

            while (eval_row > -1) and (eval_row < SIZE):

                if place_row == eval_row:
                    eval_row += inc
                    continue

                # If the "place" cell is empty
                elif self.next_raw_tiles[place_row][col] == 0:

                    # And the next tile is also empty
                    if self.next_raw_tiles[eval_row][col] == 0:
                        eval_row += inc
                        continue

                    # Found a tile, move to empty
                    else:
                        self.next_raw_tiles[place_row][col] = self.next_raw_tiles[eval_row][col]
                        self.next_tile_widgets[place_row][col] = self.next_tile_widgets[eval_row][col]
                        self.next_raw_tiles[eval_row][col] = 0
                        self.next_tile_widgets[eval_row][col] = None
                        tile_move_vect[eval_row][col][1] = place_row - eval_row
                        valid_move = True
                        eval_row += inc
                        continue

                # If the "place" cell is NOT empty
                else:

                    # And the next tile is empty
                    if self.next_raw_tiles[eval_row][col] == 0:
                        eval_row += inc
                        continue

                    # "Place" and "eval" tiles equal.  Merge.
                    elif self.next_raw_tiles[place_row][col] == self.next_raw_tiles[eval_row][col]:
                        sum = self.next_raw_tiles[place_row][col] + self.next_raw_tiles[eval_row][col]
                        self.next_raw_tiles[place_row][col] = sum
                        # self.next_tile_widgets[place_row][col].update(sum)
                        self.tiles_to_delete.append(self.next_tile_widgets[eval_row][col])
                        self.next_raw_tiles[eval_row][col] = 0
                        tile_move_vect[eval_row][col][1] = place_row - eval_row
                        valid_move = True
                        place_row += inc
                        eval_row += inc
                        continue

                    # Tiles are different. Move "place" forward
                    else:
                        place_row += inc
                        continue

        if not valid_move:
            self.tiles_to_delete.clear()
            return

        self.ui_main.animate_tiles(tile_move_vect)

    def move_horiz(self, direction):

        if not isinstance(direction, int): raise TypeError("Ui_MainWindow.move_vert() direction is not int.")

        tile_move_vect = [[[0, 0] for i in range(SIZE)] for j in range(SIZE)]
        self.next_raw_tiles = deepcopy(self.raw_tiles)
        self.next_tile_widgets = [[None] * SIZE for i in range(SIZE)]
        for row in range(SIZE):
            for col in range(SIZE):
                self.next_tile_widgets[row][col] = self.tile_widgets[row][col]
        valid_move = False

        for row in range(SIZE):

            if direction == 0:  # Left
                place_col = 0
                eval_col = 1
                inc = 1
            else:  # Right
                place_col = SIZE - 1
                eval_col = SIZE - 2
                inc = -1

            while (eval_col > -1) and (eval_col < SIZE):

                if place_col == eval_col:
                    eval_col += inc
                    continue

                # If the "place" cell is empty
                elif self.next_raw_tiles[row][place_col] == 0:

                    # And the next tile is also empty
                    if self.next_raw_tiles[row][eval_col] == 0:
                        eval_col += inc
                        continue

                    # Found a tile, move to empty
                    else:
                        self.next_raw_tiles[row][place_col] = self.next_raw_tiles[row][eval_col]
                        self.next_tile_widgets[row][place_col] = self.next_tile_widgets[row][eval_col]
                        self.next_raw_tiles[row][eval_col] = 0
                        self.next_tile_widgets[row][eval_col] = None
                        tile_move_vect[row][eval_col][0] = place_col - eval_col
                        valid_move = True
                        eval_col += inc
                        continue

                # If the "place" cell is NOT empty
                else:

                    # And the next tile is empty
                    if self.next_raw_tiles[row][eval_col] == 0:
                        eval_col += inc
                        continue

                    # "Place" and "eval" tiles equal.  Merge.
                    elif self.next_raw_tiles[row][place_col] == self.next_raw_tiles[row][eval_col]:
                        sum = self.next_raw_tiles[row][place_col] + self.next_raw_tiles[row][eval_col]
                        self.next_raw_tiles[row][place_col] = sum
                        # self.next_tile_widgets[place_row][col].update(sum)
                        self.tiles_to_delete.append(self.next_tile_widgets[row][eval_col])
                        self.next_raw_tiles[row][eval_col] = 0
                        tile_move_vect[row][eval_col][0] = place_col - eval_col
                        valid_move = True
                        place_col += inc
                        eval_col += inc
                        continue

                    # Tiles are different. Move "place" forward
                    else:
                        place_col += inc
                        continue

        if not valid_move:
            self.tiles_to_delete.clear()
            return

        self.ui_main.animate_tiles(tile_move_vect)


    def delete_and_new(self):


        self.tile_widgets = self.next_tile_widgets
        self.raw_tiles = self.next_raw_tiles

        empty = 0
        for row in range(SIZE):
            for col in range(SIZE):
                if self.next_raw_tiles[row][col] == 0:

                    empty += 1

                    if self.next_tile_widgets[row][col]:
                        self.next_tile_widgets[row][col].hide()
                        self.next_tile_widgets[row][col].destroy()

                elif self.tile_widgets[row][col]:
                    self.tile_widgets[row][col].update_num(self.raw_tiles[row][col])
                    self.tile_widgets[row][col].show()

        self.num_empty = empty

        for tile in self.tiles_to_delete:
            tile.hide()
            tile.destroy()

        self.tiles_to_delete.clear()
        self.add_random_tile()
        self.ui_main.centralwidget.grabKeyboard()


    def add_random_tile(self):

        # Find open positions
        open_positions = []
        for idx in range(16):
            if self.raw_tiles[idx // 4][idx % 4] == 0:
                open_positions.append(idx)

        num_open = len(open_positions)
        if num_open == 0:
            return

        rand_idx = self.rand.integers(0, num_open)
        pos = open_positions.pop(rand_idx)
        row = pos // SIZE
        col = pos % SIZE

        value = 2 if (self.rand.random() < 0.9) else 4

        self.raw_tiles[row][col] = value
        self.num_empty -= 1

        self.tile_widgets[row][col] = gameUIpyqt.TileWidget(self.ui_main.game_board, value, row, col)
        self.tile_widgets[row][col].show()