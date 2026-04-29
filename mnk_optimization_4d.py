import random
random.seed(42)
import statistics
import pandas
import time
import numpy as np

def create_game():
    temp_grid = [i for i in range((m * n * o * p))]
    global grid
    grid = []
    for x in range(m):
        sub_grid = np.asarray(temp_grid[0:n*o*p]).reshape(n,o,p).tolist()
        grid.append(sub_grid)
        del temp_grid[0:n*o*p]

#AI
def evaluate_position(x, y, z, w, player):
    opponent = 'O' if player == 'X' else 'X'
    grid[x][y][z][w] = player
    if check_wins(x, y, z, w) == 'TRUE':
        grid[x][y][z][w] = x * n + y
        return 100000
    grid[x][y][z][w] = opponent
    if check_wins(x, y, z, w) == 'TRUE':
        grid[x][y][z][w] = x * n + y
        return 90000
    grid[x][y][z][w] = player
    score = 0
    runs = get_runs(x, y, z, w)
    score += max(runs) * 10
    score -= abs(x - m / 2) + abs(y - n / 2)
    grid[x][y][z][w] = x * n + y
    return score

def choose_move(possible_positions, player):
    best_score = -float('inf')
    best_moves = []
    for pos in possible_positions:
        x_coord, y_coord, z_coord, w_coord = map(int, pos.split(','))
        score = evaluate_position(x_coord, y_coord, z_coord, w_coord, player)
        if score > best_score:
            best_score = score
            best_moves = [pos]
        elif score == best_score:
            best_moves.append(pos)
    return random.choice(best_moves)  # keeps some variability

