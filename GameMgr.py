import numpy as np
from copy import deepcopy
import Utils
# import pprint

SIZE = 4


class Game(object):

    def __init__(self, ui, tiles=None, score=0, num_moves=0):

        self.ui = ui

        if not tiles:
            self.tiles = np.zeros((SIZE, SIZE), dtype=np.int32)
        else:
            self.tiles = np.array(tiles, dtype=np.int32)

        self.score = int(score)
        self.num_moves = num_moves
        self.num_empty = None
        self.already_won = False
        self.game_over = False
        self.num_moves = num_moves

        self.rand = np.random.default_rng()
        self.last_move_valid = True

    def __repr__(self):
        out = []
        out.append("-"*30 + "\n" +
                   f"Game Score: {self.score} | Num Moves: {self.num_moves} | " +
                   f"Num Empty: {self.num_empty} | Won: {self.already_won} | " +
                   f"Game Over: {self.game_over}\n")
        out.append(repr(self.tiles) + "\n")

        return "".join(out)

    # move_tiles() supports multiple calling scenarios (effectively "overloaded")
    # 1: called by UI (game.ui != None), and must calculate and return UI-related features
    # 2: called by AutoPlay as confirmed game move (commit = True) that will change Game state
    # 3: called by AutoPlay for speculative game move (commit = False).  Unchanged game state.
    def move_tiles(self, direction, commit, tiles=None, score=None):

        if not isinstance(direction, int):
            raise TypeError("Game.move_tiles() direction is not int.")

        # Create vectors for animate_tiles()
        tile_move_vect = [[[0, 0] for _ in range(SIZE)] for __ in range(SIZE)]

        if commit and self.ui:

            # Create copy of tile widget array.  Original is needed in animate_tiles()
            self.ui.next_tile_widgets = [[None] * SIZE for _ in range(SIZE)]
            for row in range(SIZE):
                for col in range(SIZE):
                    self.ui.next_tile_widgets[row][col] = self.ui.tile_widgets[row][col]

        # If this is a speculative move, tiles is provided
        if tiles is None:
            tiles2 = self.tiles.copy()
        else:
            tiles2 = tiles.copy()

        # If this is a speculative move, score may be provided
        if score is None:
            score2 = deepcopy(self.score)
        else:
            score2 = deepcopy(score)

        valid_move = False

        # --- Begin primary move_tiles() loop

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
                elif tiles2[row1][col1] == 0:

                    # And the next tile is also empty
                    if tiles2[row2][col2] == 0:
                        eval_idx += inc
                        continue

                    # Found a tile, move to empty
                    else:
                        tiles2[row1][col1] = tiles2[row2][col2]
                        tiles2[row2][col2] = 0

                        # If being played with UI
                        if commit and self.ui:
                            self.ui.next_tile_widgets[row1][col1] = self.ui.next_tile_widgets[row2][col2]
                            self.ui.next_tile_widgets[row2][col2] = None
                            tile_move_vect[row2][col2] = [col1 - col2, row1 - row2]

                        valid_move = True
                        eval_idx += inc
                        continue

                # If the "place" cell is NOT empty
                else:

                    # And the next tile is empty
                    if tiles2[row2][col2] == 0:
                        eval_idx += inc
                        continue

                    # "Place" and "eval" tiles equal.  Merge.
                    elif tiles2[row1][col1] == tiles2[row2][col2]:
                        tile_sum = tiles2[row1][col1] + tiles2[row2][col2]
                        tiles2[row1][col1] = tile_sum
                        tiles2[row2][col2] = 0

                        # If being played with UI
                        if commit and self.ui:
                            self.ui.tiles_to_delete.append(self.ui.tile_widgets[row2][col2])
                            self.ui.next_tile_widgets[row2][col2] = None
                            tile_move_vect[row2][col2] = [col1 - col2, row1 - row2]

                        valid_move = True
                        place_idx += inc
                        eval_idx += inc
                        score2 += tile_sum
                        continue

                    # Tiles are different. Move "place" forward
                    else:
                        place_idx += inc
                        continue

        # --- End Primary Loop.

        if commit:
            self.last_move_valid = valid_move

            if valid_move:
                self.tiles = tiles2
                self.score = score2
                self.num_moves += 1

        return valid_move, tile_move_vect, tiles2, score2

    # MUST be called after move_tiles()
    # In the UI case, the animation is called first, then add_random_tile()
    def add_random_tile(self, commit, tiles=None, rands=None, rand_idx=None):

        if tiles is None:
            tiles = self.tiles.copy()

        game_over = False

        # Find open positions
        open_positions = np.argwhere(tiles == 0)
        num_empty = int(open_positions.size / 2)

        # --- Calculations to add tile
        if num_empty > 0:

            # If pre-calculated rands[] array is provided, use them
            if rands is not None:
                rand_idx2 = int(rands[rand_idx1] * num_empty)
                rand_idx += 1
                row = open_positions[rand_idx2][0]
                col = open_positions[rand_idx2][1]

                value = 2 if (rands[rand_idx] < 0.9) else 4
                rand_idx += 1

            # Else, generate random numbers
            else:
                rand_idx2 = self.rand.integers(0, num_empty)
                row = open_positions[rand_idx2][0]
                col = open_positions[rand_idx2][1]

                value = 2 if (self.rand.random() < 0.9) else 4

            tiles[row][col] = value
            num_empty -= 1

            if commit and self.ui is not None:
                self.ui.add_tile(row, col, value)

        # --- Tile now added

        if num_empty == 0:
            game_over = self.check_game_over(tiles)

        if commit:
            self.num_empty = num_empty
            self.tiles = tiles
            self.game_over = game_over

        return tiles, num_empty, game_over, rand_idx

    def check_game_over(self, tiles):

        up_valid, _, _, _ = self.move_tiles(0, False, tiles)
        right_valid, _, _, _ = self.move_tiles(1, False, tiles)
        down_valid, _, _, _ = self.move_tiles(2, False, tiles)
        left_valid, _, _, _ = self.move_tiles(3, False, tiles)

        if any([up_valid, right_valid, down_valid, left_valid]):
            return False

        return True
