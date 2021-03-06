
"""
This file defines the core functionality of a (2048) game.
The Game class holds the basic state data of a game, and the methods to "move".
It is designed to used by separate modules implementing UI and AutoPlay functionality.
"""

from numpy import zeros, array, random, int32, argwhere
from copy import deepcopy
# import pprint

SIZE = 4


class Game(object):
    """
    Object to hold the data of a single game, and enable moves.

    ----- Attributes -----
    - tiles : a NumPy 2D-array containing the tiles numbers
    - rand : a NumPy random Generator of floats in [0.0, 1.0)

    score, num_moves, num_empty, already_won, game_over

    ----- Methods -----
    - move_tiles(direction, commit, tiles=None, score=None)
        Moves tiles in the direction specified per 2048 game rules.
        If (commit == False) , does NOT change internal game state (for speculative moves)

    - add_random_tile(commit, tiles=None, rands=None, rand_idx=None)
        Adds a random tile (2 or 4) to an open position in the 2D-array.
        If (commit == False), does NOT change internal game state (for speculative moves)
        Also checks to see if the game is over (no more valid moves left).

    check_game_over(tiles)
        Checks if any remaining valid moves are left.  Returns True if game over, else False
        Called by add_random_tile().
    """

    def __init__(self, ui, tiles=None, score=0, num_moves=0):

        self.ui = ui

        if tiles is None:
            self.tiles = zeros((SIZE, SIZE), dtype=int32)
        else:
            self.tiles = array(tiles, dtype=int32)

        self.score = int(score)
        self.num_moves = num_moves
        self.num_empty = None
        self.already_won = False
        self.game_over = False

        self.rand = random.default_rng()
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
        """
        Moves tiles in the 'direction' specified per 2048 game rules.

        This function is effectively "overloaded" and supports multiple calling scenarios.

        1. call by UI (game.ui != None), and must calculate and return UI-related features
        2. call by as a confirmed game move (commit = True) that DOES change Game state
        3. call by AutoPlay for speculative move (commit = False). Does NOT change game state.

        ----- Parameters -----
        :param direction: int 0-3. specifies move direction (0: Up, 1: Right, 2: Down, 3: Left)
        :param commit: bool. if True, this move DOES alter current game state.
                             if False, function does NOT change current game state.
        :param tiles: int Numpy 2D-array. default None --> creates empty board
                                          Else uses provided tiles.
        :param score: int. default None --> uses current "Game" score.  Else uses provided score

        ----- Return -----
        :returns:
        valid_move: bool
        tile_move_vect: list( int[n][n][2] ) for ui.animate_tiles()
        tiles2: NumPy int 2D-array of the tile numbers AFTER move
        score2: int of new score after move
        """

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

        # Create Copy of Tiles. If speculative move, tiles is provided
        if tiles is None:
            tiles2 = self.tiles.copy()
        else:
            tiles2 = tiles.copy()

        # If this is a speculative move, score may be provided
        score2 = deepcopy(self.score) if (score is None) else deepcopy(score)

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


    def add_random_tile(self, commit, tiles=None, rands=None, rand_idx=None):
        """
        Adds new tile to empty spot, if available. (MUST be called after move_tiles())

        This function is effectively "overloaded" and supports multiple calling scenarios.

        :param commit: bool. if True, this move DOES alter current game state.
                             if False, function does NOT change current game state.
        :param tiles: int Numpy 2D-array. default None --> creates empty board
                                          Else uses provided tiles.
        :param rands: If provided, huge NumPy 1D-array of random floats [0.0, 1.0)
                        If None, random numbers will be generated on the fly.
        :param rand_idx: int. If rands is provided, the current index to use for access
        """

        # If tiles is passed in, then it has already been copied in move_tiles()

        if tiles is None:
            tiles = self.tiles.copy()

        game_over = False

        # Find open positions
        open_positions = argwhere(tiles == 0)
        num_empty = int(open_positions.size / 2)

        # --- Calculations to add tile
        if num_empty > 0:

            # If pre-calculated rands[] array is provided, use them
            if rands is not None:
                rand_idx2 = int(rands[rand_idx] * num_empty)
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
        """Checks provided tiles to see if any valid moves are left.
        :param tiles: Numpy int 2D-array.
        :return: bool. True if game is over, False, otherwise"""

        up_valid, _, _, _ = self.move_tiles(0, False, tiles)
        right_valid, _, _, _ = self.move_tiles(1, False, tiles)
        down_valid, _, _, _ = self.move_tiles(2, False, tiles)
        left_valid, _, _, _ = self.move_tiles(3, False, tiles)

        if any([up_valid, right_valid, down_valid, left_valid]):
            return False

        return True