def get_runs(x_input, y_input, z_input, w_input):
    runs_list = []
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run1a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord][w_coord] == grid[x_coord][y_coord][z_coord][w_coord]:
            run1a += 1
            x_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run1b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0:
            run1b += 1
            x_coord -= 1
    except:
        pass
    run1 = run1a + run1b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run2a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord][w_coord] == grid[x_coord][y_coord][z_coord][w_coord]:
            run2a += 1
            y_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run2b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0:
            run2b += 1
            y_coord -= 1
    except:
        pass
    run2 = run2a + run2b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run3a = 1
    try:
        while grid[x_coord][y_coord][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord]:
            run3a += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run3b = 1
    try:
        while grid[x_coord][y_coord][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0:
            run3b += 1
            z_coord -= 1
    except:
        pass
    run3 = run3a + run3b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run4a = 1
    try:
        while grid[x_coord][y_coord][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord]:
            run4a += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run4b = 1
    try:
        while grid[x_coord][y_coord][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and w_coord - 1 >= 0:
            run4b += 1
            w_coord -= 1
    except:
        pass
    run4 = run4a + run4b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run5a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord][w_coord] == grid[x_coord][y_coord][z_coord][w_coord]:
            run5a += 1
            x_coord += 1
            y_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run5b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0:
            run5b += 1
            x_coord -= 1
            y_coord -= 1
    except:
        pass
    run5 = run5a + run5b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run6a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord]:
            run6a += 1
            x_coord += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run6b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and z_coord - 1 >= 0:
            run6b += 1
            x_coord -= 1
            z_coord -= 1
    except:
        pass
    run6 = run6a + run6b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run7a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord]:
            run7a += 1
            x_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run7b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and w_coord - 1 >= 0:
            run7b += 1
            x_coord -= 1
            w_coord -= 1
    except:
        pass
    run7 = run7a + run7b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run8a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord]:
            run8a += 1
            y_coord += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run8b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run8b += 1
            y_coord -= 1
            z_coord -= 1
    except:
        pass
    run8 = run8a + run8b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run9a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord]:
            run9a += 1
            y_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run9b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and w_coord - 1 >= 0:
            run9b += 1
            y_coord -= 1
            w_coord -= 1
    except:
        pass
    run9 = run9a + run9b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run10a = 1
    try:
        while grid[x_coord][y_coord][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord]:
            run10a += 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run10b = 1
    try:
        while grid[x_coord][y_coord][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run10b += 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    run10 = run10a + run10b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run11a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord]:
            run11a += 1
            x_coord += 1
            y_coord += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run11b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run11b += 1
            x_coord -= 1
            y_coord -= 1
            z_coord -= 1
    except:
        pass
    run11 = run11a + run11b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run12a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord]:
            run12a += 1
            x_coord += 1
            y_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run12b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0 and w_coord - 1 >= 0:
            run12b += 1
            x_coord -= 1
            y_coord -= 1
            w_coord -= 1
    except:
        pass
    run12 = run12a + run12b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run13a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord]:
            run13a += 1
            x_coord += 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run13b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run13b += 1
            x_coord -= 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    run13 = run13a + run13b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run14a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord]:
            run14a += 1
            y_coord += 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run14b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run14b += 1
            y_coord -= 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    run14 = run14a + run14b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run15a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord]:
            run15a += 1
            x_coord += 1
            y_coord += 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run15b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0 and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run15b += 1
            x_coord -= 1
            y_coord -= 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    run15 = run15a + run15b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run16a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and w_coord - 1 >= 0:
            run16a += 1
            x_coord += 1
            y_coord += 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run16b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run16b += 1
            x_coord -= 1
            y_coord -= 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    run16 = run16a + run16b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run17a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0:
            run17a += 1
            x_coord += 1
            y_coord += 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run17b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0 and w_coord - 1 >= 0:
            run17b += 1
            x_coord -= 1
            y_coord -= 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    run17 = run17a + run17b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run18a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0:
            run18a += 1
            x_coord += 1
            y_coord -= 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run18b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run18b += 1
            x_coord -= 1
            y_coord += 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    run18 = run18a + run18b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run19a = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0:
            run19a += 1
            x_coord -= 1
            y_coord += 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run19b = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run19b += 1
            x_coord += 1
            y_coord -= 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    run19 = run19a + run19b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run20a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run20a += 1
            x_coord += 1
            y_coord += 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run20b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0:
            run20b += 1
            x_coord -= 1
            y_coord -= 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    run20 = run20a + run20b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run21a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and w_coord - 1 >= 0:
            run21a += 1
            x_coord += 1
            y_coord -= 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run21b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and z_coord - 1 >= 0:
            run21b += 1
            x_coord -= 1
            y_coord += 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    run21 = run21a + run21b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run22a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run22a += 1
            x_coord += 1
            y_coord -= 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run22b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and w_coord - 1 >= 0:
            run22b += 1
            x_coord -= 1
            y_coord += 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    run22 = run22a + run22b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run23a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0:
            run23a += 1
            x_coord += 1
            y_coord += 1
            z_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run23b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0:
            run23b += 1
            x_coord -= 1
            y_coord -= 1
            z_coord += 1
    except:
        pass
    run23 = run23a + run23b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run24a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and w_coord - 1 >= 0:
            run24a += 1
            x_coord += 1
            y_coord += 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run24b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0:
            run24b += 1
            x_coord -= 1
            y_coord -= 1
            w_coord += 1
    except:
        pass
    run24 = run24a + run24b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run25a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0:
            run25a += 1
            x_coord += 1
            y_coord -= 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run25b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 > 0 and z_coord - 1 >= 0:
            run25b += 1
            x_coord -= 1
            y_coord += 1
            z_coord -= 1
    except:
        pass
    run25 = run25a + run25b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run26a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and w_coord - 1 >= 0:
            run26a += 1
            x_coord += 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run26b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and z_coord - 1 >= 0:
            run26b += 1
            x_coord -= 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    run26 = run26a + run26b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run27a = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0:
            run27a += 1
            x_coord -= 1
            y_coord += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run27b = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run27b += 1
            x_coord += 1
            y_coord -= 1
            z_coord -= 1
    except:
        pass
    run27 = run27a + run27b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run28a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and w_coord - 1 >= 0:
            run28a += 1
            y_coord += 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run28b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run28b += 1
            y_coord -= 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    run28 = run28a + run28b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run29a = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0:
            run29a += 1
            x_coord -= 1
            y_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run29b = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and w_coord - 1 >= 0:
            run29b += 1
            x_coord += 1
            y_coord -= 1
            w_coord -= 1
    except:
        pass
    run29 = run29a + run29b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run30a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0:
            run30a += 1
            y_coord += 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run30b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0 and w_coord - 1 >= 0:
            run30b += 1
            y_coord -= 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    run30 = run30a + run30b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run31a = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0:
            run31a += 1
            x_coord -= 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run31b = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run31b += 1
            x_coord += 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    run31 = run31a + run31b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run32a = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord + 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0:
            run32a += 1
            y_coord -= 1
            z_coord += 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run32b = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord - 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0 and w_coord - 1 >= 0:
            run32b += 1
            y_coord += 1
            z_coord -= 1
            w_coord -= 1
    except:
        pass
    run32 = run32a + run32b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run33a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0:
            run33a += 1
            x_coord += 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run33b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and w_coord - 1 >= 0:
            run33b += 1
            x_coord -= 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    run33 = run33a + run33b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run34a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord -1 >= 0:
            run34a += 1
            x_coord += 1
            y_coord -= 1
            w_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run34b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0 and w_coord - 1 >= 0:
            run34b += 1
            x_coord -= 1
            y_coord += 1
            w_coord -= 1
    except:
        pass
    run34 = run34a + run34b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run35a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0:
            run35a += 1
            x_coord += 1
            y_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run35b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0:
            run35b += 1
            x_coord -= 1
            y_coord += 1
    except:
        pass
    run35 = run35a + run35b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run36a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0:
            run36a += 1
            x_coord += 1
            z_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run36b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0:
            run36b += 1
            x_coord -= 1
            z_coord += 1
    except:
        pass
    run36 = run36a + run36b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run37a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and w_coord - 1 >= 0:
            run37a += 1
            x_coord += 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run37b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and x_coord - 1 >= 0:
            run37b += 1
            x_coord -= 1
            w_coord += 1
    except:
        pass
    run37 = run37a + run37b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run38a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord - 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0:
            run38a += 1
            y_coord += 1
            z_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run38b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord + 1][w_coord] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0:
            run38b += 1
            y_coord -= 1
            z_coord += 1
    except:
        pass
    run38 = run37a + run37b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run39a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and w_coord - 1 >= 0:
            run39a += 1
            y_coord += 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run39b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and y_coord - 1 >= 0:
            run39b += 1
            y_coord -= 1
            w_coord += 1
    except:
        pass
    run39 = run39a + run39b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run40a = 1
    try:
        while grid[x_coord][y_coord][z_coord + 1][w_coord - 1] == grid[x_coord][y_coord][z_coord][w_coord] and w_coord - 1 >= 0:
            run40a += 1
            z_coord += 1
            w_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    w_coord = w_input
    run40b = 1
    try:
        while grid[x_coord][y_coord][z_coord - 1][w_coord + 1] == grid[x_coord][y_coord][z_coord][w_coord] and z_coord - 1 >= 0:
            run40b += 1
            z_coord -= 1
            w_coord += 1
    except:
        pass
    run40 = run40a + run40b - 1
    return [run1, run2, run3, run4, run5, run6, run7, run8, run9, run10, run11, run12, run13, run14, run15, run16, run17, run18, run19, run20,
            run21, run22, run23, run24, run25, run26, run27, run28, run29, run30, run31, run32, run33, run34, run35, run36, run37, run38, run39, run40]

