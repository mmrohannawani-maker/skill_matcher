import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { Developer, Skill, SavedSearch, TeamMember, UserRole } from "@/mockData/types";
import { mockSavedSearches, mockTeamMembers } from "@/mockData/data";

interface AppContextType {
  role: UserRole;
  setRole: (role: UserRole) => void;
  developers: Developer[];
  setDevelopers: React.Dispatch<React.SetStateAction<Developer[]>>;
  skills: Skill[];
  setSkills: React.Dispatch<React.SetStateAction<Skill[]>>;
  savedSearches: SavedSearch[];
  setSavedSearches: React.Dispatch<React.SetStateAction<SavedSearch[]>>;
  teamMembers: TeamMember[];
  setTeamMembers: React.Dispatch<React.SetStateAction<TeamMember[]>>;
  isLoading: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [role, setRole] = useState<UserRole>("Admin");
  const [isLoading, setIsLoading] = useState(true);
  const [developers, setDevelopers] = useState<Developer[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>(mockSavedSearches);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>(mockTeamMembers);

  useEffect(() => {
    const fetchDatabaseData = async () => {
      setIsLoading(true);
      console.log("[APP CONTEXT] Initiating fetch from backend...");

      try {
        // Fetch Developers
        const devResponse = await fetch("http://localhost:8000/developers");
        if (devResponse.ok) {
          const devData = await devResponse.json();
          
          // [LOGGING ADDED HERE]
          console.log("[APP CONTEXT] RAW DEVELOPER DATA RECEIVED:", devData);
          if (devData.length > 0) {
            console.log("[APP CONTEXT] Example Developer Skill Structure:", devData[0].skills);
          }

          setDevelopers(devData);
        } else {
          console.error("[APP CONTEXT] Developer fetch failed with status:", devResponse.status);
        }

        // Fetch Skills
        const skillResponse = await fetch("http://localhost:8000/skills");
        if (skillResponse.ok) {
          const skillData = await skillResponse.json();
          
          // [LOGGING ADDED HERE]
          console.log("[APP CONTEXT] RAW SKILLS DATA RECEIVED:", skillData);
          
          setSkills(skillData);
        } else {
          console.error("[APP CONTEXT] Skills fetch failed with status:", skillResponse.status);
        }
      } catch (error) {
        console.error("[APP CONTEXT] Connection to backend failed completely:", error);
      } finally {
        setIsLoading(false);
        console.log("[APP CONTEXT] Fetch cycle complete. isLoading set to false.");
      }
    };

    fetchDatabaseData();
  }, []);

  return (
    <AppContext.Provider 
      value={{ 
        role, setRole, 
        developers, setDevelopers, 
        skills, setSkills, 
        savedSearches, setSavedSearches, 
        teamMembers, setTeamMembers,
        isLoading 
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppProvider");
  return ctx;
};