import {
  useRef,
  useState,
  useCallback,
  useEffect,
  type FormEvent,
  type KeyboardEvent,
} from "react";
import type { StreamStatus } from "../hooks/useSignStream";

const LANGUAGES = [
  { value: "isharah", label: "AR" },
  { value: "how2sign", label: "EN" },
  { value: "csl", label: "ZH" },
  { value: "phoenix", label: "DE" },
] as const;

interface Props {
  onSend: (text: string, langToken: string) => void;
  onTogglePause: () => void;
  status: StreamStatus;
  paused: boolean;
}

export default function InputBar({
  onSend,
  onTogglePause,
  status,
  paused,
}: Props) {
  const [text, setText] = useState("");
  const [lang, setLang] = useState("isharah");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isPlaying = status === "playing" || status === "streaming";
  const isLoading = status === "loading";
  const canSend = text.trim().length > 0 && !isLoading && !isPlaying;

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "0";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }, [text]);

  const handleSubmit = useCallback(
    (e?: FormEvent) => {
      e?.preventDefault();
      if (isPlaying || status === "paused") {
        onTogglePause();
        return;
      }
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;
      onSend(trimmed, lang);
    },
    [text, lang, isLoading, isPlaying, status, onSend, onTogglePause],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit],
  );

  const isArabic = lang === "isharah";

  const showPause = isPlaying && !paused;
  const showPlay = status === "paused" || paused;
  const btnActive = canSend || isPlaying || showPlay;

  return (
    <div
      style={{
        position: "fixed",
        bottom: "32px",
        left: "50%",
        transform: "translateX(-50%)",
        width: "100%",
        maxWidth: "680px",
        padding: "0 20px",
        zIndex: 10,
        boxSizing: "border-box",
      }}
    >
      <form onSubmit={handleSubmit}>
        <div
          style={{
            background: "rgba(32, 33, 35, 0.7)",
            backdropFilter: "blur(24px)",
            WebkitBackdropFilter: "blur(24px)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: "24px",
            boxShadow:
              "0 0 0 1px rgba(255,255,255,0.03), 0 12px 48px rgba(0,0,0,0.5)",
          }}
        >
          <div style={{ padding: "20px 24px 12px 24px" }}>
            <textarea
              ref={textareaRef}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                isArabic
                  ? "اكتب جملة لترجمتها..."
                  : "Type a sentence to translate..."
              }
              rows={1}
              dir="auto"
              style={{
                width: "100%",
                background: "transparent",
                color: "rgba(255,255,255,0.92)",
                fontSize: "16px",
                lineHeight: "1.6",
                resize: "none",
                outline: "none",
                border: "none",
                padding: 0,
                margin: 0,
                minHeight: "26px",
                maxHeight: "200px",
                fontFamily: "inherit",
              }}
            />
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "4px 16px 16px 20px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "2px",
                background: "rgba(255,255,255,0.04)",
                borderRadius: "12px",
                padding: "3px",
              }}
            >
              {LANGUAGES.map((l) => {
                const active = lang === l.value;
                return (
                  <button
                    key={l.value}
                    type="button"
                    onClick={() => setLang(l.value)}
                    style={{
                      padding: "6px 14px",
                      borderRadius: "10px",
                      fontSize: "13px",
                      fontWeight: 500,
                      letterSpacing: "0.02em",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      border: "none",
                      background: active
                        ? "rgba(255,255,255,0.12)"
                        : "transparent",
                      color: active
                        ? "rgba(255,255,255,0.95)"
                        : "rgba(255,255,255,0.3)",
                    }}
                    onMouseEnter={(e) => {
                      if (!active)
                        e.currentTarget.style.color = "rgba(255,255,255,0.55)";
                    }}
                    onMouseLeave={(e) => {
                      if (!active)
                        e.currentTarget.style.color = "rgba(255,255,255,0.3)";
                    }}
                  >
                    {l.label}
                  </button>
                );
              })}
            </div>

            {/* Action button: send / pause / play / loading */}
            <button
              type="submit"
              disabled={!btnActive && !isLoading}
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: "none",
                cursor: btnActive ? "pointer" : "default",
                transition: "all 0.2s ease",
                background: btnActive ? "#fff" : "rgba(255,255,255,0.08)",
                color: btnActive ? "#000" : "rgba(255,255,255,0.15)",
                flexShrink: 0,
              }}
            >
              {isLoading ? (
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  style={{ animation: "spin 0.8s linear infinite" }}
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeDasharray="31.4"
                    strokeDashoffset="10"
                    strokeLinecap="round"
                  />
                </svg>
              ) : showPause ? (
                /* Pause icon */
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16" rx="1" />
                  <rect x="14" y="4" width="4" height="16" rx="1" />
                </svg>
              ) : showPlay ? (
                /* Play icon */
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z" />
                </svg>
              ) : (
                /* Send arrow */
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M12 19V5" />
                  <path d="m5 12 7-7 7 7" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </form>

      <p
        style={{
          textAlign: "center",
          fontSize: "12px",
          color: "rgba(255,255,255,0.18)",
          marginTop: "12px",
        }}
      >
        SaSOKE generates sign language from text
      </p>
    </div>
  );
}
