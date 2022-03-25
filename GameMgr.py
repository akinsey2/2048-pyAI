from numpy.random import default_rng
from copy import deepcopy
import gameUIpyqt
import pprint

SIZE = 4


class Game(object):

    def __init__(self, ui_main):

        self.ui_main = ui_main
        self.current_game = True
        self.is_paused = False
        self.tiles_nums = [[0] * SIZE for _ in range(SIZE)]
        self.next_tiles_nums = [[0] * SIZE for _ in range(SIZE)]
        self.num_empty = SIZE * SIZE
        self.tile_widgets = [[None] * SIZE for _ in range(SIZE)]
        self.next_tile_widgets = [[None] * SIZE for _ in range(SIZE)]
        self.rand = default_rng()
        self.tiles_to_delete = []
        self.last_move_valid = True
        self.score = 0
        self.already_won = False


    def move_tiles(self, direction):

        if not isinstance(direction, int):
            raise TypeError("Ui_MainWindow.move_vert() direction is not int.")

        tile_move_vect = [[[0, 0] for _ in range(SIZE)] for __ in range(SIZE)]

        # Create copies of tiles_nums and tile widget array to hold tiles after move
        self.next_tiles_nums = deepcopy(self.tiles_nums)
        self.next_tile_widgets = [[None] * SIZE for _ in range(SIZE)]
        for row in range(SIZE):
            for col in range(SIZE):
                self.next_tile_widgets[row][col] = self.tile_widgets[row][col]

        valid_move = False

        # For each row (if left/right) or col (if up/down)
        for idx1 in range(SIZE):

            if direction == 0:  # Move up
                (col1, col2, place_idx, eval_idx, inc) = (idx1, idx1, 0, 1, 1)
            elif direction == 1:  # Move Right
                (row1, row2, place_idx, eval_idx, inc) = (idx1, idx1, SIZE - 1, SIZE - 2, -1)
            elif direction == 2:  # Move Down
                (col1, col2, place_idx, eval_idx, inc) = (idx1, idx1, SIZE - 1, SIZE - 2, -1)
            elif direction == 3:  # Move Left
                (row1, row2, place_idx, eval_idx, inc) = (idx1, idx1, 0, 1, 1)
            else:
                raise ValueError("'direction' value invalid.  Must be 0-3.")

            # Traverse: (across cols in row if left/right) (across rows in col if up/down)
            while (eval_idx > -1) and (eval_idx < SIZE):

                if direction in [0, 2]:  # If move is up/down, traverse rows in column
                    (row1, row2) = (place_idx, eval_idx)
                else:  # If move is left/right, traverse cols in row
                    (col1, col2) = (place_idx, eval_idx)

                if place_idx == eval_idx:
                    eval_idx += inc
                    continue

                # If the "place" cell is empty
                elif self.next_tiles_nums[row1][col1] == 0:

                    # And the next tile is also empty
                    if self.next_tiles_nums[row2][col2] == 0:
                        eval_idx += inc
                        continue

                    # Found a tile, move to empty
                    else:
                        self.next_tiles_nums[row1][col1] = self.next_tiles_nums[row2][col2]
                        self.next_tile_widgets[row1][col1] = self.next_tile_widgets[row2][col2]
                        self.next_tiles_nums[row2][col2] = 0
                        self.next_tile_widgets[row2][col2] = None
                        tile_move_vect[row2][col2] = [col1 - col2, row1 - row2]
                        valid_move = True
                        eval_idx += inc
                        continue

                # If the "place" cell is NOT empty
                else:

                    # And the next tile is empty
                    if self.next_tiles_nums[row2][col2] == 0:
                        eval_idx += inc
                        continue

                    # "Place" and "eval" tiles equal.  Merge.
                    elif self.next_tiles_nums[row1][col1] == self.next_tiles_nums[row2][col2]:
                        tile_sum = self.next_tiles_nums[row1][col1] + self.next_tiles_nums[row2][col2]
                        self.next_tiles_nums[row1][col1] = tile_sum
                        self.tiles_to_delete.append(self.tile_widgets[row2][col2])
                        self.next_tiles_nums[row2][col2] = 0
                        self.next_tile_widgets[row2][col2] = None
                        tile_move_vect[row2][col2] = [col1 - col2, row1 - row2]
                        valid_move = True
                        place_idx += inc
                        eval_idx += inc
                        self.score += tile_sum
                        continue

                    # Tiles are different. Move "place" forward
                    else:
                        place_idx += inc
                        continue

        self.last_move_valid = valid_move

        return valid_move, tile_move_vect

    def delete_and_new(self):

        for tile in self.tiles_to_delete:
            tile.hide()
            tile.destroy()

        self.ui_main.curr_score.setText(str(self.score))
        self.tile_widgets = self.next_tile_widgets
        self.tiles_nums = self.next_tiles_nums

        empty = 0
        for row in range(SIZE):
            for col in range(SIZE):

                if self.tiles_nums[row][col] == 0:
                    empty += 1

                    # if self.tile_widgets[row][col]:
                    #     self.tile_widgets[row][col].hide()
                    #     self.tile_widgets[row][col].destroy()

                elif self.tile_widgets[row][col]:
                    self.tile_widgets[row][col].update_num(self.tiles_nums[row][col])
                    self.tile_widgets[row][col].show()

                    if (not self.already_won) and self.tiles_nums[row][col] == 2048:
                        keep_playing = self.ui_main.won_game()
                        if keep_playing:
                            self.already_won = True
                            continue
                        else:
                            self.ui_main.stop_game()

        self.num_empty = empty

        self.tiles_to_delete.clear()
        self.add_random_tile()
        self.ui_main.centralwidget.grabKeyboard()

        # # DEBUG
        # print("Raw Tiles")
        # pprint.pp(self.tiles_nums)
        # print("Tile Widgets")
        # pprint.pp(self.tile_widgets)

    def add_random_tile(self):

        # Find open positions
        open_positions = []
        for idx in range(16):
            if self.tiles_nums[idx // 4][idx % 4] == 0:
                open_positions.append(idx)

        self.num_empty = len(open_positions)

        if self.num_empty == 0:
            return

        rand_idx = self.rand.integers(0, self.num_empty)
        pos = open_positions.pop(rand_idx)
        row = pos // SIZE
        col = pos % SIZE

        value = 2 if (self.rand.random() < 0.9) else 4

        self.tiles_nums[row][col] = value
        self.num_empty -= 1

        self.tile_widgets[row][col] = gameUIpyqt.TileWidget(self.ui_main.game_board, value, row, col)
        self.tile_widgets[row][col].show()

        if self.num_empty == 0:
            self.check_game_over()

    def check_game_over(self):

        up_valid, _ = self.move_tiles(0)
        right_valid, _ = self.move_tiles(1)
        down_valid, _ = self.move_tiles(2)
        left_valid, _ = self.move_tiles(3)


        if not (up_valid or down_valid or left_valid or right_valid):
            self.ui_main.game_over()


