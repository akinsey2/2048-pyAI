import GameMgr
import AutoPlay
import numpy as np

if __name__ == '__main__':

    # Test calc_metrics0()

    # Test calc_metrics1()
    b1 = [[0, 0, 0, 0],
          [0, 0, 0, 8],
          [0, 0, 4, 16],
          [2, 4, 8, 128]]
    t1 = np.array(b1)
    num1 = AutoPlay.calc_metrics1(t1)
    print(f"metric1 = {num1}")