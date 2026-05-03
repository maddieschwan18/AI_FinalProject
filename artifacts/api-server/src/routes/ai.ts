import { Router, type IRouter } from "express";
import { spawn } from "node:child_process";
import path from "node:path";
import { GetAiMoveBody, GetAiMoveResponse } from "@workspace/api-zod";

const router: IRouter = Router();

// In dev and production, this file is bundled into artifacts/api-server/dist/,
// so going up three directories lands at the workspace root.
const REPO_ROOT = path.resolve(import.meta.dirname, "..", "..", "..");
const AI_SCRIPT = path.join(REPO_ROOT, "ai", "agent.py");
const PYTHON_BIN = process.env["PYTHON_BIN"] ?? "python3";
const TIMEOUT_MS = 10_000;

interface PythonResult {
  stdout: string;
  stderr: string;
  code: number | null;
  timedOut: boolean;
}

function runPython(input: string): Promise<PythonResult> {
  return new Promise((resolve) => {
    const child = spawn(PYTHON_BIN, [AI_SCRIPT], {
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGKILL");
    }, TIMEOUT_MS);

    child.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });

    child.on("error", (err) => {
      clearTimeout(timer);
      resolve({
        stdout,
        stderr: stderr + String(err),
        code: -1,
        timedOut,
      });
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      resolve({ stdout, stderr, code, timedOut });
    });

    child.stdin.write(input);
    child.stdin.end();
  });
}

router.post("/ai/move", async (req, res): Promise<void> => {
  const parsed = GetAiMoveBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const body = parsed.data;
  const depth = body.depth ?? 1;
  const w = body.w ?? 1;
  const winLen = body.winLen ?? 3;
  const difficulty = body.difficulty ?? "hard";
  const expectedLen = body.rows * body.cols * depth * w;

  const noEmpty = body.board.every((c) => c !== "");
  if (body.board.length !== expectedLen) {
    res.status(400).json({
      error: `Board length must equal rows * cols * depth * w (${expectedLen}).`,
    });
    return;
  }
  if (noEmpty) {
    res.status(400).json({ error: "No empty cells remain on the board." });
    return;
  }

  // Always send `depth`, `w`, `win_len`, and `difficulty` to the Python agent
  // so it can rely on them.
  const result = await runPython(
    JSON.stringify({ ...body, depth, w, win_len: winLen, difficulty }),
  );

  if (result.timedOut) {
    req.log.error({ stderr: result.stderr }, "AI agent timed out");
    res.status(500).json({ error: "AI agent timed out." });
    return;
  }

  let parsedOut: unknown;
  try {
    parsedOut = JSON.parse(result.stdout);
  } catch {
    req.log.error(
      { code: result.code, stdout: result.stdout, stderr: result.stderr },
      "AI agent produced non-JSON output",
    );
    res
      .status(500)
      .json({ error: "AI agent produced invalid JSON output." });
    return;
  }

  if (result.code !== 0) {
    const message =
      parsedOut &&
      typeof parsedOut === "object" &&
      "error" in parsedOut &&
      typeof (parsedOut as { error: unknown }).error === "string"
        ? (parsedOut as { error: string }).error
        : `AI agent exited with code ${result.code}`;
    req.log.error({ stderr: result.stderr }, "AI agent failed");
    res.status(500).json({ error: message });
    return;
  }

  const response = GetAiMoveResponse.safeParse(parsedOut);
  if (!response.success) {
    req.log.error(
      { stdout: result.stdout },
      "AI agent response failed schema validation",
    );
    res.status(500).json({ error: "AI agent returned invalid move shape." });
    return;
  }

  const { row, col } = response.data;
  const z = response.data.z ?? 0;
  const wOut = response.data.w ?? 0;
  if (row >= body.rows || col >= body.cols || z >= depth || wOut >= w) {
    res.status(500).json({
      error: `AI returned out-of-bounds move (row=${row}, col=${col}, z=${z}, w=${wOut}).`,
    });
    return;
  }
  const idx =
    wOut * (body.rows * body.cols * depth) +
    z * (body.rows * body.cols) +
    row * body.cols +
    col;
  if (body.board[idx] !== "") {
    res.status(500).json({
      error: `AI tried to play on occupied cell (row=${row}, col=${col}, z=${z}, w=${wOut}).`,
    });
    return;
  }

  res.json({ row, col, z, w: wOut });
});

export default router;
