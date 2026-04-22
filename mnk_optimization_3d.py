import random
random.seed(42)
import statistics
import pandas
import time
import numpy as np

def create_game():
    temp_grid = [i for i in range((n * m * o))]
    global grid
    grid = []
    for x in range(m):
        sub_grid = np.asarray(temp_grid[0:n*o]).reshape(n,o).tolist()
        grid.append(sub_grid)
        del temp_grid[0:n*o]

#AI
def evaluate_position(x, y, z, player):
    opponent = 'O' if player == 'X' else 'X'
    grid[x][y][z] = player
    if check_wins(x, y, z) == 'TRUE':
        grid[x][y][z] = x * n + y
        return 100000
    grid[x][y][z] = opponent
    if check_wins(x, y, z) == 'TRUE':
        grid[x][y][z] = x * n + y
        return 90000
    grid[x][y][z] = player
    score = 0
    runs = get_runs(x, y, z)
    score += max(runs) * 10
    score -= abs(x - m / 2) + abs(y - n / 2)
    grid[x][y][z] = x * n + y
    return score


def choose_move(possible_positions, player):
    best_score = -float('inf')
    best_moves = []
    for pos in possible_positions:
        x_coord, y_coord, z_coord = map(int, pos.split(','))
        score = evaluate_position(x_coord, y_coord, z_coord, player)
        if score > best_score:
            best_score = score
            best_moves = [pos]
        elif score == best_score:
            best_moves.append(pos)
    return random.choice(best_moves)  # keeps some variability

def get_runs(x_input, y_input, z_input):
    runs_list = []
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run1a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord] == grid[x_coord][y_coord][z_coord]:
            run1a += 1
            x_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run1b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0:
            run1b += 1
            x_coord -= 1
    except:
        pass
    run1 = run1a + run1b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run2a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord] == grid[x_coord][y_coord][z_coord]:
            run2a += 1
            x_coord += 1
            y_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run2b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0:
            run2b += 1
            x_coord -= 1
            y_coord -= 1
    except:
        pass
    run2 = run2a + run2b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run3a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord + 1] == grid[x_coord][y_coord][z_coord]:
            run3a += 1
            x_coord += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run3b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord - 1] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0 and z_coord - 1 >= 0:
            run3b += 1
            x_coord -= 1
            z_coord -= 1
    except:
        pass
    run3 = run3a + run3b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run4a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord + 1] == grid[x_coord][y_coord][z_coord]:
            run4a += 1
            y_coord += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run4b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord - 1] == grid[x_coord][y_coord][z_coord] and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run4b += 1
            y_coord -= 1
            z_coord -= 1
    except:
        pass
    run4 = run4a + run4b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run5a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord] == grid[x_coord][y_coord][z_coord]:
            run5a += 1
            y_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run5b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord] == grid[x_coord][y_coord][z_coord] and y_coord - 1 >= 0:
            run5b += 1
            y_coord -= 1
    except:
        pass
    run5 = run5a + run5b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run6a = 1
    try:
        while grid[x_coord][y_coord][z_coord + 1] == grid[x_coord][y_coord][z_coord]:
            run6a += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run6b = 1
    try:
        while grid[x_coord][y_coord][z_coord - 1] == grid[x_coord][y_coord][z_coord] and z_coord - 1 >= 0:
            run6b += 1
            z_coord -= 1
    except:
        pass
    run6 = run6a + run6b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run7a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord + 1] == grid[x_coord][y_coord][z_coord]:
            run7a += 1
            x_coord += 1
            y_coord += 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run7b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord - 1] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run7b += 1
            x_coord -= 1
            y_coord -= 1
            z_coord -= 1
    except:
        pass
    run7 = run7a + run7b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run8a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord - 1] == grid[x_coord][y_coord][z_coord] and y_coord - 1 >= 0 and z_coord - 1 >= 0:
            run8a += 1
            x_coord += 1
            y_coord -= 1
            z_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run8b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord + 1] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0:
            run8b += 1
            x_coord -= 1
            y_coord += 1
            z_coord += 1
    except:
        pass
    run8 = run8a + run8b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run9a = 1
    try:
        while grid[x_coord + 1][y_coord + 1][z_coord - 1] == grid[x_coord][y_coord][z_coord] and z_coord - 1 >= 0:
            run9a += 1
            x_coord += 1
            y_coord += 1
            z_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run9b = 1
    try:
        while grid[x_coord - 1][y_coord - 1][z_coord + 1] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0:
            run9b += 1
            x_coord -= 1
            y_coord -= 1
            z_coord += 1
    except:
        pass
    run9 = run9a + run9b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run10a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord + 1] == grid[x_coord][y_coord][z_coord] and y_coord - 1 >= 0:
            run10a += 1
            x_coord += 1
            y_coord -= 1
            z_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run10b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord - 1] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0 and z_coord - 1 >= 0:
            run10b += 1
            x_coord -= 1
            y_coord += 1
            z_coord -= 1
    except:
        pass
    run10 = run10a + run10b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run11a = 1
    try:
        while grid[x_coord + 1][y_coord - 1][z_coord] == grid[x_coord][y_coord][z_coord] and y_coord - 1 >= 0:
            run11a += 1
            x_coord += 1
            y_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run11b = 1
    try:
        while grid[x_coord - 1][y_coord + 1][z_coord] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0:
            run11b += 1
            x_coord -= 1
            y_coord += 1
    except:
        pass
    run11 = run11a + run11b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run12a = 1
    try:
        while grid[x_coord + 1][y_coord][z_coord - 1] == grid[x_coord][y_coord][z_coord] and z_coord - 1 >= 0:
            run12a += 1
            x_coord += 1
            z_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run12b = 1
    try:
        while grid[x_coord - 1][y_coord][z_coord + 1] == grid[x_coord][y_coord][z_coord] and x_coord - 1 >= 0:
            run12b += 1
            x_coord -= 1
            z_coord += 1
    except:
        pass
    run12 = run12a + run12b - 1
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run13a = 1
    try:
        while grid[x_coord][y_coord + 1][z_coord - 1] == grid[x_coord][y_coord][z_coord] and z_coord - 1 >= 0:
            run13a += 1
            y_coord += 1
            z_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    z_coord = z_input
    run13b = 1
    try:
        while grid[x_coord][y_coord - 1][z_coord + 1] == grid[x_coord][y_coord][z_coord] and y_coord - 1 >= 0:
            run13b += 1
            y_coord -= 1
            z_coord += 1
    except:
        pass
    run13 = run13a + run13b - 1
    return [run1, run2, run3, run4, run5, run6, run7, run8, run9, run10, run11, run12, run13]

