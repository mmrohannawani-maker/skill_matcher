import { useState, useMemo } from "react";
import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { SkillLevelBar } from "@/components/StatusBadges";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

export default function SkillsPage() {
  const { skills, developers, isLoading } = useAppContext();
  const [searchTerm, setSearchTerm] = useState("");

  if (isLoading || !skills || !developers) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading skills data...</p>
        </div>
      </DashboardLayout>
    );
  }

  // Calculate the stats for all skills
  const skillStats = useMemo(() => {
    return skills.map((skill) => {
      const devs = developers.filter((d) => 
        d.skills?.some((s) => s.skill_id === Number(skill.id))
      );

      const avgLevel = devs.length
        ? devs.reduce((a, d) => {
            const s = d.skills?.find((s) => s.skill_id === Number(skill.id));
            return a + (s?.proficiency_level || 0);
          }, 0) / devs.length
        : 0;

      return { 
        ...skill, 
        devCount: devs.length, 
        avgLevel: Math.round(avgLevel * 10) / 10 
      };
    });
  }, [skills, developers]);

  // [NEW] Filter the skills based on the search bar
  const filteredSkills = useMemo(() => {
    const lowerSearch = searchTerm.toLowerCase().trim();
    if (!lowerSearch) return skillStats;
    
    // Only searches the skill_name as requested
    return skillStats.filter((s) => s.skill_name.toLowerCase().includes(lowerSearch));
  }, [skillStats, searchTerm]);

  // [MODIFIED] Extract categories ONLY from the filtered results so empty categories disappear
  const categories = Array.from(new Set(filteredSkills.map((s) => s.category || "Uncategorized")));

  return (
    <DashboardLayout>
      <div className="page-header flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="page-title">Skills Overview</h1>
          <p className="page-subtitle">Browse all skills and their availability across the team</p>
        </div>
        
        {/* [NEW] Search Bar */}
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search skills (e.g. mvc, core)..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 bg-card shadow-sm"
          />
        </div>
      </div>

      {categories.length > 0 ? (
        categories.map((cat) => (
          <div key={cat} className="mb-6">
            <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider mb-3">{cat}</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredSkills.filter((s) => (s.category || "Uncategorized") === cat).map((s) => (
                <div key={s.id} className="bg-card rounded-lg border p-4 flex items-center justify-between hover:shadow-sm transition-shadow">
                  <div>
                    <span className="font-medium text-sm capitalize">{s.skill_name}</span>
                    <p className="text-xs text-muted-foreground mt-0.5">{s.devCount} developer{s.devCount !== 1 ? "s" : ""}</p>
                  </div>
                  <div className="text-right">
                    <SkillLevelBar level={Math.round(s.avgLevel)} />
                    <p className="text-xs text-muted-foreground mt-1">avg {s.avgLevel}/5</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))
      ) : (
        // [NEW] Fallback message when a search yields no results
        <div className="text-center py-20 bg-muted/20 rounded-xl border-2 border-dashed">
          <Search className="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-muted-foreground">No skills found matching "{searchTerm}"</p>
        </div>
      )}
    </DashboardLayout>
  );
}