// import { Developer, Skill, SavedSearch, TeamMember } from "./types";

// export const mockSkills: Skill[] = [
//   { id: "1", name: "React", category: "Frontend" },
//   { id: "2", name: "TypeScript", category: "Frontend" },
//   { id: "3", name: "Node.js", category: "Backend" },
//   { id: "4", name: "Python", category: "Backend" },
//   { id: "5", name: "AWS", category: "Cloud" },
//   { id: "6", name: "Docker", category: "DevOps" },
//   { id: "7", name: "PostgreSQL", category: "Database" },
//   { id: "8", name: "MongoDB", category: "Database" },
//   { id: "9", name: "Java", category: "Backend" },
//   { id: "10", name: "Angular", category: "Frontend" },
//   { id: "11", name: "Vue.js", category: "Frontend" },
//   { id: "12", name: "Kubernetes", category: "DevOps" },
//   { id: "13", name: "GraphQL", category: "Backend" },
//   { id: "14", name: "Redis", category: "Database" },
//   { id: "15", name: ".NET", category: "Backend" },
//   { id: "16", name: "Azure", category: "Cloud" },
//   { id: "17", name: "Go", category: "Backend" },
//   { id: "18", name: "Terraform", category: "DevOps" },
// ];

// export const mockDevelopers: Developer[] = [
//   {
//     id: "1", name: "Arun Sharma", email: "arun.sharma@company.com",
//     department: "Engineering", role: "Senior Developer", status: "Active",
//     availability: "Available",
//     skills: [
//       { technology: "React", skillLevel: 5, yearsExperience: 6, lastUsedYear: 2026, certification: "Meta React Certified" },
//       { technology: "TypeScript", skillLevel: 5, yearsExperience: 5, lastUsedYear: 2026, certification: "" },
//       { technology: "Node.js", skillLevel: 4, yearsExperience: 4, lastUsedYear: 2025, certification: "" },
//       { technology: "AWS", skillLevel: 3, yearsExperience: 3, lastUsedYear: 2026, certification: "AWS Solutions Architect" },
//     ],
//   },
//   {
//     id: "2", name: "Priya Patel", email: "priya.patel@company.com",
//     department: "Engineering", role: "Lead Developer", status: "Active",
//     availability: "On Project",
//     skills: [
//       { technology: "Python", skillLevel: 5, yearsExperience: 8, lastUsedYear: 2026, certification: "" },
//       { technology: "AWS", skillLevel: 5, yearsExperience: 6, lastUsedYear: 2026, certification: "AWS DevOps Professional" },
//       { technology: "Docker", skillLevel: 4, yearsExperience: 5, lastUsedYear: 2026, certification: "" },
//       { technology: "Kubernetes", skillLevel: 4, yearsExperience: 4, lastUsedYear: 2025, certification: "CKA" },
//       { technology: "Terraform", skillLevel: 3, yearsExperience: 3, lastUsedYear: 2025, certification: "" },
//     ],
//   },
//   {
//     id: "3", name: "Rahul Gupta", email: "rahul.gupta@company.com",
//     department: "Engineering", role: "Developer", status: "Active",
//     availability: "Available",
//     skills: [
//       { technology: "Java", skillLevel: 4, yearsExperience: 5, lastUsedYear: 2026, certification: "Oracle Java SE" },
//       { technology: "PostgreSQL", skillLevel: 4, yearsExperience: 5, lastUsedYear: 2026, certification: "" },
//       { technology: ".NET", skillLevel: 3, yearsExperience: 3, lastUsedYear: 2024, certification: "" },
//       { technology: "Angular", skillLevel: 3, yearsExperience: 3, lastUsedYear: 2025, certification: "" },
//     ],
//   },
//   {
//     id: "4", name: "Sneha Reddy", email: "sneha.reddy@company.com",
//     department: "Engineering", role: "Senior Developer", status: "Active",
//     availability: "Available",
//     skills: [
//       { technology: "React", skillLevel: 4, yearsExperience: 4, lastUsedYear: 2026, certification: "" },
//       { technology: "Vue.js", skillLevel: 5, yearsExperience: 5, lastUsedYear: 2026, certification: "" },
//       { technology: "TypeScript", skillLevel: 4, yearsExperience: 4, lastUsedYear: 2026, certification: "" },
//       { technology: "GraphQL", skillLevel: 4, yearsExperience: 3, lastUsedYear: 2025, certification: "" },
//       { technology: "MongoDB", skillLevel: 3, yearsExperience: 3, lastUsedYear: 2025, certification: "" },
//     ],
//   },
//   {
//     id: "5", name: "Vikram Singh", email: "vikram.singh@company.com",
//     department: "Engineering", role: "Developer", status: "Active",
//     availability: "Busy",
//     skills: [
//       { technology: "Go", skillLevel: 4, yearsExperience: 4, lastUsedYear: 2026, certification: "" },
//       { technology: "Docker", skillLevel: 5, yearsExperience: 5, lastUsedYear: 2026, certification: "" },
//       { technology: "Kubernetes", skillLevel: 5, yearsExperience: 4, lastUsedYear: 2026, certification: "CKA, CKAD" },
//       { technology: "AWS", skillLevel: 4, yearsExperience: 4, lastUsedYear: 2026, certification: "" },
//       { technology: "Terraform", skillLevel: 4, yearsExperience: 3, lastUsedYear: 2026, certification: "Terraform Associate" },
//     ],
//   },
//   {
//     id: "6", name: "Meera Joshi", email: "meera.joshi@company.com",
//     department: "Engineering", role: "Senior Developer", status: "Active",
//     availability: "Available",
//     skills: [
//       { technology: "React", skillLevel: 5, yearsExperience: 7, lastUsedYear: 2026, certification: "" },
//       { technology: "TypeScript", skillLevel: 5, yearsExperience: 6, lastUsedYear: 2026, certification: "" },
//       { technology: "Node.js", skillLevel: 5, yearsExperience: 7, lastUsedYear: 2026, certification: "" },
//       { technology: "PostgreSQL", skillLevel: 4, yearsExperience: 5, lastUsedYear: 2026, certification: "" },
//       { technology: "Redis", skillLevel: 3, yearsExperience: 3, lastUsedYear: 2025, certification: "" },
//     ],
//   },
//   {
//     id: "7", name: "Karthik Nair", email: "karthik.nair@company.com",
//     department: "Engineering", role: "Developer", status: "Active",
//     availability: "On Project",
//     skills: [
//       { technology: "Angular", skillLevel: 5, yearsExperience: 6, lastUsedYear: 2026, certification: "" },
//       { technology: "TypeScript", skillLevel: 4, yearsExperience: 5, lastUsedYear: 2026, certification: "" },
//       { technology: "Java", skillLevel: 4, yearsExperience: 5, lastUsedYear: 2025, certification: "" },
//       { technology: ".NET", skillLevel: 3, yearsExperience: 3, lastUsedYear: 2024, certification: "" },
//     ],
//   },
//   {
//     id: "8", name: "Anita Desai", email: "anita.desai@company.com",
//     department: "Engineering", role: "Lead Developer", status: "Active",
//     availability: "Available",
//     skills: [
//       { technology: "Python", skillLevel: 5, yearsExperience: 9, lastUsedYear: 2026, certification: "" },
//       { technology: "PostgreSQL", skillLevel: 5, yearsExperience: 8, lastUsedYear: 2026, certification: "" },
//       { technology: "AWS", skillLevel: 4, yearsExperience: 5, lastUsedYear: 2026, certification: "AWS Solutions Architect Professional" },
//       { technology: "Docker", skillLevel: 3, yearsExperience: 4, lastUsedYear: 2025, certification: "" },
//       { technology: "Redis", skillLevel: 4, yearsExperience: 4, lastUsedYear: 2026, certification: "" },
//     ],
//   },
//   {
//     id: "9", name: "Rohan Kumar", email: "rohan.kumar@company.com",
//     department: "Engineering", role: "Developer", status: "Active",
//     availability: "Busy",
//     skills: [
//       { technology: "React", skillLevel: 3, yearsExperience: 2, lastUsedYear: 2026, certification: "" },
//       { technology: "TypeScript", skillLevel: 3, yearsExperience: 2, lastUsedYear: 2026, certification: "" },
//       { technology: "MongoDB", skillLevel: 4, yearsExperience: 3, lastUsedYear: 2025, certification: "MongoDB Certified Developer" },
//       { technology: "Node.js", skillLevel: 3, yearsExperience: 2, lastUsedYear: 2025, certification: "" },
//     ],
//   },
//   {
//     id: "10", name: "Divya Menon", email: "divya.menon@company.com",
//     department: "Engineering", role: "Senior Developer", status: "Active",
//     availability: "Available",
//     skills: [
//       { technology: "Azure", skillLevel: 5, yearsExperience: 6, lastUsedYear: 2026, certification: "Azure Solutions Architect Expert" },
//       { technology: ".NET", skillLevel: 5, yearsExperience: 7, lastUsedYear: 2026, certification: "" },
//       { technology: "TypeScript", skillLevel: 4, yearsExperience: 4, lastUsedYear: 2026, certification: "" },
//       { technology: "React", skillLevel: 3, yearsExperience: 3, lastUsedYear: 2025, certification: "" },
//       { technology: "PostgreSQL", skillLevel: 4, yearsExperience: 5, lastUsedYear: 2026, certification: "" },
//     ],
//   },
// ];

