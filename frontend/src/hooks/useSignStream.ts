import { useCallback, useRef, useState } from "react";

export type StreamStatus =
  | "idle"
  | "loading"
  | "streaming"
  | "playing"
  | "paused"
  | "done";

const API_URL = import.meta.env.VITE_API_URL as string | undefined;

function b64ToFloat32(b64: string): Float32Array {
  const bin = atob(b64);
  const buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return new Float32Array(buf.buffer);
}

export function useSignStream() {
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [totalFrames, setTotalFrames] = useState(0);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [fps, setFps] = useState(30);
  const [paused, setPaused] = useState(false);

  const framesRef = useRef<Float32Array[]>([]);
  const playRef = useRef<number | null>(null);
  const frameIndexRef = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const streamDoneRef = useRef(false);

  const stopPlayback = useCallback(() => {
    if (playRef.current !== null) {
      clearInterval(playRef.current);
      playRef.current = null;
    }
  }, []);

  const startPlayback = useCallback(
    (fpsVal: number, fromFrame = 0) => {
      stopPlayback();
      frameIndexRef.current = fromFrame;
      const interval = 1000 / fpsVal;

      playRef.current = window.setInterval(() => {
        const buf = framesRef.current;
        const i = frameIndexRef.current;

        if (i < buf.length) {
          setCurrentFrame(i);
          frameIndexRef.current = i + 1;
        } else if (streamDoneRef.current) {
          stopPlayback();
          setStatus("done");
        }
      }, interval);
    },
    [stopPlayback],
  );

  const togglePause = useCallback(() => {
    setPaused((prev) => {
      if (prev) {
        startPlayback(fps, frameIndexRef.current);
        setStatus("playing");
        return false;
      } else {
        stopPlayback();
        setStatus("paused");
        return true;
      }
    });
  }, [fps, startPlayback, stopPlayback]);

  const replay = useCallback(() => {
    streamDoneRef.current = true;
    setPaused(false);
    setStatus("playing");
    frameIndexRef.current = 0;
    setCurrentFrame(0);
    startPlayback(fps, 0);
  }, [fps, startPlayback]);

  const changeFps = useCallback(
    (newFps: number) => {
      setFps(newFps);
      if (status === "playing") {
        startPlayback(newFps, frameIndexRef.current);
      }
    },
    [status, startPlayback],
  );

  const send = useCallback(
    async (text: string, langToken: string) => {
      if (!API_URL) {
        console.error("VITE_API_URL not set");
        return;
      }

      stopPlayback();
      framesRef.current = [];
      frameIndexRef.current = 0;
      streamDoneRef.current = false;
      setPaused(false);
      setCurrentFrame(0);
      setTotalFrames(0);
      setStatus("loading");

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const resp = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, lang_token: langToken }),
          signal: controller.signal,
        });

        if (!resp.ok || !resp.body) {
          setStatus("idle");
          return;
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let playbackStarted = false;
        let streamFps = 30;
        let eventType = "";

        setStatus("streaming");

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              eventType = line.slice(7).trim();
            } else if (line.startsWith("data: ") && eventType) {
              try {
                const data = JSON.parse(line.slice(6));

                if (eventType === "metadata") {
                  setTotalFrames(data.total_frames);
                  streamFps = data.fps ?? 20;
                  setFps(streamFps);
                  console.log(
                    `[SSE] metadata: ${data.total_frames} frames @ ${streamFps} fps`,
                  );
                } else if (eventType === "frame") {
                  // Binary mode: base64-encoded Float32Array
                  if (data.v) {
                    framesRef.current.push(b64ToFloat32(data.v));
                  } else if (data.vertices) {
                    // Fallback: JSON array mode (backward compat)
                    const verts = data.vertices as number[][];
                    const flat = new Float32Array(verts.length * 3);
                    for (let vi = 0; vi < verts.length; vi++) {
                      flat[vi * 3] = verts[vi][0];
                      flat[vi * 3 + 1] = verts[vi][1];
                      flat[vi * 3 + 2] = verts[vi][2];
                    }
                    framesRef.current.push(flat);
                  }

                  if (framesRef.current.length % 20 === 0) {
                    console.log(
                      `[SSE] buffered ${framesRef.current.length} frames`,
                    );
                  }

                  if (!playbackStarted && framesRef.current.length >= 2) {
                    playbackStarted = true;
                    console.log("[SSE] starting playback");
                    setStatus("playing");
                    startPlayback(streamFps, 0);
                  }
                } else if (eventType === "done") {
                  streamDoneRef.current = true;
                  console.log(
                    `[SSE] done, ${framesRef.current.length} frames`,
                  );
                }
              } catch (parseErr) {
                console.warn("[SSE] parse error:", parseErr);
              }
              eventType = "";
            }
          }
        }

        streamDoneRef.current = true;
        console.log(
          `[SSE] reader finished, ${framesRef.current.length} frames`,
        );
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          console.error("Stream error:", err);
          setStatus("idle");
        }
      }
    },
    [startPlayback, stopPlayback],
  );

  return {
    send,
    frames: framesRef,
    currentFrame,
    status,
    totalFrames,
    fps,
    paused,
    togglePause,
    replay,
    changeFps,
  };
}
