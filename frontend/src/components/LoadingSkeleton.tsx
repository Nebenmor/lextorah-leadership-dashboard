// frontend/src/components/LoadingSkeleton.tsx
// Shown instantly while the API wakes up (Render free tier), so the page never looks empty.
export default function LoadingSkeleton() {
  const block = "animate-pulse rounded bg-slate-200";
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Leadership Dashboard</h1>
        <div className={`mt-2 h-4 w-56 ${block}`} />
      </header>
      <main className="mx-auto max-w-6xl space-y-4 p-6">
        <div
          role="status"
          className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
        >
          Waking up the server (free hosting). This can take up to a minute, and
          the data will appear automatically.
        </div>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div className={`h-3 w-20 ${block}`} />
              <div className={`mt-3 h-7 w-14 ${block}`} />
            </div>
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-5">
          <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:col-span-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className={`h-10 w-full ${block}`} />
            ))}
          </div>
          <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:col-span-3">
            <div className={`h-6 w-40 ${block}`} />
            <div className={`h-40 w-full ${block}`} />
          </div>
        </div>
      </main>
    </div>
  );
}
