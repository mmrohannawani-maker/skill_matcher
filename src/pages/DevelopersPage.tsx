import { useState, useMemo } from "react";
import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AvailabilityBadge, SkillLevelBar } from "@/components/StatusBadges";
import { Search, Mail, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

const PAGE_SIZE = 8;

export default function DevelopersPage() {
  const { developers, skills, isLoading } = useAppContext();
  const [search, setSearch] = useState("");
  const [techFilter, setTechFilter] = useState("all");
  const [availFilter, setAvailFilter] = useState("all");
  const [page, setPage] = useState(0);

  // Helper function to translate ID to Name
  const getSkillName = (skillId: number | string) => {
    if (!skills || skills.length === 0) return `Skill ${skillId}`;
    const foundSkill = skills.find(s => Number(s.id) === Number(skillId));
    return foundSkill ? foundSkill.skill_name : `Skill ${skillId}`;
  };

  const allTechs = useMemo(() => {
    if (!developers) return [];
    const uniqueIds = new Set(developers.flatMap((d) => d.skills?.map((s) => s.skill_id.toString()) || []));
    
    return Array.from(uniqueIds)
      .map(id => ({ id, name: getSkillName(id) }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [developers, skills]);

  const filtered = useMemo(() => {
    if (!developers) return [];
    const lowerSearch = search.toLowerCase().trim();

    return developers.filter((d) => {
      // 1. Check ONLY if the name matches
      const matchName = d.name.toLowerCase().includes(lowerSearch);
      
      const matchSearch = lowerSearch === "" || matchName;
      
      const matchTech = 
        techFilter === "all" || 
        d.skills?.some((s) => s.skill_id.toString() === techFilter);
      
      let matchAvail = true;
      if (availFilter === "Available") matchAvail = d.availability === true;
      else if (availFilter === "Busy") matchAvail = d.availability === false;
      
      return matchSearch && matchTech && matchAvail;
    });
  }, [developers, skills, search, techFilter, availFilter]);

  // Loading State to prevent UI crashes
  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Syncing with database...</p>
        </div>
      </DashboardLayout>
    );
  }

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paged = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1 className="page-title">Developers Directory</h1>
        <p className="page-subtitle">Browse and filter the developer pool</p>
      </div>

      <div className="bg-card rounded-lg border p-4 mb-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search developer name..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} className="pl-9 h-9 bg-muted border-0" />
        </div>
        <Select value={techFilter} onValueChange={(v) => { setTechFilter(v); setPage(0); }}>
          <SelectTrigger className="w-40 h-9"><SelectValue placeholder="Technology" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Technologies</SelectItem>
            {allTechs.map((t) => <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={availFilter} onValueChange={(v) => { setAvailFilter(v); setPage(0); }}>
          <SelectTrigger className="w-36 h-9"><SelectValue placeholder="Availability" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="Available">Available</SelectItem>
            <SelectItem value="Busy">Occupied</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground">{filtered.length} results</span>
      </div>

      <div className="bg-card rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Developer</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Primary Skills</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Experience</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Top Rating</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Availability</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Contact</th>
              </tr>
            </thead>
            <tbody>
              {paged.map((d) => (
                <tr key={d.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-medium">{d.name}</div>
                    <div className="text-xs text-muted-foreground">{d.current_role}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {d.skills?.slice(0, 3).map((s) => (
                        <span key={s.skill_id} className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-md">
                          {getSkillName(s.skill_id)}
                        </span>
                      ))}
                      {(d.skills?.length || 0) > 3 && <span className="text-xs text-muted-foreground">+{d.skills.length - 3}</span>}
                    </div>
                  </td>
                  {/* [MODIFIED] Now looking directly at the Global Experience from the main Developers table! */}
                  <td className="py-3 px-4 text-muted-foreground font-medium">
                    {d.years_of_experience || 0} yrs
                  </td>
                  <td className="py-3 px-4">
                    <SkillLevelBar level={(d.skills?.length || 0) > 0 ? Math.max(...d.skills.map((s) => s.proficiency_level)) : 0} />
                  </td>
                  <td className="py-3 px-4">
                    <AvailabilityBadge status={d.availability ? "Available" : "Busy"} />
                  </td>
                  <td className="py-3 px-4">
                    {d.email ? (
                      <a 
                        href={`https://mail.google.com/mail/?view=cm&fs=1&to=${d.email}&body=Hi%20${d.name},%0A%0AI%20am%20reaching%20out%20to%20discuss%20a%20potential%20opportunity.`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex p-1.5 rounded hover:bg-muted transition-colors" 
                        title={`Email ${d.name} in Gmail`}
                      >
                        <Mail className="h-4 w-4 text-primary" />
                      </a>
                    ) : (
                      <span className="text-xs text-muted-foreground">No Email</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t">
            <span className="text-xs text-muted-foreground">Page {page + 1} of {totalPages}</span>
            <div className="flex gap-1">
              <Button variant="outline" size="sm" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}><ChevronLeft className="h-4 w-4" /></Button>
              <Button variant="outline" size="sm" onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}><ChevronRight className="h-4 w-4" /></Button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}