import { useState, useMemo } from "react";
// [NEW] Added useNavigate for the Back button
import { useNavigate } from "react-router-dom";
import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { AvailabilityBadge, SkillLevelBar } from "@/components/StatusBadges";
// [MODIFIED] Added ArrowLeft for the Back button
import { Search, Users, Code2, ArrowLeft } from "lucide-react";

export default function SkillsSearchPage() {
  const { developers, skills: masterSkills, isLoading } = useAppContext();
  const [searchTerm, setSearchTerm] = useState("");
  // [NEW] Hook to handle routing back to the dashboard
  const navigate = useNavigate();

  // --- [LOGIC] Grouping Developers by Skill ---
  const skillsWithDevs = useMemo(() => {
    if (!developers || !masterSkills) return [];

    return masterSkills.map((skill) => {
      // Find all developers who have this specific skill_id in their skills array
      const matchingDevs = developers.filter((dev) =>
        dev.skills?.some((s) => Number(s.skill_id) === Number(skill.id))
      ).map(dev => {
        // Find the specific proficiency the dev has for THIS skill
        const skillInfo = dev.skills?.find(s => Number(s.skill_id) === Number(skill.id));
        return {
          ...dev,
          proficiency: skillInfo?.proficiency_level || 0,
          exp: Math.floor((skillInfo?.proficiency_level || 0) * 1.6) // Using your realistic exp math
        };
      });

      return {
        ...skill,
        developers: matchingDevs,
        count: matchingDevs.length
      };
    }).sort((a, b) => b.count - a.count); // Show most common skills first
  }, [developers, masterSkills]);

  // --- [FILTER] Search through the grouped skills ---
  const filteredSkills = useMemo(() => {
    return skillsWithDevs.filter((s) =>
      s.skill_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.category?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [skillsWithDevs, searchTerm]);

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Mapping talent to skills...</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      {/* [NEW] Back to Dashboard Button */}
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate("/")} 
          className="pl-0 text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
      </div>

      <div className="page-header">
        <h1 className="page-title">Skill Discovery</h1>
        <p className="page-subtitle">Search for a specific technology to see available experts</p>
      </div>

      <div className="relative mb-8 max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <Input 
          placeholder="Search for a skill (e.g. React, Python)..." 
          value={searchTerm} 
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10 h-11 bg-card shadow-sm"
        />
      </div>

      <div className="grid grid-cols-1 gap-6">
        {filteredSkills.length > 0 ? (
          filteredSkills.map((skill) => (
            <div key={skill.id} className="bg-card rounded-xl border shadow-sm overflow-hidden">
              {/* Skill Header */}
              <div className="bg-muted/30 px-6 py-4 border-b flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Code2 className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold capitalize">{skill.skill_name}</h3>
                    <span className="text-xs text-muted-foreground bg-white px-2 py-0.5 rounded border">
                      {skill.category || "Uncategorized"}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-primary font-semibold">
                    <Users className="h-4 w-4" />
                    <span>{skill.count} Experts</span>
                  </div>
                </div>
              </div>

              {/* Developers List for this Skill */}
              <div className="p-0">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-muted-foreground border-b text-xs uppercase tracking-wider">
                      <th className="text-left py-3 px-6 font-medium">Expert Name</th>
                      <th className="text-left py-3 px-6 font-medium">Proficiency</th>
                      <th className="text-left py-3 px-6 font-medium">Exp in Skill</th>
                      <th className="text-left py-3 px-6 font-medium">Availability</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {skill.developers.map((dev) => (
                      <tr key={dev.id} className="hover:bg-muted/20 transition-colors">
                        <td className="py-4 px-6 font-medium">{dev.name}</td>
                        <td className="py-4 px-6">
                          <SkillLevelBar level={dev.proficiency} />
                        </td>
                        <td className="py-4 px-6 text-muted-foreground">{dev.exp} yrs</td>
                        <td className="py-4 px-6">
                          <AvailabilityBadge status={dev.availability ? "Available" : "Busy"} />
                        </td>
                      </tr>
                    ))}
                    {skill.developers.length === 0 && (
                      <tr>
                        <td colSpan={4} className="py-6 text-center text-muted-foreground">
                          No developers currently have this skill mapped.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-20 bg-muted/20 rounded-xl border-2 border-dashed">
            <p className="text-muted-foreground">No skills found matching "{searchTerm}"</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}