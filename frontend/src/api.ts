// frontend/src/api.ts
import type { ClassSummary, Insight, Student } from "./types";

const BASE = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return res.json() as Promise<T>;
}

export const getSummary = () => request<ClassSummary>("/api/class/summary");
export const getAtRisk = () => request<Student[]>("/api/students/at-risk");
export const generateInsight = (id: number, refresh = false) =>
  request<Insight>(`/api/students/${id}/insight${refresh ? "?refresh=true" : ""}`, {
    method: "POST",
  });
