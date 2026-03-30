import { useMemo, useState } from "react";
import PRInput from "./components/PRInput.jsx";
import { LiveFeed } from "./components/LiveFeed.jsx";
import { DiffViewer } from "./components/DiffViewer.jsx";
import { ApprovePanel } from "./components/ApprovePanel.jsx";

const EMPTY_FIX_PATCH = {
  diff: "",
  files_changed: [],
  test_output: "",
  co_authored_by: "",
};

export default function App() {
  const [threadId, setThreadId] = useState("");
  const [mode, setMode] = useState("review_only");
  const [currentStep, setCurrentStep] = useState("");
  const [workflowResult, setWorkflowResult] = useState({
    approval_status: "",
    fix_patch: EMPTY_FIX_PATCH,
  });
  const [awaitingApproval, setAwaitingApproval] = useState(false);
  const [error, setError] = useState("");

  const showApproval = useMemo(() => mode === "human_in_loop", [mode]);

  const handleStart = ({ threadId: nextThreadId, mode: nextMode }) => {
    setThreadId(nextThreadId);
    setMode(nextMode);
    setCurrentStep("");
    setAwaitingApproval(false);
    setError("");
    setWorkflowResult({ approval_status: "", fix_patch: EMPTY_FIX_PATCH });
  };

  const onEvent = ({ event, data }) => {
    setCurrentStep(event);
    if (event === "awaiting_approval") {
      setAwaitingApproval(true);
      setError("");
      return;
    }
    if (event === "error") {
      setAwaitingApproval(false);
      setError(data?.message ? String(data.message) : "workflow_error");
      return;
    }
    if (event === "fixing") {
      if (data?.fix_patch) {
        setWorkflowResult((prev) => ({
          ...prev,
          fix_patch: data.fix_patch,
        }));
      }
      setAwaitingApproval(false);
      return;
    }
    if (event === "complete") {
      setAwaitingApproval(false);
      setError("");
      setWorkflowResult({
        approval_status: data?.approval_status ? String(data.approval_status) : "",
        fix_patch: data?.fix_patch || EMPTY_FIX_PATCH,
      });
      return;
    }
    if (event === "reviewing" || event === "bug_hunting" || event === "issue_raising" || event === "indexing") {
      setError("");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl p-6">
        <header className="mb-6">
          <h1 className="text-2xl font-bold">Smart PR Review Agent</h1>
          <p className="mt-1 text-sm text-slate-400">
            Stream agent progress, optionally pause for approval, and view drafted diffs.
          </p>
        </header>

        {error ? (
          <div className="mb-4 rounded-lg border border-red-800 bg-red-950/40 p-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        <div className="grid gap-4 lg:grid-cols-2">
          <PRInput
            disabled={false}
            mode={mode}
            onModeChange={setMode}
            onStart={handleStart}
          />
          <LiveFeed threadId={threadId} mode={mode} onEvent={onEvent} disabled={false} />
        </div>

        {showApproval ? (
          <div className="mt-4">
            <ApprovePanel
              visible={awaitingApproval}
              threadId={threadId}
              disabled={false}
              busy={false}
              mode={mode}
              onUpdate={(next) => {
                setWorkflowResult((prev) => ({
                  ...prev,
                  approval_status: next.approval_status ? String(next.approval_status) : prev.approval_status,
                  fix_patch: next.fix_patch || prev.fix_patch,
                }));
              }}
            />
          </div>
        ) : null}

        {workflowResult?.fix_patch?.diff ? (
          <div className="mt-4">
            <DiffViewer fixPatch={workflowResult.fix_patch} />
          </div>
        ) : null}

        <div className="mt-6 text-xs text-slate-500">
          Current step: <span className="font-mono">{currentStep || "none"}</span>
        </div>
      </div>
    </div>
  );
}
