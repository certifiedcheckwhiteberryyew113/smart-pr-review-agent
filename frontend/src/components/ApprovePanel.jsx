import { useState } from "react";

export function ApprovePanel({
  visible,
  threadId,
  disabled,
  busy,
  onUpdate,
}) {
  const [message, setMessage] = useState("");
  const [fault, setFault] = useState("");

  const postDecision = async (approved) => {
    if (!threadId || disabled || busy) {
      return;
    }
    setFault("");
    setMessage("");
    const response = await fetch("/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ thread_id: threadId, approved }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload?.detail || payload?.message || response.statusText;
      setFault(String(detail));
      return;
    }
    const next = {
      approval_status: payload.approval_status,
      fix_patch: payload.fix_patch,
    };
    setMessage(`Decision recorded: ${payload.approval_status}`);
    if (onUpdate) onUpdate(next);
  };

  if (!visible) {
    return null;
  }

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-950 p-4">
      <header>
        <h2 className="text-lg font-semibold text-slate-100">
          Human approval
        </h2>
        <p className="mt-1 text-sm text-slate-400">
          Confirm whether to proceed with applying the drafted fix.
        </p>
      </header>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-600"
          disabled={disabled || busy || !threadId}
          onClick={() => postDecision(true)}
        >
          Approve
        </button>
        <button
          type="button"
          className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-slate-50 disabled:bg-slate-600"
          disabled={disabled || busy || !threadId}
          onClick={() => postDecision(false)}
        >
          Reject
        </button>
      </div>
      {fault ? (
        <p className="mt-3 text-sm text-red-300">{fault}</p>
      ) : null}
      {message ? (
        <pre className="mt-3 whitespace-pre-wrap rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm text-slate-200 font-mono">
          {message}
        </pre>
      ) : null}
    </section>
  );
}

