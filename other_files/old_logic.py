from numpy.random import default_rng

class Game(object):

    def __init__(self, size):

        self._size = size
        self._tiles = [[0]*size for i in range(size)]

        # Tiles are indexed as follows
        #  -------------
        # | 0  1  2  3  |
        # | 4  5  6  7  |
        # | 8  9  10 11 |
        # | 12 13 14 15 |
        #  -------------

        self.rand = default_rng()

        # Generate UI
        # app = QApplication([])
        # main_window = QMainWindow()
        # ui = Ui_MainWindow()
        # ui.setupUi(main_window)
        # main_window.show()
        # sys.exit(app.exec())

    def __repr__(self):

        out = []
        header = ["{:^4d}".format(num) for num in range(self._size)]
        out.append(" ".join(header) + "\n")
        out.append("".join(["-"]*20) + "\n")

        for tile_row in self._tiles:
            strlist = ["{:^4d}".format(num) for num in tile_row]
            out.append("| " + "".join(strlist) + "\n")
        outstr = ''.join(out)

        return outstr

    def get_tiles(self):
        return (tuple(tile_row) for tile_row in self._tiles)

    def add_random_tile(self):

        open_positions = self.find_open_positions()
        num_open = len(open_positions)
        if num_open == 0:
            return

        rand_idx = self.rand.integers(0, num_open)
        pos = open_positions.pop(rand_idx)
        row_idx = pos // self._size
        col_idx = pos % self._size

        value = 2 if (self.rand.random() < 0.9) else 4
        self._tiles[row_idx][col_idx] = value

    def find_open_positions(self):

        open_positions = []

        for idx in range(16):
            if self._tiles[idx // 4][idx % 4] == 0:
                open_positions.append(idx)

        return open_positions

    def move_tiles(self, direction):

        # NEED to check if a move is "valid"...if there is something to move
        if not isinstance(direction, int):
            raise TypeError("'direction' input to move_tiles() is not of type 'int'")

        if direction == 0 or direction == 2:    # Up or Down
            self.move_tiles_vert(direction // 2)

        elif direction == 1 or direction == 3:  # Left or Right
            self.move_tiles_horiz((direction-1) // 2)

        else:
            raise ValueError("'direction' input to move_tiles() is not between 0-3"
                             "")

    def move_tiles_vert(self, direction):

        for col in range(4):  # In each column

            if direction == 0:  # Up
                place_row = 0
                eval_row = 1
                inc = 1
            else:               # Down
                place_row = self._size - 1
                eval_row = self._size - 2
                inc = -1

            # Evaluate, move and combine row tiles
            # starting from "direction" edge and moving across

            while (eval_row > -1) and (eval_row < self._size):
                if self._tiles[eval_row][col] == 0:  # If tile spot empty
                    eval_row += inc
                    continue
                else:
                    if place_row == eval_row:
                        eval_row += inc
                        continue
                    elif self._tiles[place_row][col] == 0:
                        self._tiles[place_row][col] = self._tiles[eval_row][col]
                        self._tiles[eval_row][col] = 0
                        eval_row += inc
                        continue
                    elif self._tiles[place_row][col] == self._tiles[eval_row][col]:
                        tile_sum: int = self._tiles[place_row][col] + self._tiles[eval_row][col]
                        self._tiles[place_row][col] = tile_sum
                        self._tiles[eval_row][col] = 0
                        eval_row += inc
                        place_row += inc
                    else:
                        place_row += inc

    def move_tiles_horiz(self, direction):

        for row in range(4):  # In each row

            if direction == 0:  # Left
                place_col = 0
                eval_col = 1
                inc = 1
            else:               # Right
                place_col = self._size - 1
                eval_col = self._size - 2
                inc = -1
            # Evaluate, move and combine row tiles
            # starting from "direction" edge and moving backwards

            while (eval_col > -1) and (eval_col < self._size):
                if self._tiles[row][eval_col] == 0:  # If tile spot empty
                    eval_col += inc
                    continue
                else:
                    if place_col == eval_col:
                        eval_col += inc
                        continue
                    # If "place" col empty, move "eval" tile into empty spot
                    elif self._tiles[row][place_col] == 0:
                        self._tiles[row][place_col] = self._tiles[row][eval_col]
                        self._tiles[row][eval_col] = 0
                        eval_col += inc
                        continue
                    elif self._tiles[row][place_col] == self._tiles[row][eval_col]:
                        tile_sum: int = self._tiles[row][place_col] + self._tiles[row][eval_col]
                        self._tiles[row][place_col] = tile_sum
                        self._tiles[row][eval_col] = 0
                        place_col += inc
                        eval_col += inc
                    else:
                        place_col += inc

    def is_game_over(self):
        pass


if __name__ == '__main__':
    # from gameUIpyqt import *
    # from PyQt6.QtWidgets import QApplication, QMainWindow
    from numpy import random
    import sys
    game1 = Game(4)
    print(game1)
    print(f"len(game1._tiles) = {len(game1._tiles)}")
    print(f"len(game1._tiles[0]) = {len(game1._tiles[0])}")

    for i in range(100):
        game1.add_random_tile()
        opens = game1.find_open_positions()
        print(f"Num Open: {len(opens)}")
        print(' '.join([f"{i}" for i in opens]))
        print(game1)
        game1.move_tiles(int(input("0:Up 1:Right 2:Down 3:Left : ")))
