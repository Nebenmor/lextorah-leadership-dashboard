// frontend/src/components/AtRiskTable.tsx
import { BADGE } from "../risk";
import type { Student } from "../types";

interface Props {
  students: Student[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}

export default function AtRiskTable({ students, selectedId, onSelect }: Props) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <h2 className="border-b border-slate-200 px-4 py-3 font-semibold">Students needing attention</h2>
      <ul className="divide-y divide-slate-100">
        {students.map((s) => (
          <li key={s.id}>
            <button
              onClick={() => onSelect(s.id)}
              className={`flex w-full items-center justify-between px-4 py-3 text-left hover:bg-slate-50 ${
                s.id === selectedId ? "bg-indigo-50" : ""
              }`}
            >
              <span>
                <span className="block font-medium">{s.name}</span>
                <span className="text-xs text-slate-500">
                  {s.attendance}% attendance · latest score {s.latest_score}%
                </span>
              </span>
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${BADGE[s.risk_level]}`}>
                {s.risk_level} · {s.risk_score}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
