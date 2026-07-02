export function FunnelChart({ funnel }: { funnel: Record<string, number> }) {
  const stages = [
    { key: "VIEWED",    label: "Viewed",    color: "bg-blue-600" },
    { key: "CARTED",    label: "Carted",    color: "bg-purple-600" },
    { key: "PURCHASED", label: "Purchased", color: "bg-emerald-600" },
  ];
  const max = Math.max(...stages.map(s => funnel[s.key] ?? 0), 1);
  return (
    <div className="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
      <h3 className="text-zinc-400 text-sm mb-3 font-medium">Conversion Funnel</h3>
      <div className="space-y-3">
        {stages.map(({ key, label, color }) => {
          const val = funnel[key] ?? 0;
          const pct = Math.round((val / max) * 100);
          return (
            <div key={key}>
              <div className="flex justify-between text-xs text-zinc-400 mb-1">
                <span>{label}</span><span>{val.toLocaleString()}</span>
              </div>
              <div className="h-4 bg-zinc-700 rounded-full overflow-hidden">
                <div className={`h-full ${color} transition-all duration-500 rounded-full`}
                     style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}