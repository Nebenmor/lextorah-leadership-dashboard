// frontend/src/types.ts
export type RiskLevel = "high" | "medium" | "low";

export interface ClassSummary {
  school_name: string;
  class_name: string;
  total_students: number;
  avg_score: number;
  avg_attendance: number;
  declining_count: number;
  low_attendance_count: number;
  incomplete_practice_count: number;
  at_risk_count: number;
}

export interface Student {
  id: number;
  name: string;
  class_name: string;
  attendance: number;
  practice_completion: number;
  speaking: number;
  listening: number;
  recent_scores: number[];
  latest_score: number;
  risk_score: number;
  risk_level: RiskLevel;
  flags: string[];
  weak_skills: string[];
}

export interface Insight {
  student_id: number;
  student_name: string;
  risk_level: RiskLevel;
  risk_score: number;
  why: string;
  primary_concern: string;
  recommended_action: string;
  source: "ai" | "fallback";
  cached: boolean;
}
