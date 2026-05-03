import { useEffect, useMemo, useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import {
  RotateCcw,
  Grid3x3,
  Bot,
  AlertCircle,
  Loader2,
  Trophy,
  Eraser,
  Box,
  Square,
  Layers,
  Lightbulb,
} from "lucide-react";
import { useGetAiMove } from "@workspace/api-client-react";
import { CubePreview } from "@/components/cube-preview";

type CellValue = "" | "X" | "O";
type Player = "X" | "O";
type GameMode = "2d" | "3d" | "4d";

const MIN_SIZE = 2;
const MAX_SIZE = 10;
const MIN_WIN_LEN = 2;
const MIN_DEPTH = 2;
const MAX_DEPTH = 6;
const MIN_W = 2;
const MAX_W = 4;

function makeEmptyBoard(
  rows: number,
  cols: number,
  depth: number,
  w: number,
): CellValue[] {
  return Array<CellValue>(rows * cols * depth * w).fill("");
}

function idxOf(
  rows: number,
  cols: number,
  depth: number,
  x: number,
  y: number,
  z: number,
  w: number,
) {
  return w * (rows * cols * depth) + z * (rows * cols) + y * cols + x;
}

// All 4D line directions, with the canonical "first non-zero component is positive"
// rule to avoid double-counting opposites. For 4D this gives (3^4 - 1) / 2 = 40
// directions. With dw=0 it collapses to the 13 3D directions; with dw=0,dz=0 to
// the 4 2D directions. We filter dw!=0 / dz!=0 components at the call site if the
// board's w/depth is 1.
function buildDirections4D(): Array<[number, number, number, number]> {
  const dirs: Array<[number, number, number, number]> = [];
  for (let dw = -1; dw <= 1; dw++) {
    for (let dz = -1; dz <= 1; dz++) {
      for (let dy = -1; dy <= 1; dy++) {
        for (let dx = -1; dx <= 1; dx++) {
          if (dw === 0 && dz === 0 && dy === 0 && dx === 0) continue;
          // Canonical form: first non-zero component (in dw, dz, dy, dx order)
          // must be positive.
          const components = [dw, dz, dy, dx];
          const firstNonZero = components.find((c) => c !== 0)!;
          if (firstNonZero < 0) continue;
          dirs.push([dx, dy, dz, dw]);
        }
      }
    }
  }
  return dirs;
}

const DIRECTIONS_4D = buildDirections4D();

function findWinningLine(
  board: CellValue[],
  rows: number,
  cols: number,
  depth: number,
  w: number,
  winLen: number,
): { player: Player; cells: number[] } | null {
  for (let wi = 0; wi < w; wi++) {
    for (let z = 0; z < depth; z++) {
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const start = board[idxOf(rows, cols, depth, x, y, z, wi)];
          if (start !== "X" && start !== "O") continue;
          for (const [dx, dy, dz, dw] of DIRECTIONS_4D) {
            if (dz !== 0 && depth === 1) continue;
            if (dw !== 0 && w === 1) continue;
            const endX = x + dx * (winLen - 1);
            const endY = y + dy * (winLen - 1);
            const endZ = z + dz * (winLen - 1);
            const endW = wi + dw * (winLen - 1);
            if (endX < 0 || endX >= cols) continue;
            if (endY < 0 || endY >= rows) continue;
            if (endZ < 0 || endZ >= depth) continue;
            if (endW < 0 || endW >= w) continue;
            const cells: number[] = [];
            let ok = true;
            for (let k = 0; k < winLen; k++) {
              const idx = idxOf(
                rows,
                cols,
                depth,
                x + dx * k,
                y + dy * k,
                z + dz * k,
                wi + dw * k,
              );
              if (board[idx] !== start) {
                ok = false;
                break;
              }
              cells.push(idx);
            }
            if (ok) return { player: start, cells };
          }
        }
      }
    }
  }
  return null;
}

