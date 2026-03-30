export function DiffViewer({ fixPatch }) {
  const diff = fixPatch?.diff ? String(fixPatch.diff) : "";
  const filesChanged = Array.isArray(fixPatch?.files_changed)
    ? fixPatch.files_changed
    : [];
  const testOutput = fixPatch?.test_output ? String(fixPatch.test_output) : "";

  if (!diff.trim()) {
    return (
      <section className="rounded-xl border border-slate-700 bg-slate-950 p-4">
        <h2 className="text-lg font-semibold text-slate-100">Proposed fix</h2>
        <p className="mt-2 text-sm text-slate-400">
          No fix patch has been generated yet.
        </p>
      </section>
    );
  }

  const lines = diff.split("\n");
  const renderLine = (line, idx) => {
    if (line.startsWith("+") && !line.startsWith("+++")) {
      return (
        <div key={idx} className="font-mono text-xs text-green-300">
          {line}
        </div>
      );
    }
    if (line.startsWith("-") && !line.startsWith("---")) {
      return (
        <div key={idx} className="font-mono text-xs text-red-300">
          {line}
        </div>
      );
    }
    return (
      <div key={idx} className="font-mono text-xs text-slate-200">
        {line}
      </div>
    );
  };

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-950 p-4">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">
            Proposed fix diff
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Files changed: {filesChanged.length ? filesChanged.join(", ") : "none"}
          </p>
        </div>
      </header>
      <div className="mt-4 rounded-lg border border-slate-800 bg-slate-900 p-3">
        <div className="max-h-[420px] overflow-auto">
          {lines.map((l, i) => renderLine(l, i))}
        </div>
      </div>
      {testOutput ? (
        <div className="mt-4">
          <h3 className="text-sm font-semibold text-slate-100">Test output</h3>
          <pre className="mt-2 max-h-[240px] overflow-auto rounded-lg border border-slate-800 bg-slate-900 p-3 font-mono text-xs text-slate-200 whitespace-pre-wrap">
            {testOutput}
          </pre>
        </div>
      ) : null}
    </section>
  );
}

