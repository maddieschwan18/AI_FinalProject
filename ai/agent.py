"""
AI agent for Grid Game.

This script reads a JSON request from stdin and writes a JSON response to
stdout. The Express API server (artifacts/api-server) invokes this script
once per AI move via subprocess.

Replace the body of `get_move` with your own AI logic. Everything else
(I/O wiring, validation, error reporting) is already handled below.

Request (stdin) shape:
    {
        "rows": int,                   # 2..10
        "cols": int,                   # 2..10
        "depth": int,                  # 1..10  (1 = 2D game, >1 = 3D game)
        "w": int,                      # 1..4   (1 = 2D/3D game, >1 = 4D game)
        "win_len": int,                # 2..10  (number in a row required to win)
        "board": list[str],            # length rows*cols*depth*w, each "" | "X" | "O"
        "player": "X" | "O"            # the marker the AI should place
    }

Index convention for `board`:
    idx = w * (rows * cols * depth) + z * (rows * cols) + y * cols + x
        x = column     (0..cols-1)
        y = row        (0..rows-1)
        z = layer      (0..depth-1)
        w = hyperslice (0..w-1)

Response (stdout) shape:
    {
        "row": int,                    # 0..rows-1     (y)
        "col": int,                    # 0..cols-1     (x)
        "z":   int,                    # 0..depth-1    (omit or 0 for 2D)
        "w":   int                     # 0..w-1        (omit or 0 for 2D/3D)
    }

On error, exit with a non-zero status code and write a JSON error object
to stdout: {"error": "<message>"}.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Literal, TypedDict


CellValue = Literal["", "X", "O"]
Player = Literal["X", "O"]


Difficulty = Literal["easy", "medium", "hard"]


# Probability the agent plays the heuristic (optimal) move at each difficulty.
# Anything else is filled in by a uniformly-random move.
#   easy   = 0.10  (≈ 90% random — barely above random)
#   hard   = 0.95  (≈  5% random — barely below perfect)
#   medium = (easy + hard) / 2 = 0.525  (exact midpoint)
_OPTIMAL_PROB = {"easy": 0.10, "medium": 0.525, "hard": 0.95}


class MoveRequest(TypedDict):
    rows: int
    cols: int
    depth: int
    w: int
    win_len: int
    difficulty: Difficulty
    board: List[CellValue]
    player: Player


class Move(TypedDict, total=False):
    row: int
    col: int
    z: int
    w: int


# ---------------------------------------------------------------------------
# Board state and helpers used by the user's AI heuristic below.
#
# `grid[x][y][z][w]` holds:
#   - 'X' or 'O' for filled cells
#   - the integer placeholder `x * n + y` for empty cells
# This matches the convention `evaluate_position` was written against
# (it restores empty cells to `x * n + y` after probing).
# ---------------------------------------------------------------------------

grid: list = []
n: int = 0           # size of the y dimension (rows)
m: int = 0           # size of the x dimension (cols)
_d: int = 1          # depth (z size)
_wsize: int = 1      # w size
win_len: int = 3


def _is_marker(v) -> bool:
    return v == 'X' or v == 'O'


def _build_directions():
    """All 40 4D line directions; first non-zero component is positive."""
    dirs = []
    for dw in (-1, 0, 1):
        for dz in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0 and dz == 0 and dw == 0:
                        continue
                    first = next(c for c in (dw, dz, dy, dx) if c != 0)
                    if first < 0:
                        continue
                    dirs.append((dx, dy, dz, dw))
    return dirs


_DIRECTIONS = _build_directions()


def _in_bounds(x: int, y: int, z: int, w: int) -> bool:
    return 0 <= x < m and 0 <= y < n and 0 <= z < _d and 0 <= w < _wsize


def _run_along(x, y, z, w, marker, dx, dy, dz, dw) -> int:
    """Length of consecutive `marker` cells starting at (x,y,z,w) walking +dir."""
    count = 0
    cx, cy, cz, cw = x, y, z, w
    while _in_bounds(cx, cy, cz, cw) and grid[cx][cy][cz][cw] == marker:
        count += 1
        cx += dx
        cy += dy
        cz += dz
        cw += dw
    return count


def check_wins(x: int, y: int, z: int, w: int) -> str:
    """Return 'TRUE' iff the marker at (x,y,z,w) sits in a line of >= win_len."""
    marker = grid[x][y][z][w]
    if not _is_marker(marker):
        return 'FALSE'
    for dx, dy, dz, dw in _DIRECTIONS:
        # Skip directions that step through dimensions of size 1.
        if dz != 0 and _d == 1:
            continue
        if dw != 0 and _wsize == 1:
            continue
        forward = _run_along(x, y, z, w, marker, dx, dy, dz, dw)
        backward = _run_along(
            x - dx, y - dy, z - dz, w - dw, marker, -dx, -dy, -dz, -dw
        )
        # `forward` already counts (x,y,z,w); `backward` is the run not including it.
        if forward + backward >= win_len:
            return 'TRUE'
    return 'FALSE'


def get_runs(x: int, y: int, z: int, w: int) -> list:
    """Run-length emanating from (x,y,z,w) along each line direction."""
    marker = grid[x][y][z][w]
    if not _is_marker(marker):
        return [0]
    runs = []
    for dx, dy, dz, dw in _DIRECTIONS:
        if dz != 0 and _d == 1:
            continue
        if dw != 0 and _wsize == 1:
            continue
        forward = _run_along(x, y, z, w, marker, dx, dy, dz, dw)
        backward = _run_along(
            x - dx, y - dy, z - dz, w - dw, marker, -dx, -dy, -dz, -dw
        )
        runs.append(forward + backward - 1)
    return runs if runs else [0]


# ---------------------------------------------------------------------------
# User-supplied AI logic — kept verbatim. The selection function was
# originally named `get_move`; it has been renamed to `_select_best_position`
# so that the entry-point `get_move(request)` (called by the I/O wiring) does
# not collide with it.
# ---------------------------------------------------------------------------

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

def _select_best_position(possible_positions, player):
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


# ---------------------------------------------------------------------------
# Entry point called by the I/O wiring. Sets up the module-level state
# (`grid`, `n`, `m`, `_d`, `_wsize`, `win_len`) that the user's heuristic
# above relies on, then delegates to `_select_best_position`.
# ---------------------------------------------------------------------------

def get_move(request: MoveRequest) -> Move:
    """
    Return the AI's next move for the given board state.

    >>> REPLACE THIS FUNCTION WITH YOUR PYTHON AI LOGIC. <<<

    The default implementation just picks a random empty cell, so the
    frontend has something to talk to until you wire in the real agent.
    Works for 2D (depth==1, w==1), 3D (depth>1, w==1), and 4D (w>1) boards.
    """
    """
    rows = request["rows"]
    cols = request["cols"]
    depth = request["depth"]
    board = request["board"]
    layer_size = rows * cols
    hyperslice_size = layer_size * depth

    empty_indices = [i for i, cell in enumerate(board) if cell == ""]
    if not empty_indices:
        raise ValueError("No empty cells remain on the board.")

    choice = random.choice(empty_indices)
    w = choice // hyperslice_size
    rem_w = choice % hyperslice_size
    z = rem_w // layer_size
    rem_z = rem_w % layer_size
    return {"row": rem_z // cols, "col": rem_z % cols, "z": z, "w": w}
    """
    global grid, n, m, _d, _wsize, win_len

    rows = request["rows"]
    cols = request["cols"]
    depth = request["depth"]
    w_size = request["w"]
    board = request["board"]
    player = request["player"]
    difficulty = request.get("difficulty", "hard")

    # Bind the module-level state the user's heuristic reads.
    n = rows           # `y` (row) ranges 0..n-1
    m = cols           # `x` (col) ranges 0..m-1
    _d = depth
    _wsize = w_size
    win_len = request.get("win_len", 3)

    # Build the 4D grid. Empty cells get the integer placeholder `x * n + y`
    # so that `evaluate_position`'s "restore" step (which writes that value
    # back) leaves the board in its original state.
    grid = [
        [
            [
                [(x * n + y) for _ in range(w_size)]
                for _ in range(depth)
            ]
            for y in range(rows)
        ]
        for x in range(cols)
    ]

    layer_size = rows * cols
    hyperslice_size = layer_size * depth
    for idx, cell in enumerate(board):
        if cell == "":
            continue
        ww = idx // hyperslice_size
        rem_w = idx % hyperslice_size
        zz = rem_w // layer_size
        rem_z = rem_w % layer_size
        yy = rem_z // cols
        xx = rem_z % cols
        grid[xx][yy][zz][ww] = cell

    # Build the list of empty positions in "x,y,z,w" string form, the shape
    # `_select_best_position` expects.
    possible_positions = []
    for xx in range(cols):
        for yy in range(rows):
            for zz in range(depth):
                for ww in range(w_size):
                    if not _is_marker(grid[xx][yy][zz][ww]):
                        possible_positions.append(f"{xx},{yy},{zz},{ww}")

    if not possible_positions:
        raise ValueError("No empty cells remain on the board.")

    # Difficulty mix: with probability `optimal_prob` play the heuristic move,
    # otherwise pick a uniformly-random empty cell.
    optimal_prob = _OPTIMAL_PROB.get(difficulty, _OPTIMAL_PROB["hard"])
    if random.random() < optimal_prob:
        chosen = _select_best_position(possible_positions, player)
    else:
        chosen = random.choice(possible_positions)

    xx, yy, zz, ww = map(int, chosen.split(','))
    return {"row": yy, "col": xx, "z": zz, "w": ww}


# ---------------------------------------------------------------------------
# I/O wiring — you generally do not need to edit anything below this line.
# ---------------------------------------------------------------------------


def _validate(request: object) -> MoveRequest:
    if not isinstance(request, dict):
        raise ValueError("Request must be a JSON object.")

    rows = request.get("rows")
    cols = request.get("cols")
    depth = request.get("depth", 1)
    w = request.get("w", 1)
    win_len_in = request.get("win_len", 3)
    difficulty = request.get("difficulty", "hard")
    board = request.get("board")
    player = request.get("player")

    if not isinstance(rows, int) or not (2 <= rows <= 10):
        raise ValueError("`rows` must be an integer in [2, 10].")
    if not isinstance(cols, int) or not (2 <= cols <= 10):
        raise ValueError("`cols` must be an integer in [2, 10].")
    if not isinstance(depth, int) or not (1 <= depth <= 10):
        raise ValueError("`depth` must be an integer in [1, 10].")
    if not isinstance(w, int) or not (1 <= w <= 4):
        raise ValueError("`w` must be an integer in [1, 4].")
    if not isinstance(win_len_in, int) or not (2 <= win_len_in <= 10):
        raise ValueError("`win_len` must be an integer in [2, 10].")
    if difficulty not in ("easy", "medium", "hard"):
        raise ValueError("`difficulty` must be 'easy', 'medium', or 'hard'.")
    expected_len = rows * cols * depth * w
    if not isinstance(board, list) or len(board) != expected_len:
        raise ValueError(
            f"`board` must be a list of length rows*cols*depth*w ({expected_len})."
        )
    for cell in board:
        if cell not in ("", "X", "O"):
            raise ValueError("Each board cell must be '', 'X', or 'O'.")
    if player not in ("X", "O"):
        raise ValueError("`player` must be 'X' or 'O'.")

    return {
        "rows": rows,
        "cols": cols,
        "depth": depth,
        "w": w,
        "win_len": win_len_in,
        "difficulty": difficulty,
        "board": board,
        "player": player,
    }


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("No input received on stdin.")
        request = _validate(json.loads(raw))
        move = get_move(request)

        z = move.get("z", 0)
        w = move.get("w", 0)
        row = move.get("row")
        col = move.get("col")

        if (
            not isinstance(row, int)
            or not isinstance(col, int)
            or not isinstance(z, int)
            or not isinstance(w, int)
        ):
            raise ValueError("AI must return integer `row`, `col`, `z`, and `w`.")
        if not (0 <= row < request["rows"]):
            raise ValueError(f"`row` {row} out of bounds for {request['rows']} rows.")
        if not (0 <= col < request["cols"]):
            raise ValueError(f"`col` {col} out of bounds for {request['cols']} cols.")
        if not (0 <= z < request["depth"]):
            raise ValueError(f"`z` {z} out of bounds for depth {request['depth']}.")
        if not (0 <= w < request["w"]):
            raise ValueError(f"`w` {w} out of bounds for size {request['w']}.")

        rows = request["rows"]
        cols = request["cols"]
        depth = request["depth"]
        idx = w * (rows * cols * depth) + z * (rows * cols) + row * cols + col
        if request["board"][idx] != "":
            raise ValueError(
                f"AI tried to play on occupied cell (row={row}, col={col}, z={z}, w={w})."
            )

        sys.stdout.write(json.dumps({"row": row, "col": col, "z": z, "w": w}))
        return 0
    except Exception as exc:  # noqa: BLE001
        import traceback
        sys.stderr.write(traceback.format_exc())
        sys.stdout.write(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