def check_wins(x, y, z):
    if max(get_runs(x, y, z)) >= k:
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
                possible_positions.append(f'{x},{y},{z}')
    while win == 'FALSE':
        try:
            current_move = 'X'
            best_coords = choose_move(possible_positions, current_move)
            x_coord, y_coord, z_coord = best_coords.split(',')
            grid[int(x_coord)][int(y_coord)][int(z_coord)] = 'X'
            possible_positions.remove(best_coords)
            num_moves += 1
            win = check_wins(int(x_coord), int(y_coord), int(z_coord))
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
            x_coord, y_coord, z_coord = best_coords.split(',')
            grid[int(x_coord)][int(y_coord)][int(z_coord)] = 'O'
            possible_positions.remove(best_coords)
            num_moves += 1
            win = check_wins(int(x_coord), int(y_coord), int(z_coord))
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

def simulate(m_var, n_var, o_var, k_var, sim_var):
    global m
    m = m_var
    global n
    n = n_var
    global o
    o = o_var
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
global k_ind
k_ind = []
global outcome_ind
outcome_ind = []
global num_moves_ind
num_moves_ind = []

m_df = []
n_df = []
o_df = []
k_df = []
sim_num_df = []
X_wins_df = []
O_wins_df = []
Ties_df = []
num_moves_mean_df = []
num_moves_stdv_df = []

overall_start_time = time.time()
for m in range(1,4):
    for n in range(m,4):
        for o in range(max(m,n),4):
            for k in range(1, (max(m,n,o)+1)):
                start_time = time.time()
                simulate(m,n,o,k,1000)
                end_time = time.time()
                print(f'\033[1m{m}, {n}, {o}, {k}\033[0m completed in {end_time-start_time} at {time.time()}')
overall_end_time = time.time()
print(f'\033[1mAll permutations\033[0m completed in {overall_end_time-overall_start_time}')

data_aggregate = pandas.DataFrame({'m': m_df,
                         'n': n_df,
                         'o': o_df,
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
                         'k': k_ind,
                         'outcome': outcome_ind,
                         'num_moves': num_moves_ind,
                         })
print(data_individual.head())
print(data_individual.tail())