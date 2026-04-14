import { useEffect, useMemo, useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface Props {
  frames: React.MutableRefObject<Float32Array[]>;
  currentFrame: number;
}

const VERT_COUNT = 10_475;
const FLOATS = VERT_COUNT * 3;

export default function SignModel({ frames, currentFrame }: Props) {
  const geoRef = useRef<THREE.BufferGeometry>(null);
  const currentFrameRef = useRef(0);
  const lastAppliedRef = useRef(-1);
  const [ready, setReady] = useState(false);

  // Interpolation buffers — lerp between frameA and frameB
  const interpBuf = useRef(new Float32Array(FLOATS));

  const geometry = useMemo(() => new THREE.BufferGeometry(), []);

  currentFrameRef.current = currentFrame;

  useEffect(() => {
    geoRef.current = geometry;

    Promise.all([
      fetch("/smplx_faces.bin").then((r) => r.arrayBuffer()),
      fetch("/smplx_tpose.bin").then((r) => r.arrayBuffer()),
    ]).then(([facesBuf, tposeBuf]) => {
      const faces = new Uint32Array(facesBuf);
      const tpose = new Float32Array(tposeBuf);

      geometry.setIndex(new THREE.BufferAttribute(faces, 1));
      geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(new Float32Array(tpose), 3),
      );
      geometry.computeVertexNormals();
      geometry.computeBoundingSphere();
      setReady(true);
    });

    return () => geometry.dispose();
  }, [geometry]);

  useFrame(() => {
    if (!ready || !geoRef.current) return;

    const frame = currentFrameRef.current;
    const buf = frames.current;
    const cur = buf[frame];
    if (!cur) return;

    const posAttr = geoRef.current.getAttribute("position") as THREE.BufferAttribute;
    const arr = posAttr.array as Float32Array;
    if (arr.length !== FLOATS) return;

    const next = buf[frame + 1];

    if (next) {
      // Lerp between current frame and next for sub-frame smoothness.
      // Factor 0.35 gives a gentle blend toward the next pose each
      // render tick (~60fps), creating fluid motion between 20fps keyframes.
      const out = interpBuf.current;
      const t = 0.35;
      for (let i = 0; i < FLOATS; i++) {
        out[i] = arr[i] + (cur[i] + (next[i] - cur[i]) * t - arr[i]) * 0.5;
      }
      arr.set(out);
    } else if (frame !== lastAppliedRef.current) {
      // No next frame available — snap to current
      arr.set(cur);
      lastAppliedRef.current = frame;
    } else {
      return;
    }

    posAttr.needsUpdate = true;
    geoRef.current.computeVertexNormals();
  });

  if (!ready) return null;

  return (
    <mesh geometry={geometry}>
      <meshPhysicalMaterial
        color="#c8a08a"
        roughness={0.55}
        metalness={0.02}
        clearcoat={0.05}
        clearcoatRoughness={0.4}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}
