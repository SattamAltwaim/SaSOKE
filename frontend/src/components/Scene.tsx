import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import SignModel from "./SignModel";

interface Props {
  frames: React.MutableRefObject<Float32Array[]>;
  currentFrame: number;
}

function Lighting() {
  return (
    <>
      <directionalLight position={[3, 4, 5]} intensity={1.8} color="#fff5ee" />
      <directionalLight position={[-4, 2, 3]} intensity={0.6} color="#e8eeff" />
      <directionalLight position={[0, 3, -5]} intensity={0.8} color="#ffffff" />
      <ambientLight intensity={0.15} />
    </>
  );
}

export default function Scene({ frames, currentFrame }: Props) {
  return (
    <Canvas
      gl={{ antialias: true, alpha: false }}
      camera={{ position: [0, 0, 3], fov: 35, near: 0.01, far: 100 }}
      onCreated={({ gl }) => {
        gl.setClearColor("#000000");
        gl.toneMapping = 3;
        gl.toneMappingExposure = 1.1;
      }}
      style={{ position: "absolute", inset: 0 }}
    >
      <Lighting />
      <SignModel frames={frames} currentFrame={currentFrame} />
      <OrbitControls
        enablePan={false}
        enableZoom={true}
        minDistance={0.5}
        maxDistance={8}
        target={[0, 0, 0]}
        enableDamping
        dampingFactor={0.08}
      />
    </Canvas>
  );
}
