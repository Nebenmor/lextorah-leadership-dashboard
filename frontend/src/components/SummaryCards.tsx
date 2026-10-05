// frontend/src/components/SummaryCards.tsx
import type { ClassSummary } from "../types";

export default function SummaryCards({ data }: { data: ClassSummary }) {
  const cards = [
    { label: "Average score", value: `${data.avg_score}%` },
    { label: "Average attendance", value: `${data.avg_attendance}%` },
    { label: "Declining scores", value: data.declining_count },
    { label: "Attendance below 75%", value: data.low_attendance_count },
    { label: "Practice incomplete", value: data.incomplete_practice_count },
    { label: "Students at risk", value: data.at_risk_count, alert: true },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
      {cards.map((c) => (
        <div key={c.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-xs text-slate-500">{c.label}</p>
          <p className={`mt-1 text-2xl font-semibold ${c.alert ? "text-red-600" : "text-slate-900"}`}>
            {c.value}
          </p>
        </div>
      ))}
    </div>
  );
}
