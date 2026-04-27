import random
random.seed(42)
import statistics
import pandas
import time

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, world!"

if __name__ == "__main__":
    app.run(debug=True)

def create_game():
    temp_grid = [i for i in range((n * m))]
    global grid
    grid = []
    for x in range(m):
        grid.append(temp_grid[0:n])
        del temp_grid[0:n]

#AI
def evaluate_position(x, y, player):
    opponent = 'O' if player == 'X' else 'X'
    grid[x][y] = player
    if check_wins(x, y) == 'TRUE':
        grid[x][y] = x * n + y
        return 100000
    grid[x][y] = opponent
    if check_wins(x, y) == 'TRUE':
        grid[x][y] = x * n + y
        return 90000
    grid[x][y] = player
    score = 0
    runs = get_runs(x, y)
    score += max(runs) * 10
    score -= abs(x - m / 2) + abs(y - n / 2)
    grid[x][y] = x * n + y
    return score


def choose_move(possible_positions, player):
    best_score = -float('inf')
    best_moves = []
    for pos in possible_positions:
        x_coord, y_coord = map(int, pos.split(','))
        score = evaluate_position(x_coord, y_coord, player)
        if score > best_score:
            best_score = score
            best_moves = [pos]
        elif score == best_score:
            best_moves.append(pos)
    return random.choice(best_moves)

def get_runs(x_input, y_input):
    x_coord = x_input
    y_coord = y_input
    run1a = 1
    try:
        while grid[x_coord + 1][y_coord] == grid[x_coord][y_coord]:
            run1a += 1
            x_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    run1b = 1
    try:
        while grid[x_coord - 1][y_coord] == grid[x_coord][y_coord] and x_coord - 1 >= 0:
            run1b += 1
            x_coord -= 1
    except:
        pass
    run1 = run1a + run1b - 1
    x_coord = x_input
    y_coord = y_input
    run2a = 1
    try:
        while grid[x_coord][y_coord + 1] == grid[x_coord][y_coord]:
            run2a += 1
            y_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    run2b = 1
    try:
        while grid[x_coord][y_coord - 1] == grid[x_coord][y_coord] and y_coord - 1 >= 0:
            run2b += 1
            y_coord -= 1
    except:
        pass
    run2 = run2a + run2b - 1
    x_coord = x_input
    y_coord = y_input
    run3a = 1
    try:
        while grid[x_coord + 1][y_coord + 1] == grid[x_coord][y_coord]:
            run3a += 1
            x_coord += 1
            y_coord += 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    run3b = 1
    try:
        while grid[x_coord - 1][y_coord - 1] == grid[x_coord][y_coord] and x_coord - 1 >= 0 and y_coord - 1 >= 0:
            run3b += 1
            x_coord -= 1
            y_coord -= 1
    except:
        pass
    run3 = run3a + run3b - 1
    x_coord = x_input
    y_coord = y_input
    run4a = 1
    try:
        while grid[x_coord + 1][y_coord - 1] == grid[x_coord][y_coord] and y_coord - 1 >= 0:
            run4a += 1
            x_coord += 1
            y_coord -= 1
    except:
        pass
    x_coord = x_input
    y_coord = y_input
    run4b = 1
    try:
        while grid[x_coord - 1][y_coord + 1] == grid[x_coord][y_coord] and x_coord - 1 >= 0:
            run4b += 1
            x_coord -= 1
            y_coord += 1
    except:
        pass
    run4 = run4a + run4b - 1
    return [run1, run2, run3, run4]

def check_wins(x, y):
    if max(get_runs(x, y)) >= k:
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
    k_ind.append(k)
    global win
    win = 'FALSE'
    global current_move
    global num_moves
    num_moves = 0
    possible_positions = []
    for x in range(m):
        for y in range(n):
            possible_positions.append(f'{x},{y}')
    while win == 'FALSE':
        try:
            current_move = 'X'
            best_coords = choose_move(possible_positions, current_move)
            x_coord, y_coord = best_coords.split(',')
            grid[int(x_coord)][int(y_coord)] = 'X'
            possible_positions.remove(best_coords)
            num_moves += 1
            win = check_wins(int(x_coord), int(y_coord))
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
            x_coord, y_coord = best_coords.split(',')
            grid[int(x_coord)][int(y_coord)] = 'O'
            possible_positions.remove(best_coords)
            num_moves += 1
            win = check_wins(int(x_coord), int(y_coord))
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

def simulate(m_var, n_var, k_var, sim_var):
    global m
    m = m_var
    global n
    n = n_var
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
global k_ind
k_ind = []
global outcome_ind
outcome_ind = []
global num_moves_ind
num_moves_ind = []

m_df = []
n_df = []
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
        for k in range(1, min((max(m,n)+1), 11)):
            start_time = time.time()
            simulate(m,n,k,1000)
            end_time = time.time()
            print(f'\033[1m{m}, {n}, {k}\033[0m completed in {end_time-start_time} at {time.time()}')
overall_end_time = time.time()
print(f'\033[1mAll permutations\033[0m completed in {overall_end_time-overall_start_time}')

data_aggregate = pandas.DataFrame({'m': m_df,
                         'n': n_df,
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
                         'k': k_ind,
                         'outcome': outcome_ind,
                         'num_moves': num_moves_ind,
                         })
print(data_individual.head())
print(data_individual.tail())