// frontend/src/api.ts
import type { ClassSummary, Insight, Student } from "./types";

const BASE = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

// Render's free tier sleeps when idle and can take ~30-60s to wake up.
// We retry on network errors, timeouts and gateway errors (502/503/504),
// with exponential backoff (1s, 2s, 4s, 8s) and a timeout per attempt.
const RETRY_STATUS = new Set([502, 503, 504]);

interface RequestOptions {
  retries?: number;
  timeoutMs?: number;
}

class HttpError extends Error {}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function request<T>(
  path: string,
  init?: RequestInit,
  { retries = 4, timeoutMs = 20000 }: RequestOptions = {}
): Promise<T> {
  for (let attempt = 0; ; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(`${BASE}${path}`, { ...init, signal: controller.signal });
      if (res.ok) return (await res.json()) as T;
      if (!RETRY_STATUS.has(res.status)) throw new HttpError(`Request failed (${res.status})`);
    } catch (err) {
      if (err instanceof HttpError) throw err; // real error (404, 500...): do not retry
    } finally {
      clearTimeout(timer);
    }
    if (attempt >= retries) throw new Error("API unreachable");
    await sleep(1000 * 2 ** attempt);
  }
}

export const getSummary = () => request<ClassSummary>("/api/class/summary");
export const getAtRisk = () => request<Student[]>("/api/students/at-risk");
export const generateInsight = (id: number, refresh = false) =>
  request<Insight>(
    `/api/students/${id}/insight${refresh ? "?refresh=true" : ""}`,
    { method: "POST" },
    { retries: 2, timeoutMs: 40000 }
  );