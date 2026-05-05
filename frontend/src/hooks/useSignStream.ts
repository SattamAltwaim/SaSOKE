import { useCallback, useRef, useState } from "react";

export type StreamStatus =
  | "idle"
  | "loading"
  | "streaming"
  | "playing"
  | "paused"
  | "done"
  | "error";

export interface StreamError {
  code: string;
  title: string;
  message: string;
}

function describeHttpError(status: number): StreamError {
  switch (status) {
    case 502:
      return {
        code: "502",
        title: "Server Unreachable",
        message:
          "The sign language server is not responding. It may be starting up — try again in a moment.",
      };
    case 503:
      return {
        code: "503",
        title: "Service Unavailable",
        message:
          "The server is temporarily overloaded or under maintenance. Please try again shortly.",
      };
    case 504:
      return {
        code: "504",
        title: "Gateway Timeout",
        message:
          "The request timed out waiting for the server. The model may be loading — try again in a minute.",
      };
    case 404:
      return {
        code: "404",
        title: "Endpoint Not Found",
        message:
          "The generation endpoint could not be found. The tunnel URL may have changed.",
      };
    case 500:
      return {
        code: "500",
        title: "Server Error",
        message:
          "Something went wrong on the server. Please try again.",
      };
    case 429:
      return {
        code: "429",
        title: "Too Many Requests",
        message:
          "The server is busy. Please wait a few seconds and try again.",
      };
    default:
      return {
        code: String(status),
        title: `HTTP Error ${status}`,
        message: "An unexpected error occurred. Please try again.",
      };
  }
}

const SHEET_ID = "1V1YfGb5-f26pBaurrzTegERkYloJi7iNjQ7YVqaGFnE";
const SHEET_CSV_URL = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:csv`;

let cachedApiUrl: string | null = null;
let cacheTimestamp = 0;
const CACHE_TTL_MS = 5 * 60 * 1000; // re-fetch from sheet every 5 min

async function fetchApiUrlFromSheet(): Promise<string | null> {
  const now = Date.now();
  if (cachedApiUrl && now - cacheTimestamp < CACHE_TTL_MS) return cachedApiUrl;

  try {
    const resp = await fetch(SHEET_CSV_URL);
    if (!resp.ok) throw new Error(`Sheet fetch failed: ${resp.status}`);
    const csv = await resp.text();

    const rows = csv
      .trim()
      .split("\n")
      .map((row) =>
        row.split(",").map((cell) => cell.replace(/^"|"$/g, "").trim()),
      )
      .filter((cols) => cols[0] && cols[1]);

    if (rows.length === 0) return null;

    // Sort by timestamp (column B) descending to get the latest entry
    rows.sort((a, b) => new Date(b[1]).getTime() - new Date(a[1]).getTime());

    cachedApiUrl = rows[0][0];
    cacheTimestamp = now;
    console.log(`[tunnel] resolved API URL: ${cachedApiUrl}`);
    return cachedApiUrl;
  } catch (err) {
    console.error("[tunnel] failed to fetch URL from Google Sheet:", err);
    return cachedApiUrl; // fall back to stale cache if available
  }
}

function b64ToFloat32(b64: string): Float32Array {
  const bin = atob(b64);
  const buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return new Float32Array(buf.buffer);
}

export function useSignStream() {
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [error, setError] = useState<StreamError | null>(null);
  const [totalFrames, setTotalFrames] = useState(0);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [fps, setFps] = useState(30);
  const [paused, setPaused] = useState(false);

  const framesRef = useRef<Float32Array[]>([]);
  const playRef = useRef<number | null>(null);
  const frameIndexRef = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const streamDoneRef = useRef(false);

  const fail = useCallback((err: StreamError) => {
    setError(err);
    setStatus("error");
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    setStatus("idle");
  }, []);

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
    async (text: string, langToken: string, mode: string) => {
      stopPlayback();
      framesRef.current = [];
      frameIndexRef.current = 0;
      streamDoneRef.current = false;
      setPaused(false);
      setCurrentFrame(0);
      setTotalFrames(0);
      setStatus("loading");

      setError(null);

      const apiUrl = await fetchApiUrlFromSheet();
      if (!apiUrl) {
        fail({
          code: "CONFIG",
          title: "No Server Configured",
          message:
            "Could not fetch the server URL. Check that the Google Sheet has a valid tunnel link.",
        });
        return;
      }

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const resp = await fetch(apiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, lang_token: langToken, mode: mode }),
          signal: controller.signal,
        });

        if (!resp.ok || !resp.body) {
          if (!resp.ok) {
            fail(describeHttpError(resp.status));
          } else {
            fail({
              code: "EMPTY",
              title: "Empty Response",
              message: "The server returned an empty response. Please try again.",
            });
          }
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
        if ((err as Error).name === "AbortError") return;
        console.error("Stream error:", err);

        const msg = (err as Error).message || "";
        if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
          fail({
            code: "NETWORK",
            title: "Connection Failed",
            message:
              "Could not reach the server. The tunnel may be down — check your connection and try again.",
          });
        } else {
          fail({
            code: "STREAM",
            title: "Stream Interrupted",
            message:
              "The connection was lost while receiving data. Please try again.",
          });
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
    error,
    clearError,
    totalFrames,
    fps,
    paused,
    togglePause,
    replay,
    changeFps,
  };
}
