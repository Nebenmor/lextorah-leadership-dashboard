// frontend/src/risk.ts
import type { RiskLevel } from "./types";

export const BADGE: Record<RiskLevel, string> = {
  high: "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-green-100 text-green-700",
};
