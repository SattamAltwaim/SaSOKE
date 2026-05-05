import { useState, useEffect } from "react";
import Scene from "./components/Scene";
import InputBar from "./components/InputBar";
import { useSignStream } from "./hooks/useSignStream";

const FPS_OPTIONS = [10, 15, 20, 25, 30];

export default function App() {
  const {
    send,
    frames,
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
  } = useSignStream();

  const [errorVisible, setErrorVisible] = useState(false);

  useEffect(() => {
    if (error) {
      setErrorVisible(true);
    }
  }, [error]);

  const dismissError = () => {
    setErrorVisible(false);
    setTimeout(clearError, 300);
  };

  const [showFpsMenu, setShowFpsMenu] = useState(false);

  const showControls = status === "done" || status === "paused";

  return (
    <div className="relative w-full h-full">
      <Scene frames={frames} currentFrame={currentFrame} />

      {/* Top-left controls — visible when done or paused */}
      {showControls && (
        <div
          style={{
            position: "fixed",
            top: "24px",
            left: "24px",
            zIndex: 20,
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          {/* Replay button */}
          <button
            onClick={replay}
            title="Replay"
            style={{
              width: "44px",
              height: "44px",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(32,33,35,0.7)",
              backdropFilter: "blur(20px)",
              WebkitBackdropFilter: "blur(20px)",
              color: "rgba(255,255,255,0.8)",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.12)";
              e.currentTarget.style.color = "#fff";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(32,33,35,0.7)";
              e.currentTarget.style.color = "rgba(255,255,255,0.8)";
            }}
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="1 4 1 10 7 10" />
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
            </svg>
          </button>

          {/* FPS selector */}
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setShowFpsMenu((p) => !p)}
              title="Playback speed"
              style={{
                height: "44px",
                borderRadius: "22px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "6px",
                padding: "0 16px",
                border: "1px solid rgba(255,255,255,0.1)",
                background: "rgba(32,33,35,0.7)",
                backdropFilter: "blur(20px)",
                WebkitBackdropFilter: "blur(20px)",
                color: "rgba(255,255,255,0.8)",
                cursor: "pointer",
                transition: "all 0.2s ease",
                fontSize: "13px",
                fontWeight: 500,
                fontFamily: "inherit",
                letterSpacing: "0.01em",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(255,255,255,0.12)";
                e.currentTarget.style.color = "#fff";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(32,33,35,0.7)";
                e.currentTarget.style.color = "rgba(255,255,255,0.8)";
              }}
            >
              <span>{fps} FPS</span>
              <svg
                width="10"
                height="10"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>

            {showFpsMenu && (
              <div
                style={{
                  position: "absolute",
                  top: "52px",
                  left: 0,
                  background: "rgba(32,33,35,0.9)",
                  backdropFilter: "blur(20px)",
                  WebkitBackdropFilter: "blur(20px)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "14px",
                  padding: "6px",
                  minWidth: "90px",
                  boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
                }}
              >
                {FPS_OPTIONS.map((f) => (
                  <button
                    key={f}
                    onClick={() => {
                      changeFps(f);
                      setShowFpsMenu(false);
                    }}
                    style={{
                      display: "block",
                      width: "100%",
                      padding: "8px 14px",
                      borderRadius: "10px",
                      border: "none",
                      background:
                        f === fps ? "rgba(255,255,255,0.1)" : "transparent",
                      color:
                        f === fps
                          ? "rgba(255,255,255,0.95)"
                          : "rgba(255,255,255,0.5)",
                      fontSize: "13px",
                      fontWeight: 500,
                      fontFamily: "inherit",
                      cursor: "pointer",
                      textAlign: "left",
                      transition: "all 0.15s ease",
                    }}
                    onMouseEnter={(e) => {
                      if (f !== fps)
                        e.currentTarget.style.background =
                          "rgba(255,255,255,0.06)";
                    }}
                    onMouseLeave={(e) => {
                      if (f !== fps)
                        e.currentTarget.style.background = "transparent";
                    }}
                  >
                    {f} FPS
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Frame counter */}
          <span
            style={{
              fontSize: "12px",
              color: "rgba(255,255,255,0.3)",
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {currentFrame + 1} / {totalFrames}
          </span>
        </div>
      )}

      {/* Status pill — only during loading/streaming */}
      {(status === "loading" || status === "streaming") && (
        <div
          style={{
            position: "fixed",
            top: "24px",
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 10,
          }}
        >
          <div
            style={{
              fontSize: "11px",
              color: "rgba(255,255,255,0.3)",
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              padding: "6px 14px",
              borderRadius: "20px",
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.06)",
              backdropFilter: "blur(16px)",
              WebkitBackdropFilter: "blur(16px)",
            }}
          >
            {status === "loading" ? "Generating..." : "Receiving frames..."}
          </div>
        </div>
      )}

      {/* Error toast */}
      {error && (
        <div
          style={{
            position: "fixed",
            bottom: "140px",
            left: "50%",
            transform: `translateX(-50%) translateY(${errorVisible ? "0" : "20px"})`,
            zIndex: 30,
            width: "100%",
            maxWidth: "480px",
            padding: "0 20px",
            boxSizing: "border-box",
            opacity: errorVisible ? 1 : 0,
            transition: "all 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
            pointerEvents: errorVisible ? "auto" : "none",
          }}
        >
          <div
            style={{
              background: "rgba(40, 20, 20, 0.85)",
              backdropFilter: "blur(24px)",
              WebkitBackdropFilter: "blur(24px)",
              border: "1px solid rgba(255, 80, 80, 0.2)",
              borderRadius: "16px",
              padding: "16px 20px",
              boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
              display: "flex",
              alignItems: "flex-start",
              gap: "14px",
            }}
          >
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: "rgba(255, 80, 80, 0.12)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 700,
                  color: "rgba(255, 120, 100, 0.9)",
                  fontFamily: "monospace",
                  letterSpacing: "-0.02em",
                }}
              >
                {error.code}
              </span>
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <div
                style={{
                  fontSize: "14px",
                  fontWeight: 600,
                  color: "rgba(255, 200, 190, 0.95)",
                  marginBottom: "4px",
                }}
              >
                {error.title}
              </div>
              <div
                style={{
                  fontSize: "13px",
                  lineHeight: "1.5",
                  color: "rgba(255, 180, 170, 0.6)",
                }}
              >
                {error.message}
              </div>
            </div>

            <button
              onClick={dismissError}
              style={{
                width: "28px",
                height: "28px",
                borderRadius: "8px",
                border: "none",
                background: "transparent",
                color: "rgba(255, 180, 170, 0.4)",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                transition: "all 0.15s ease",
                padding: 0,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(255,255,255,0.06)";
                e.currentTarget.style.color = "rgba(255, 180, 170, 0.8)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "transparent";
                e.currentTarget.style.color = "rgba(255, 180, 170, 0.4)";
              }}
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
              >
                <path d="M18 6L6 18" />
                <path d="M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <InputBar
        onSend={send}
        onTogglePause={togglePause}
        status={status}
        paused={paused}
      />
    </div>
  );
}