// export const mockTeamMembers: TeamMember[] = [
//   { id: "1", name: "Arun Sharma", email: "arun.sharma@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "2", name: "Priya Patel", email: "priya.patel@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "3", name: "Rahul Gupta", email: "rahul.gupta@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "4", name: "Sneha Reddy", email: "sneha.reddy@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "5", name: "Vikram Singh", email: "vikram.singh@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "6", name: "Meera Joshi", email: "meera.joshi@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "7", name: "Karthik Nair", email: "karthik.nair@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "8", name: "Anita Desai", email: "anita.desai@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "9", name: "Rohan Kumar", email: "rohan.kumar@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "10", name: "Divya Menon", email: "divya.menon@company.com", role: "Developer", department: "Engineering", status: "Active" },
//   { id: "11", name: "Rajesh Admin", email: "rajesh.admin@company.com", role: "Admin", department: "Management", status: "Active" },
//   { id: "12", name: "Sita Sales", email: "sita.sales@company.com", role: "Sales", department: "Sales", status: "Active" },
// ];

// export const mockSavedSearches: SavedSearch[] = [
//   { id: "1", name: "React + Node.js Senior", date: "2026-02-28", keywords: ["React", "Node.js", "TypeScript"], resultsCount: 4 },
//   { id: "2", name: "AWS DevOps Engineer", date: "2026-02-25", keywords: ["AWS", "Docker", "Kubernetes", "Terraform"], resultsCount: 3 },
//   { id: "3", name: "Full Stack Python", date: "2026-02-20", keywords: ["Python", "PostgreSQL", "AWS"], resultsCount: 2 },
// ];


import { Developer, Skill, SavedSearch, TeamMember } from "./types";

// [MODIFIED] Set to empty so the app uses your Database data instead
export const mockDevelopers: Developer[] = [];
export const mockSkills: Skill[] = [];

// Keep these if you haven't built the backend for them yet
export const mockSavedSearches: SavedSearch[] = [];
export const mockTeamMembers: TeamMember[] = [];