"use client";
export function RevenueChart({ revenueByHour }: { revenueByHour: Record<string, number> }) {
  const entries = Object.entries(revenueByHour)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-12);
  const max = Math.max(...entries.map(([, v]) => v), 1);
  return (
    <div className="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
      <h3 className="text-zinc-400 text-sm mb-3 font-medium">Revenue by Hour</h3>
      <div className="flex items-end gap-1 h-32">
        {entries.map(([hour, val]) => (
          <div key={hour} className="flex-1 flex flex-col items-center gap-1">
            <div className="w-full bg-emerald-500 rounded-t transition-all duration-500"
                 style={{ height: `${(val / max) * 100}%` }} title={`$${val.toFixed(2)}`} />
            <span className="text-zinc-600 text-[8px] rotate-45 origin-left">{hour.slice(11)}</span>
          </div>
        ))}
        {entries.length === 0 && (
          <div className="text-zinc-600 text-sm w-full text-center self-center">Waiting for data…</div>
        )}
      </div>
    </div>
  );
}