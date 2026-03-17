export interface DeveloperSkill {
  // [MODIFIED] Matches backend SQLAlchemy columns
  skill_id: number;
  proficiency_level: number;
  years_of_experience: number;
  last_used_year: number;
  certification: string;
}

export interface Developer {
  id: string;
  name: string;
  email: string;
  department: string;
  // [MODIFIED] Matches backend 'current_role'
  current_role: string;
  status: string;
  availability: boolean; // Backend uses Boolean
  skills: DeveloperSkill[];
  // [NEW] Added to fix the TypeScript error on the Dashboard
  years_of_experience?: number; 
}

export interface Skill {
  id: string;
  // [MODIFIED] Matches backend 'skill_name'
  skill_name: string;
  category: string;
}

export interface SavedSearch {
  id: string;
  name: string;
  date: string;
  keywords: string[];
  resultsCount: number;
}

export interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  status: string;
}

export type UserRole = "Admin" | "Developer" | "Sales";

export interface JDMatchResult {
  developer: Developer;
  matchedSkills: string[];
  matchScore: number;
}