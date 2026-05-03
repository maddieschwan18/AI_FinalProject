import { Suspense, useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";

type CellValue = "" | "X" | "O";

interface CubePreviewProps {
  rows: number;
  cols: number;
  depth: number;
  board: CellValue[];
  winningCells: Set<number>;
}

function cellIndex(
  rows: number,
  cols: number,
  x: number,
  y: number,
  z: number,
): number {
  return z * rows * cols + y * cols + x;
}

function CubeScene({
  rows,
  cols,
  depth,
  board,
  winningCells,
}: CubePreviewProps) {
  const cellEdges = useMemo(
    () => new THREE.EdgesGeometry(new THREE.BoxGeometry(0.96, 0.96, 0.96)),
    [],
  );
  const xBarGeometry = useMemo(
    () => new THREE.BoxGeometry(0.7, 0.12, 0.12),
    [],
  );
  const oTorusGeometry = useMemo(
    () => new THREE.TorusGeometry(0.28, 0.07, 16, 32),
    [],
  );

  const offsetX = (cols - 1) / 2;
  const offsetY = (rows - 1) / 2;
  const offsetZ = (depth - 1) / 2;

  const items: React.JSX.Element[] = [];

  for (let z = 0; z < depth; z++) {
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const idx = cellIndex(rows, cols, x, y, z);
        const cell = board[idx];
        const isWin = winningCells.has(idx);
        const pos: [number, number, number] = [
          x - offsetX,
          -(y - offsetY),
          -(z - offsetZ),
        ];

        items.push(
          <lineSegments key={`frame-${x}-${y}-${z}`} position={pos}>
            <primitive object={cellEdges} attach="geometry" />
            <lineBasicMaterial
              color={isWin ? "#16a34a" : "#cbd5e1"}
              transparent
              opacity={isWin ? 1 : 0.4}
            />
          </lineSegments>,
        );

        if (cell === "X") {
          const color = isWin ? "#16a34a" : "#2563eb";
          items.push(
            <group key={`x-${x}-${y}-${z}`} position={pos}>
              <mesh rotation={[0, 0, Math.PI / 4]}>
                <primitive object={xBarGeometry} attach="geometry" />
                <meshStandardMaterial color={color} roughness={0.4} metalness={0.2} />
              </mesh>
              <mesh rotation={[0, 0, -Math.PI / 4]}>
                <primitive object={xBarGeometry} attach="geometry" />
                <meshStandardMaterial color={color} roughness={0.4} metalness={0.2} />
              </mesh>
            </group>,
          );
        } else if (cell === "O") {
          items.push(
            <mesh key={`o-${x}-${y}-${z}`} position={pos}>
              <primitive object={oTorusGeometry} attach="geometry" />
              <meshStandardMaterial
                color={isWin ? "#16a34a" : "#f97316"}
                roughness={0.4}
                metalness={0.2}
              />
            </mesh>
          );
        }
      }
    }
  }

  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 10, 7]} intensity={0.8} />
      <directionalLight position={[-5, -3, -5]} intensity={0.3} />
      <group>{items}</group>
      <OrbitControls enablePan={false} />
    </>
  );
}

export function CubePreview(props: CubePreviewProps) {
  const cameraDistance =
    Math.max(props.rows, props.cols, props.depth) * 2.2 + 2;
  return (
    <Canvas
      camera={{
        position: [cameraDistance, cameraDistance, cameraDistance],
        fov: 35,
      }}
      style={{ width: "100%", height: "100%" }}
    >
      <Suspense fallback={null}>
        <CubeScene {...props} />
      </Suspense>
    </Canvas>
  );
}
