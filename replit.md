# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

## Artifacts

- **grid-game** (`artifacts/grid-game`) — React + Vite frontend at `/`. A configurable grid game supporting **2D** (rows × cols, each 2..10), **3D** (rows × cols × depth, depth 2..6), and **4D** (rows × cols × depth × W, W 2..4) modes. 2D uses a single click-to-play board; 3D uses a row of stacked slices plus a rotatable Three.js cube preview (`src/components/cube-preview.tsx`, built with React Three Fiber + drei); 4D nests this — each "hyperslice" card holds a row of 3D slices, with one mini cube preview per hyperslice below. Includes "Play vs AI" mode, configurable win-length, scoreboard tracking, and winning-line highlighting that spans layers and hyperslices.

## Python AI agent

- `ai/agent.py` — entry point for the Python AI agent. Reads a JSON request on stdin, writes a `{ "row", "col", "z", "w" }` JSON response on stdout. Supports 2D (`depth: 1, w: 1`), 3D (`depth > 1`), and 4D (`w > 1`) boards. The board is a flat array of length `rows*cols*depth*w`, indexed as `idx = w*(rows*cols*depth) + z*(rows*cols) + y*cols + x`. The default implementation picks a random empty cell. Replace the body of `get_move(request)` with your own logic; the surrounding I/O wiring, validation, and error reporting are already in place.
- `artifacts/api-server/src/routes/ai.ts` — Express route at `POST /api/ai/move` that spawns Python (`python3` by default; override via `PYTHON_BIN` env var), with a 10s timeout and validation against the OpenAPI-generated Zod schemas. The `depth` and `w` fields on the request are optional (default to 1 for backward compatibility).
- Win detection on the frontend uses a generic 4D direction enumerator that produces (3^4 − 1) / 2 = 40 line directions, automatically collapsing to 13 in 3D and 4 in 2D when the corresponding dimension is 1.

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
