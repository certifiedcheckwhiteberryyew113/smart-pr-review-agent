import { useEffect, useMemo, useState } from "react";

const STEP_ORDER = [
  "indexing",
  "reviewing",
  "bug_hunting",
  "issue_raising",
  "fixing",
  "awaiting_approval",
];

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function stepLabel(step) {
  if (step === "indexing") return "Indexing";
  if (step === "reviewing") return "Reviewing";
  if (step === "bug_hunting") return "Bug hunting";
  if (step === "issue_raising") return "Issue raising";
  if (step === "fixing") return "Fix drafting";
  if (step === "awaiting_approval") return "Awaiting approval";
  if (step === "complete") return "Complete";
  if (step === "error") return "Error";
  return step;
}

function formatDuration(ms) {
  const n = Number(ms);
  if (!Number.isFinite(n) || n < 0) return "";
  if (n < 1000) return `${n}ms`;
  const s = n / 1000;
  if (s < 60) return `${s.toFixed(1)}s`;
  const m = Math.floor(s / 60);
  const rem = Math.round(s - m * 60);
  return `${m}m ${rem}s`;
}

export function LiveFeed({ threadId, mode, onEvent, disabled }) {
  const stepsOrder = useMemo(() => STEP_ORDER, []);
  const [stepStates, setStepStates] = useState(() => {
    const initial = {};
    for (const s of STEP_ORDER) initial[s] = { status: "pending" };
    return initial;
  });
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!threadId) {
      setErrorMessage("");
      const initial = {};
      for (const s of STEP_ORDER) initial[s] = { status: "pending" };
      setStepStates(initial);
      return;
    }

    setErrorMessage("");
    const initial = {};
    for (const s of STEP_ORDER) initial[s] = { status: "pending" };
    initial.indexing = { status: "in_progress", startedAt: Date.now() };
    setStepStates(initial);

    const source = new EventSource(`/stream/${threadId}`);

    const handleEvent = (eventName, event) => {
      if (disabled) return;
      const parsed = safeJsonParse(event.data);
      const payload = parsed && parsed.data ? parsed.data : null;
      const now = Date.now();
      const nextError =
        eventName === "error" ? (payload?.message || "stream_error") : "";

      if (eventName === "error") {
        setErrorMessage(nextError);
      }

      setStepStates((prev) => {
        const copy = { ...prev };
        const target = eventName === "complete" ? null : eventName;
        if (target && copy[target]) {
          if (eventName === "awaiting_approval") {
            copy[target] = {
              ...copy[target],
              status: "done",
              finishedAt: copy[target].startedAt || now,
            };
          } else if (eventName !== "error") {
            const startedAt = copy[target].startedAt || now;
            copy[target] = {
              ...copy[target],
              status: "done",
              startedAt,
              finishedAt: now,
            };
          }
        }

        if (eventName === "complete" || eventName === "error") {
          return copy;
        }

        if (eventName === "awaiting_approval") {
          return copy;
        }

        const currentIndex = stepsOrder.indexOf(eventName);
        for (let i = currentIndex + 1; i < stepsOrder.length; i++) {
          const s = stepsOrder[i];
          if (!copy[s] || copy[s].status === "done") continue;
          if (s === "awaiting_approval") continue;
          if (copy[s].status === "pending") {
            copy[s] = { ...copy[s], status: "in_progress", startedAt: now };
          }
          break;
        }

        return copy;
      });

      if (onEvent) onEvent({ event: eventName, data: payload || {} });
      if (eventName === "complete" || eventName === "error") {
        source.close();
      }
    };

    for (const s of STEP_ORDER) {
      source.addEventListener(s, (event) => handleEvent(s, event));
    }

    source.addEventListener("complete", (event) => handleEvent("complete", event));
    source.addEventListener("error", (event) => handleEvent("error", event));

    return () => {
      source.close();
    };
  }, [threadId, disabled, mode, onEvent, stepsOrder]);

  const renderStatusIcon = (step) => {
    const st = stepStates[step]?.status;
    if (st === "in_progress") {
      return (
        <span className="inline-flex h-3 w-3 items-center justify-center">
          <span className="h-3 w-3 animate-spin rounded-full border-2 border-cyan-300 border-t-transparent" />
        </span>
      );
    }
    if (st === "done") {
      return <span className="text-green-400">OK</span>;
    }
    if (st === "error") {
      return <span className="text-red-400">X</span>;
    }
    return <span className="text-slate-500">•</span>;
  };

  const renderStepMeta = (step) => {
    const st = stepStates[step] || {};
    if (st.status !== "done") return "";
    const dur = formatDuration((st.finishedAt || 0) - (st.startedAt || st.finishedAt || 0));
    return dur ? ` (${dur})` : "";
  };

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-950 p-4">
      <header>
        <h2 className="text-lg font-semibold text-slate-100">Live timeline</h2>
        <p className="text-sm text-slate-400">
          Thread: <span className="font-mono">{threadId || "none"}</span>
        </p>
      </header>
      {errorMessage ? (
        <div className="mt-3 rounded-lg border border-red-700 bg-red-950 p-3 text-sm text-red-200">
          {errorMessage}
        </div>
      ) : null}
      <div className="mt-4 grid gap-2">
        {STEP_ORDER.map((s) => {
          const st = stepStates[s]?.status;
          return (
            <div
              key={s}
              className={[
                "flex items-center justify-between rounded-lg border px-3 py-2",
                st === "done"
                  ? "border-green-700 bg-green-950/40"
                  : st === "in_progress"
                    ? "border-cyan-700 bg-cyan-950/30"
                    : st === "error"
                      ? "border-red-700 bg-red-950/40"
                      : "border-slate-700 bg-slate-900/30",
              ].join(" ")}
            >
              <div className="flex items-center gap-2">
                {renderStatusIcon(s)}
                <div className="text-sm font-medium text-slate-100">
                  {stepLabel(s)}
                </div>
              </div>
              <div className="text-xs text-slate-400">
                {st === "done" ? renderStepMeta(s) : st === "in_progress" ? "Running" : ""}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

