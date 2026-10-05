// frontend/src/components/StudentPanel.tsx
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Student } from "../types";
import { BADGE } from "../risk";

export default function StudentPanel({ student }: { student: Student }) {
  const trend = student.recent_scores.map((score, i) => ({ test: `Test ${i + 1}`, score }));
  const metrics = [
    { label: "Attendance", value: student.attendance },
    { label: "Practice", value: student.practice_completion },
    { label: "Speaking", value: student.speaking },
    { label: "Listening", value: student.listening },
  ];
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{student.name}</h2>
          <p className="text-sm text-slate-500">{student.class_name}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${BADGE[student.risk_level]}`}>
          {student.risk_level} risk · {student.risk_score}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {metrics.map((m) => (
          <div key={m.label} className="rounded-lg bg-slate-50 p-3">
            <p className="text-xs text-slate-500">{m.label}</p>
            <p className={`text-xl font-semibold ${m.value < 50 ? "text-red-600" : ""}`}>{m.value}%</p>
          </div>
        ))}
      </div>

      <div className="mt-4 h-44">
        <p className="mb-1 text-xs text-slate-500">Recent assessment scores</p>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trend} margin={{ top: 5, right: 10, bottom: 15, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="test" fontSize={12} />
            <YAxis domain={[0, 100]} fontSize={12} />
            <Tooltip />
            <Line type="monotone" dataKey="score" stroke="#4f46e5" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 flex flex-wrap gap-2">
        {student.flags.map((f) => (
          <span key={f} className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700">
            {f}
          </span>
        ))}
      </div>
    </div>
  );
}