export default function GridPage() {
  const [mode, setMode] = useState<GameMode>("2d");
  const [rows, setRows] = useState<number>(3);
  const [cols, setCols] = useState<number>(3);
  const [depth, setDepth] = useState<number>(3);
  const [w, setW] = useState<number>(2);
  const [winLen, setWinLen] = useState<number>(3);

  const effectiveDepth = mode === "2d" ? 1 : depth;
  const effectiveW = mode === "4d" ? w : 1;
  const [board, setBoard] = useState<CellValue[]>(() =>
    makeEmptyBoard(3, 3, 1, 1),
  );
  const [currentPlayer, setCurrentPlayer] = useState<Player>("X");
  const [moveCount, setMoveCount] = useState<number>(0);

  const [vsAi, setVsAi] = useState<boolean>(false);
  const [humanPlayer, setHumanPlayer] = useState<Player>("X");
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">(
    "medium",
  );
  const [aiError, setAiError] = useState<string | null>(null);

  const [scores, setScores] = useState<{ X: number; O: number; draws: number }>(
    { X: 0, O: 0, draws: 0 },
  );
  const scoredGameRef = useRef<number>(0);

  const aiMutation = useGetAiMove();
  const aiMutate = aiMutation.mutate;
  const isAiThinking = aiMutation.isPending;
  const requestedRef = useRef<number>(0);

  const hintMutation = useGetAiMove();
  const hintMutate = hintMutation.mutate;
  const isHintLoading = hintMutation.isPending;
  const [hintIdx, setHintIdx] = useState<number | null>(null);
  const hintTimerRef = useRef<number | null>(null);

  const aiPlayer: Player = humanPlayer === "X" ? "O" : "X";
  const noEmptyCells = useMemo(() => board.every((c) => c !== ""), [board]);
  const maxWinLen =
    mode === "4d"
      ? Math.max(rows, cols, effectiveDepth, effectiveW)
      : mode === "3d"
        ? Math.max(rows, cols, effectiveDepth)
        : Math.max(rows, cols);
  const effectiveWinLen = Math.min(winLen, maxWinLen);

  const winner = useMemo(
    () =>
      findWinningLine(
        board,
        rows,
        cols,
        effectiveDepth,
        effectiveW,
        effectiveWinLen,
      ),
    [board, rows, cols, effectiveDepth, effectiveW, effectiveWinLen],
  );
  const isGameOver = winner !== null || noEmptyCells;

  const resetState = useCallback(
    (
      nextRows: number,
      nextCols: number,
      nextDepth: number,
      nextW: number,
      opts?: { resetScores?: boolean },
    ) => {
      setBoard(makeEmptyBoard(nextRows, nextCols, nextDepth, nextW));
      setCurrentPlayer("X");
      setMoveCount(0);
      setAiError(null);
      requestedRef.current += 1;
      scoredGameRef.current += 1;
      if (opts?.resetScores) {
        setScores({ X: 0, O: 0, draws: 0 });
      }
    },
    [],
  );

  const handleResetScores = useCallback(() => {
    setScores({ X: 0, O: 0, draws: 0 });
  }, []);

  // Tally a finished game exactly once.
  useEffect(() => {
    if (!isGameOver) return;
    const gameId = scoredGameRef.current;
    if (gameId < 0) return;
    scoredGameRef.current = -1;
    setScores((prev) => {
      if (winner) {
        return { ...prev, [winner.player]: prev[winner.player] + 1 };
      }
      return { ...prev, draws: prev.draws + 1 };
    });
  }, [isGameOver, winner]);

  const handleModeChange = useCallback(
    (next: GameMode) => {
      setMode(next);
      const nextDepth = next === "2d" ? 1 : depth;
      const nextW = next === "4d" ? w : 1;
      resetState(rows, cols, nextDepth, nextW, { resetScores: true });
    },
    [rows, cols, depth, w, resetState],
  );

  const handleRowsChange = useCallback(
    (value: number[]) => {
      const next = value[0] ?? MIN_SIZE;
      setRows(next);
      resetState(next, cols, effectiveDepth, effectiveW, { resetScores: true });
    },
    [cols, effectiveDepth, effectiveW, resetState],
  );

  const handleColsChange = useCallback(
    (value: number[]) => {
      const next = value[0] ?? MIN_SIZE;
      setCols(next);
      resetState(rows, next, effectiveDepth, effectiveW, { resetScores: true });
    },
    [rows, effectiveDepth, effectiveW, resetState],
  );

  const handleDepthChange = useCallback(
    (value: number[]) => {
      const next = value[0] ?? MIN_DEPTH;
      setDepth(next);
      resetState(rows, cols, next, effectiveW, { resetScores: true });
    },
    [rows, cols, effectiveW, resetState],
  );

  const handleWChange = useCallback(
    (value: number[]) => {
      const next = value[0] ?? MIN_W;
      setW(next);
      resetState(rows, cols, effectiveDepth, next, { resetScores: true });
    },
    [rows, cols, effectiveDepth, resetState],
  );

  const requestHint = useCallback(() => {
    if (!vsAi) return;
    if (isGameOver) return;
    if (currentPlayer !== humanPlayer) return;
    if (isAiThinking || isHintLoading) return;
    if (noEmptyCells) return;

    if (hintTimerRef.current !== null) {
      window.clearTimeout(hintTimerRef.current);
      hintTimerRef.current = null;
    }
    setHintIdx(null);

    hintMutate(
      {
        data: {
          rows,
          cols,
          depth: effectiveDepth,
          w: effectiveW,
          winLen: effectiveWinLen,
          difficulty: "hard",
          board,
          player: humanPlayer,
        },
      },
      {
        onSuccess: (move) => {
          const z = move.z ?? 0;
          const wi = move.w ?? 0;
          const idx = idxOf(
            rows,
            cols,
            effectiveDepth,
            move.col,
            move.row,
            z,
            wi,
          );
          setHintIdx(idx);
          hintTimerRef.current = window.setTimeout(() => {
            setHintIdx(null);
            hintTimerRef.current = null;
          }, 2500);
        },
      },
    );
  }, [
    vsAi,
    isGameOver,
    currentPlayer,
    humanPlayer,
    isAiThinking,
    isHintLoading,
    noEmptyCells,
    rows,
    cols,
    effectiveDepth,
    effectiveW,
    effectiveWinLen,
    board,
    hintMutate,
  ]);

  // Clear any active hint as soon as the board changes (a move was made).
  useEffect(() => {
    if (hintTimerRef.current !== null) {
      window.clearTimeout(hintTimerRef.current);
      hintTimerRef.current = null;
    }
    setHintIdx(null);
  }, [board]);

  // Cleanup hint timer on unmount.
  useEffect(() => {
    return () => {
      if (hintTimerRef.current !== null) {
        window.clearTimeout(hintTimerRef.current);
      }
    };
  }, []);

  const handleCellClick = useCallback(
    (index: number) => {
      if (isGameOver) return;
      if (board[index] !== "") return;
      if (vsAi && currentPlayer !== humanPlayer) return;
      if (isAiThinking) return;

      setBoard((prev) => {
        const next = [...prev];
        next[index] = currentPlayer;
        return next;
      });
      setCurrentPlayer((p) => (p === "X" ? "O" : "X"));
      setMoveCount((c) => c + 1);
      setAiError(null);
    },
    [board, currentPlayer, vsAi, humanPlayer, isAiThinking, isGameOver],
  );

  const handleReset = useCallback(() => {
    resetState(rows, cols, effectiveDepth, effectiveW);
  }, [rows, cols, effectiveDepth, effectiveW, resetState]);

  const handleToggleVsAi = useCallback(
    (next: boolean) => {
      setVsAi(next);
      resetState(rows, cols, effectiveDepth, effectiveW, { resetScores: true });
    },
    [rows, cols, effectiveDepth, effectiveW, resetState],
  );

  const handleSwapSides = useCallback(() => {
    setHumanPlayer((p) => (p === "X" ? "O" : "X"));
    resetState(rows, cols, effectiveDepth, effectiveW, { resetScores: true });
  }, [rows, cols, effectiveDepth, effectiveW, resetState]);

  // When it's the AI's turn, ask the backend for its move.
  useEffect(() => {
    if (!vsAi) return;
    if (isGameOver) return;
    if (currentPlayer === humanPlayer) return;
    if (isAiThinking) return;

    const requestId = requestedRef.current;
    const snapshotBoard = board;
    const snapshotRows = rows;
    const snapshotCols = cols;
    const snapshotDepth = effectiveDepth;
    const snapshotW = effectiveW;
    const snapshotWinLen = effectiveWinLen;
    const snapshotDifficulty = difficulty;

    aiMutate(
      {
        data: {
          rows: snapshotRows,
          cols: snapshotCols,
          depth: snapshotDepth,
          w: snapshotW,
          winLen: snapshotWinLen,
          difficulty: snapshotDifficulty,
          board: snapshotBoard,
          player: aiPlayer,
        },
      },
      {
        onSuccess: (move) => {
          if (requestId !== requestedRef.current) return;
          const z = move.z ?? 0;
          const wOut = move.w ?? 0;
          const idx = idxOf(
            snapshotRows,
            snapshotCols,
            snapshotDepth,
            move.col,
            move.row,
            z,
            wOut,
          );
          if (
            idx < 0 ||
            idx >= snapshotBoard.length ||
            snapshotBoard[idx] !== ""
          ) {
            setAiError(
              `AI returned an occupied or invalid cell (row=${move.row}, col=${move.col}, z=${z}, w=${wOut}).`,
            );
            return;
          }
          setBoard((prev) => {
            const next = [...prev];
            next[idx] = aiPlayer;
            return next;
          });
          setCurrentPlayer(humanPlayer);
          setMoveCount((c) => c + 1);
          setAiError(null);
        },
        onError: (err) => {
          if (requestId !== requestedRef.current) return;
          const message =
            err && typeof err === "object" && "data" in err
              ? ((err as { data?: { error?: string } }).data?.error ?? null)
              : null;
          setAiError(
            message ?? (err instanceof Error ? err.message : "AI request failed."),
          );
        },
      },
    );
  }, [
    vsAi,
    isGameOver,
    currentPlayer,
    humanPlayer,
    isAiThinking,
    board,
    rows,
    cols,
    effectiveDepth,
    effectiveW,
    effectiveWinLen,
    difficulty,
    aiPlayer,
    aiMutate,
  ]);

  const cellSizePx = useMemo(() => {
    const longest2d = Math.max(rows, cols);
    if (mode === "4d") {
      // Even smaller cells in 4D since the slices grid can be very wide.
      const target = Math.min(220, Math.max(110, 40 * longest2d));
      return Math.floor(target / longest2d);
    }
    if (mode === "3d") {
      const target = Math.min(280, Math.max(140, 50 * longest2d));
      return Math.floor(target / longest2d);
    }
    const target = Math.min(560, Math.max(280, 80 * longest2d));
    return Math.floor(target / longest2d);
  }, [mode, rows, cols]);

  const turnLabel = isGameOver
    ? winner
      ? "Winner"
      : "Result"
    : vsAi
      ? currentPlayer === humanPlayer
        ? "Your turn"
        : isAiThinking
          ? "AI thinking…"
          : "AI's turn"
      : "Next";

  const turnValueText = isGameOver
    ? winner
      ? winner.player
      : "Draw"
    : currentPlayer;

  const winningCellSet = useMemo(
    () => new Set(winner?.cells ?? []),
    [winner],
  );

  const winnerBannerText = winner
    ? vsAi
      ? winner.player === humanPlayer
        ? `You win! (${winner.player})`
        : `AI wins (${winner.player})`
      : `${winner.player} wins!`
    : noEmptyCells
      ? "It's a draw."
      : null;

  const renderSlice = (z: number, wi: number) => (
    <div
      key={`slice-${wi}-${z}`}
      className="flex flex-col items-center gap-2"
      data-testid={`slice-${wi}-${z}`}
    >
      {mode !== "2d" && (
        <div className="font-mono text-xs uppercase tracking-wide text-muted-foreground">
          {mode === "4d" ? `W${wi + 1} · L${z + 1}` : `Layer ${z + 1} / ${effectiveDepth}`}
        </div>
      )}
      <div
        className="grid gap-1.5"
        style={{
          gridTemplateColumns: `repeat(${cols}, ${cellSizePx}px)`,
          gridTemplateRows: `repeat(${rows}, ${cellSizePx}px)`,
        }}
        data-testid={`grid-board-${wi}-${z}`}
      >
        {Array.from({ length: rows * cols }).map((_, i) => {
          const y = Math.floor(i / cols);
          const x = i % cols;
          const idx = idxOf(rows, cols, effectiveDepth, x, y, z, wi);
          const cell = board[idx] ?? "";
          const isEmpty = cell === "";
          const humanCanClick =
            !vsAi || (currentPlayer === humanPlayer && !isAiThinking);
          const interactive = isEmpty && humanCanClick && !isGameOver;
          const isWinningCell = winningCellSet.has(idx);
          const isHintCell = hintIdx === idx;
          return (
            <button
              key={idx}
              type="button"
              onClick={() => handleCellClick(idx)}
              disabled={!interactive}
              aria-label={`Cell row ${y + 1}, column ${x + 1}, layer ${z + 1}, hyperslice ${wi + 1}${
                isEmpty ? "" : `, ${cell}`
              }${isHintCell ? ", suggested move" : ""}`}
              data-testid={
                mode === "4d"
                  ? `cell-${wi}-${z}-${y}-${x}`
                  : mode === "3d"
                    ? `cell-${z}-${y}-${x}`
                    : `cell-${y}-${x}`
              }
              className={[
                "flex items-center justify-center rounded-md border transition-colors",
                "font-mono font-semibold",
                isWinningCell
                  ? "border-primary bg-primary/15"
                  : isHintCell
                    ? "border-amber-500 bg-amber-400/30 ring-2 ring-amber-400 animate-pulse"
                    : "border-border bg-background",
                interactive
                  ? "hover:bg-muted active:bg-muted/80 cursor-pointer"
                  : "cursor-default",
                cell === "X" ? "text-primary" : "",
                cell === "O" ? "text-accent" : "",
              ].join(" ")}
              style={{
                fontSize: Math.max(12, Math.floor(cellSizePx * 0.45)),
              }}
            >
              {cell}
            </button>
          );
        })}
      </div>
    </div>
  );

  // Per-w sliced board + reindexed winning cells, used for the cube preview(s).
  const cubeSlices = useMemo(() => {
    if (mode === "2d") return [];
    const sliceLen = rows * cols * effectiveDepth;
    const slices: Array<{ board: CellValue[]; winning: Set<number> }> = [];
    for (let wi = 0; wi < effectiveW; wi++) {
      const start = wi * sliceLen;
      const sliceBoard = board.slice(start, start + sliceLen);
      const winning = new Set<number>();
      for (const cellIdx of winningCellSet) {
        if (cellIdx >= start && cellIdx < start + sliceLen) {
          winning.add(cellIdx - start);
        }
      }
      slices.push({ board: sliceBoard, winning });
    }
    return slices;
  }, [mode, board, rows, cols, effectiveDepth, effectiveW, winningCellSet]);

  return (
    <div className="min-h-screen w-full bg-background text-foreground">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <header className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Grid3x3 className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Grid Game</h1>
            <p className="text-sm text-muted-foreground">
              Play in 2D, 3D (up to {MAX_DEPTH} layers), or 4D (up to {MAX_W}{" "}
              hyperslices)
            </p>
          </div>
        </header>

        {/* Mode toggle */}
        <div className="mb-6 inline-flex rounded-md border border-border bg-muted p-1">
          <Button
            variant={mode === "2d" ? "default" : "ghost"}
            size="sm"
            className="gap-1.5"
            onClick={() => handleModeChange("2d")}
            data-testid="button-mode-2d"
          >
            <Square className="h-4 w-4" />
            2D
          </Button>
          <Button
            variant={mode === "3d" ? "default" : "ghost"}
            size="sm"
            className="gap-1.5"
            onClick={() => handleModeChange("3d")}
            data-testid="button-mode-3d"
          >
            <Box className="h-4 w-4" />
            3D
          </Button>
          <Button
            variant={mode === "4d" ? "default" : "ghost"}
            size="sm"
            className="gap-1.5"
            onClick={() => handleModeChange("4d")}
            data-testid="button-mode-4d"
          >
            <Layers className="h-4 w-4" />
            4D
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-[300px_1fr]">
          <Card className="h-fit p-5">
            <div className="space-y-6">
              <div className="space-y-3">
                <div className="flex items-baseline justify-between">
                  <Label htmlFor="rows-slider" className="text-sm font-medium">
                    Rows
                  </Label>
                  <span className="font-mono text-sm tabular-nums text-muted-foreground">
                    {rows}
                  </span>
                </div>
                <Slider
                  id="rows-slider"
                  min={MIN_SIZE}
                  max={MAX_SIZE}
                  step={1}
                  value={[rows]}
                  onValueChange={handleRowsChange}
                  data-testid="slider-rows"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{MIN_SIZE}</span>
                  <span>{MAX_SIZE}</span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-baseline justify-between">
                  <Label htmlFor="cols-slider" className="text-sm font-medium">
                    Columns
                  </Label>
                  <span className="font-mono text-sm tabular-nums text-muted-foreground">
                    {cols}
                  </span>
                </div>
                <Slider
                  id="cols-slider"
                  min={MIN_SIZE}
                  max={MAX_SIZE}
                  step={1}
                  value={[cols]}
                  onValueChange={handleColsChange}
                  data-testid="slider-cols"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{MIN_SIZE}</span>
                  <span>{MAX_SIZE}</span>
                </div>
              </div>

              {(mode === "3d" || mode === "4d") && (
                <div className="space-y-3">
                  <div className="flex items-baseline justify-between">
                    <Label
                      htmlFor="depth-slider"
                      className="text-sm font-medium"
                    >
                      Depth (layers)
                    </Label>
                    <span className="font-mono text-sm tabular-nums text-muted-foreground">
                      {depth}
                    </span>
                  </div>
                  <Slider
                    id="depth-slider"
                    min={MIN_DEPTH}
                    max={MAX_DEPTH}
                    step={1}
                    value={[depth]}
                    onValueChange={handleDepthChange}
                    data-testid="slider-depth"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{MIN_DEPTH}</span>
                    <span>{MAX_DEPTH}</span>
                  </div>
                </div>
              )}

              {mode === "4d" && (
                <div className="space-y-3">
                  <div className="flex items-baseline justify-between">
                    <Label htmlFor="w-slider" className="text-sm font-medium">
                      W (hyperslices)
                    </Label>
                    <span className="font-mono text-sm tabular-nums text-muted-foreground">
                      {w}
                    </span>
                  </div>
                  <Slider
                    id="w-slider"
                    min={MIN_W}
                    max={MAX_W}
                    step={1}
                    value={[w]}
                    onValueChange={handleWChange}
                    data-testid="slider-w"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{MIN_W}</span>
                    <span>{MAX_W}</span>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                <div className="flex items-baseline justify-between">
                  <Label htmlFor="win-slider" className="text-sm font-medium">
                    In a row to win
                  </Label>
                  <span className="font-mono text-sm tabular-nums text-muted-foreground">
                    {effectiveWinLen}
                  </span>
                </div>
                <Slider
                  id="win-slider"
                  min={MIN_WIN_LEN}
                  max={maxWinLen}
                  step={1}
                  value={[effectiveWinLen]}
                  onValueChange={(value) => {
                    const next = value[0] ?? MIN_WIN_LEN;
                    setWinLen(next);
                    resetState(rows, cols, effectiveDepth, effectiveW, {
                      resetScores: true,
                    });
                  }}
                  disabled={maxWinLen <= MIN_WIN_LEN}
                  data-testid="slider-win-length"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{MIN_WIN_LEN}</span>
                  <span>{maxWinLen}</span>
                </div>
              </div>

              <div className="space-y-3 rounded-md border border-border bg-muted/40 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Bot className="h-4 w-4 text-muted-foreground" />
                    <Label htmlFor="vs-ai-switch" className="text-sm font-medium">
                      Play vs AI
                    </Label>
                  </div>
                  <Switch
                    id="vs-ai-switch"
                    checked={vsAi}
                    onCheckedChange={handleToggleVsAi}
                    data-testid="switch-vs-ai"
                  />
                </div>
                {vsAi && (
                  <>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">You play as</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleSwapSides}
                        data-testid="button-swap-sides"
                        className="font-mono"
                      >
                        {humanPlayer}
                        <span className="mx-1.5 text-muted-foreground">vs</span>
                        <span className="text-muted-foreground">{aiPlayer}</span>
                      </Button>
                    </div>
                    <div className="flex items-center justify-between gap-2 text-sm">
                      <span className="text-muted-foreground">Difficulty</span>
                      <div
                        className="inline-flex overflow-hidden rounded-md border border-border"
                        role="group"
                        aria-label="AI difficulty"
                      >
                        {(["easy", "medium", "hard"] as const).map((level) => {
                          const isActive = difficulty === level;
                          return (
                            <button
                              key={level}
                              type="button"
                              onClick={() => setDifficulty(level)}
                              data-testid={`button-difficulty-${level}`}
                              aria-pressed={isActive}
                              className={[
                                "px-2.5 py-1 text-xs font-medium capitalize transition-colors",
                                "focus:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                                isActive
                                  ? "bg-primary text-primary-foreground"
                                  : "bg-background text-muted-foreground hover:bg-muted",
                              ].join(" ")}
                            >
                              {level}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={requestHint}
                      disabled={
                        isGameOver ||
                        isAiThinking ||
                        isHintLoading ||
                        currentPlayer !== humanPlayer ||
                        noEmptyCells
                      }
                      data-testid="button-hint"
                      className="w-full"
                    >
                      {isHintLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Lightbulb className="h-4 w-4" />
                      )}
                      <span className="ml-2">
                        {isHintLoading ? "Thinking…" : "Hint"}
                      </span>
                    </Button>
                  </>
                )}
              </div>

              <div className="space-y-3 rounded-md border border-border bg-muted/40 p-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Size</span>
                  <span className="font-mono tabular-nums">
                    {mode === "4d"
                      ? `${rows} × ${cols} × ${effectiveDepth} × ${effectiveW}`
                      : mode === "3d"
                        ? `${rows} × ${cols} × ${effectiveDepth}`
                        : `${rows} × ${cols}`}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Win at</span>
                  <span className="font-mono tabular-nums">
                    {effectiveWinLen} in a row
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Moves</span>
                  <span className="font-mono tabular-nums">{moveCount}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{turnLabel}</span>
                  <span
                    className={[
                      "flex items-center gap-1.5 font-mono font-semibold",
                      isGameOver && !winner
                        ? "text-muted-foreground"
                        : turnValueText === "X"
                          ? "text-primary"
                          : turnValueText === "O"
                            ? "text-accent"
                            : "text-muted-foreground",
                    ].join(" ")}
                    data-testid="text-current-player"
                  >
                    {!isGameOver &&
                      isAiThinking &&
                      currentPlayer !== humanPlayer &&
                      vsAi && <Loader2 className="h-3 w-3 animate-spin" />}
                    {turnValueText}
                  </span>
                </div>
              </div>

              {winnerBannerText && (
                <div
                  className="flex items-center gap-2 rounded-md border border-primary/30 bg-primary/10 p-3 text-sm font-medium text-primary"
                  data-testid="text-winner-banner"
                >
                  <Trophy className="h-4 w-4 shrink-0" />
                  <span>{winnerBannerText}</span>
                </div>
              )}

              {aiError && (
                <div
                  className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-xs text-destructive"
                  data-testid="text-ai-error"
                >
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{aiError}</span>
                </div>
              )}

              <div className="space-y-2 rounded-md border border-border bg-muted/40 p-3">
                <div className="flex items-center justify-between text-xs uppercase tracking-wide text-muted-foreground">
                  <span>Scoreboard</span>
                  <span className="font-mono normal-case tracking-normal">
                    {scores.X + scores.O + scores.draws} games
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div
                    className="rounded-md border border-border bg-background p-2"
                    data-testid="score-x"
                  >
                    <div className="font-mono text-xs text-primary">
                      {vsAi
                        ? humanPlayer === "X"
                          ? "You (X)"
                          : "AI (X)"
                        : "X"}
                    </div>
                    <div className="font-mono text-lg font-semibold tabular-nums text-primary">
                      {scores.X}
                    </div>
                  </div>
                  <div
                    className="rounded-md border border-border bg-background p-2"
                    data-testid="score-draws"
                  >
                    <div className="font-mono text-xs text-muted-foreground">
                      Draws
                    </div>
                    <div className="font-mono text-lg font-semibold tabular-nums text-muted-foreground">
                      {scores.draws}
                    </div>
                  </div>
                  <div
                    className="rounded-md border border-border bg-background p-2"
                    data-testid="score-o"
                  >
                    <div className="font-mono text-xs text-accent">
                      {vsAi
                        ? humanPlayer === "O"
                          ? "You (O)"
                          : "AI (O)"
                        : "O"}
                    </div>
                    <div className="font-mono text-lg font-semibold tabular-nums text-accent">
                      {scores.O}
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full text-xs text-muted-foreground"
                  onClick={handleResetScores}
                  disabled={
                    scores.X === 0 && scores.O === 0 && scores.draws === 0
                  }
                  data-testid="button-reset-scores"
                >
                  <Eraser className="mr-1.5 h-3.5 w-3.5" />
                  Reset scores
                </Button>
              </div>

              <Button
                variant="secondary"
                className="w-full"
                onClick={handleReset}
                data-testid="button-reset"
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                {isGameOver ? "New game" : "Reset board"}
              </Button>
            </div>
          </Card>

          <div className="space-y-6">
            <Card className="p-6">
              {mode === "2d" ? (
                <div className="flex items-center justify-center">
                  {renderSlice(0, 0)}
                </div>
              ) : mode === "3d" ? (
                <div className="flex flex-wrap items-start justify-center gap-6">
                  {Array.from({ length: effectiveDepth }).map((_, z) =>
                    renderSlice(z, 0),
                  )}
                </div>
              ) : (
                <div className="flex flex-col gap-6">
                  {Array.from({ length: effectiveW }).map((_, wi) => (
                    <div
                      key={`hyperslice-${wi}`}
                      className="rounded-md border border-border bg-muted/30 p-4"
                      data-testid={`hyperslice-${wi}`}
                    >
                      <div className="mb-3 flex items-center gap-2">
                        <Layers className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">
                          Hyperslice W{wi + 1} / {effectiveW}
                        </span>
                      </div>
                      <div className="flex flex-wrap items-start justify-center gap-4">
                        {Array.from({ length: effectiveDepth }).map((_, z) =>
                          renderSlice(z, wi),
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {mode === "3d" && (
              <Card className="p-3">
                <div className="mb-2 flex items-center justify-between px-2">
                  <div className="flex items-center gap-2">
                    <Box className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">3D preview</span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    drag to rotate · scroll to zoom
                  </span>
                </div>
                <div
                  className="rounded-md border border-border bg-muted/30"
                  style={{ height: 320 }}
                  data-testid="cube-preview"
                >
                  <CubePreview
                    rows={rows}
                    cols={cols}
                    depth={effectiveDepth}
                    board={cubeSlices[0]?.board ?? board}
                    winningCells={cubeSlices[0]?.winning ?? winningCellSet}
                  />
                </div>
              </Card>
            )}

            {mode === "4d" && (
              <Card className="p-3">
                <div className="mb-2 flex items-center justify-between px-2">
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">
                      3D previews · one per hyperslice
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    drag to rotate · scroll to zoom
                  </span>
                </div>
                <div
                  className="grid gap-3"
                  style={{
                    gridTemplateColumns: `repeat(${effectiveW}, minmax(0, 1fr))`,
                  }}
                  data-testid="cube-previews-row"
                >
                  {cubeSlices.map((slice, wi) => (
                    <div
                      key={`cube-${wi}`}
                      className="rounded-md border border-border bg-muted/30"
                      data-testid={`cube-preview-${wi}`}
                    >
                      <div className="border-b border-border px-2 py-1 font-mono text-xs uppercase tracking-wide text-muted-foreground">
                        W{wi + 1}
                      </div>
                      <div style={{ height: 220 }}>
                        <CubePreview
                          rows={rows}
                          cols={cols}
                          depth={effectiveDepth}
                          board={slice.board}
                          winningCells={slice.winning}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          {mode === "4d"
            ? "Each card is one 3D hyperslice; lines can run within a hyperslice or across hyperslices in any direction."
            : mode === "3d"
              ? "Click any cell across the layers to play. The 3D preview reflects every move and highlights the winning line."
              : vsAi
                ? "Your moves go through Python — edit ai/agent.py to swap in your own AI logic."
                : "Tap any cell to place a mark. Toggle “Play vs AI” to play against the Python agent."}
        </p>
      </div>
    </div>
  );
}
