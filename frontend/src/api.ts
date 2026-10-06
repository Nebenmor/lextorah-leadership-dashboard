// frontend/src/api.ts
import type { ClassSummary, Insight, Student } from "./types";

const BASE = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

// Render's free tier sleeps when idle and can take 30-60s+ to wake up.
// We retry with capped exponential backoff until a total time budget runs out (not a
// fixed attempt count), because failures during a cold start can be instant (e.g. proxy
// 502/503 or a blocked response with no CORS headers), which would burn a fixed
// retry count in a few seconds.
const RETRY_STATUS = new Set([502, 503, 504]);
const MAX_DELAY_MS = 5_000; // backoff cap: 1s, 2s, 4s, 5s, 5s, ...

interface RequestOptions {
  maxWaitMs?: number; // total time budget across all attempts
  timeoutMs?: number; // timeout per attempt
}

class HttpError extends Error {}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function request<T>(
  path: string,
  init?: RequestInit,
  { maxWaitMs = 100_000, timeoutMs = 20_000 }: RequestOptions = {}
): Promise<T> {
  const started = Date.now();
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
    const delay = Math.min(1000 * 2 ** attempt, MAX_DELAY_MS);
    if (Date.now() - started + delay >= maxWaitMs) throw new Error("API unreachable");
    await sleep(delay);
  }
}

export const getSummary = () => request<ClassSummary>("/api/class/summary");
export const getAtRisk = () => request<Student[]>("/api/students/at-risk");
export const generateInsight = (id: number, refresh = false) =>
  request<Insight>(
    `/api/students/${id}/insight${refresh ? "?refresh=true" : ""}`,
    { method: "POST" },
    { maxWaitMs: 60_000, timeoutMs: 40_000 }
  );