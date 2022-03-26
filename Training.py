import AutoPlay
import csv

if __name__ == '__main__':

    records = []

    tree_depth_max = 8
    topx_max = 8

    start_tiles = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    for calc_option in range(0,4):

        for tree_depth in range(3,tree_depth_max+1):

            for topx in range(topx_max+1):

                for game_num in range(1):

                    total_fwd_tiles = 0
                    for i in range(tree_depth+1):
                        total_fwd_tiles += 4**i

                    if (2**topx) > (total_fwd_tiles / 4):
                        continue

                    game = AutoPlay.AutoPlayer(start_tiles, 0, tree_depth, 2**topx, calc_option)
                    game_over = False

                    while not game_over:

                        valid_move, tiles, score, num_empty = game.auto_move()
                        game_over = (not valid_move) and (num_empty == 0)

                    records.append([calc_option, tree_depth, topx, game_num, score])

    filename = f"tdmax{tree_depth_max}_topx{topx_max}_1.csv"

    with open(filename, mode='w') as file1:
        csv_writer = csv.writer(file1)
        csv_writer.writerow(["Calc_Option", "Tree_Depth", "TopX", "Game_Number", "Score"])  # Must write header row manually
        for row_list in data:
            csv_writer.writerow(row_list)  # pass write data as list which will be str() formatted


