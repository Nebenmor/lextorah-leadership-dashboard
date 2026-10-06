// frontend/src/App.tsx
import { useEffect, useState } from "react";
import { generateInsight, getAtRisk, getSummary } from "./api";
import AtRiskTable from "./components/AtRiskTable";
import InsightCard from "./components/InsightCard";
import LoadingSkeleton from "./components/LoadingSkeleton";
import StudentPanel from "./components/StudentPanel";
import SummaryCards from "./components/SummaryCards";
import type { ClassSummary, Insight, Student } from "./types";

export default function App() {
  const [summary, setSummary] = useState<ClassSummary | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [insight, setInsight] = useState<Insight | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getSummary(), getAtRisk()])
      .then(([s, list]) => {
        setSummary(s);
        setStudents(list);
        if (list.length) setSelectedId(list[0].id); // auto-select the highest-risk student
      })
      .catch(() =>
        setLoadError(
          "Could not reach the API. The server may still be starting.",
        ),
      );
  }, []);

  const selected = students.find((s) => s.id === selectedId) ?? null;

  function select(id: number) {
    setSelectedId(id);
    setInsight(null);
    setError(null);
  }

  async function handleGenerate() {
    if (!selected) return;
    setLoading(true);
    setError(null);
    try {
      setInsight(await generateInsight(selected.id, insight !== null));
    } catch {
      setError("Could not generate the insight. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (loadError)
    return (
      <div className="p-8">
        <p className="text-red-700">{loadError}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-3 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
        >
          Try again
        </button>
      </div>
    );
  if (!summary) return <LoadingSkeleton />;

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Leadership Dashboard</h1>
        <p className="text-sm text-slate-500">
          {summary.school_name} · {summary.class_name} ·{" "}
          {summary.total_students} students
        </p>
      </header>
      <main className="mx-auto max-w-6xl space-y-4 p-6">
        <SummaryCards data={summary} />
        <div className="grid gap-4 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <AtRiskTable
              students={students}
              selectedId={selectedId}
              onSelect={select}
            />
          </div>
          <div className="space-y-4 lg:col-span-3">
            {selected && (
              <>
                <StudentPanel student={selected} />
                <InsightCard
                  studentName={selected.name}
                  insight={insight}
                  loading={loading}
                  error={error}
                  onGenerate={handleGenerate}
                />
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