def check_wins(x, y, z, w):
    if max(get_runs(x, y, z, w)) >= k:
        return 'TRUE'
    else:
        return 'FALSE'

def conclude_game(result):
    global X_wins
    global O_wins
    global Ties
    if result == 'X':
        X_wins += 1
    if result == 'O':
        O_wins += 1
    if result == 'Tie':
        Ties += 1
    num_moves_ind.append(num_moves)

def report_results():
    m_df.append(m)
    n_df.append(n)
    o_df.append(o)
    p_df.append(p)
    k_df.append(k)
    sim_num_df.append(sim_num)
    X_wins_df.append(X_wins)
    O_wins_df.append(O_wins)
    Ties_df.append(Ties)
    num_moves_mean_df.append(statistics.mean(num_moves_global))
    num_moves_stdv_df.append(statistics.stdev(num_moves_global))

def run_game():
    m_ind.append(m)
    n_ind.append(n)
    o_ind.append(o)
    p_ind.append(p)
    k_ind.append(k)
    global win
    win = 'FALSE'
    global current_move
    global num_moves
    num_moves = 0
    possible_positions = []
    for x in range(m):
        for y in range(n):
            for z in range(o):
                for w in range(p):
                    possible_positions.append(f'{x},{y},{z},{w}')
    while win == 'FALSE':
        try:
            current_move = 'X'
            best_coords = choose_move(possible_positions, current_move)
            x_coord, y_coord, z_coord, w_coord = best_coords.split(',')
            grid[int(x_coord)][int(y_coord)][int(z_coord)][int(w_coord)] = 'X'
            possible_positions.remove(best_coords)
            num_moves += 1
            win = check_wins(int(x_coord),int(y_coord),int(z_coord),int(w_coord))
            if win == 'TRUE':
                num_moves_global.append(num_moves)
                break
        except IndexError:
            current_move = 'Tie'
            win = 'TRUE'
            num_moves_global.append(num_moves)
            break
        try:
            current_move = 'O'
            best_coords = choose_move(possible_positions, current_move)
            x_coord, y_coord, z_coord, w_coord = best_coords.split(',')
            grid[int(x_coord)][int(y_coord)][int(z_coord)][int(w_coord)] = 'O'
            possible_positions.remove(best_coords)
            num_moves += 1
            win = check_wins(int(x_coord),int(y_coord),int(z_coord),int(w_coord))
            if win == 'TRUE':
                num_moves_global.append(num_moves)
                break
        except IndexError:
            current_move = 'Tie'
            win = 'TRUE'
            num_moves_global.append(num_moves)
            break
    outcome_ind.append(current_move)
    conclude_game(current_move)

def simulate(m_var, n_var, o_var, p_var, k_var, sim_var):
    global m
    m = m_var
    global n
    n = n_var
    global o
    o = o_var
    global p
    p = p_var
    global k
    k = k_var
    global sim_num
    sim_num = sim_var
    global X_wins
    X_wins = 0
    global O_wins
    O_wins = 0
    global Ties
    Ties = 0
    global num_moves_global
    num_moves_global = []
    for i in range(sim_num):
        create_game()
        run_game()
    report_results()

global m_ind
m_ind = []
global n_ind
n_ind = []
global o_ind
o_ind = []
global p_ind
p_ind = []
global k_ind
k_ind = []
global outcome_ind
outcome_ind = []
global num_moves_ind
num_moves_ind = []

m_df = []
n_df = []
o_df = []
p_df = []
k_df = []
sim_num_df = []
X_wins_df = []
O_wins_df = []
Ties_df = []
num_moves_mean_df = []
num_moves_stdv_df = []

overall_start_time = time.time()
for m in range(1,6):
    for n in range(m,6):
        for o in range(max(m,n),6):
            for p in range(max(m,n,o), 6):
                for k in range(1, (max(m,n,o,p)+1)):
                    start_time = time.time()
                    simulate(m,n,o,p,k,1000)
                    end_time = time.time()
                    print(f'\033[1m{m}, {n}, {o}, {p}, {k}\033[0m completed in {end_time-start_time} at {time.time()}')
overall_end_time = time.time()
print(f'\033[1mAll permutations\033[0m completed in {overall_end_time-overall_start_time}')

data_aggregate = pandas.DataFrame({'m': m_df,
                         'n': n_df,
                         'o': o_df,
                         'p': p_df,
                         'k': k_df,
                         'sim_num': sim_num_df,
                         'X_wins': X_wins_df,
                         'O_wins': O_wins_df,
                         'Ties': Ties_df,
                         'num_moves_mean': num_moves_mean_df,
                         'num_moves_stdv': num_moves_stdv_df
                         })
print(data_aggregate.head())
print(data_aggregate.tail())

data_individual = pandas.DataFrame({'m': m_ind,
                         'n': n_ind,
                         'o': o_ind,
                         'p': p_ind,
                         'k': k_ind,
                         'outcome': outcome_ind,
                         'num_moves': num_moves_ind,
                         })
print(data_individual.head())
print(data_individual.tail())