import { useState } from "react";
import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Trash2, User } from "lucide-react";
import { SkillLevelBar } from "@/components/StatusBadges";
import { DeveloperSkill } from "@/mockData/types";
import { toast } from "sonner";

export default function ProfilePage() {
  // [MODIFIED] Added isLoading and skills for name mapping
  const { developers, setDevelopers, skills: masterSkills, isLoading } = useAppContext();
  const dev = developers[0]; // Simulate logged-in developer
  
  // [MODIFIED] Removed the buggy availability useState. We will derive it directly from the 'dev' object.
  
  const [newSkill, setNewSkill] = useState<Partial<DeveloperSkill>>({ 
    skill_id: 0, 
    proficiency_level: 3, 
    years_of_experience: 0, 
    last_used_year: 2026, 
    certification: "" 
  });

  // [MODIFIED] Consistent loading guard
  if (isLoading || !dev || !masterSkills) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading profile data...</p>
        </div>
      </DashboardLayout>
    );
  }

  const handleAddSkill = () => {
    if (!newSkill.skill_id) return;
    // [MODIFIED] Fallback to empty array to ensure safe spreading
    const updated = { ...dev, skills: [...(dev.skills || []), newSkill as DeveloperSkill] };
    setDevelopers(developers.map((d) => d.id === dev.id ? updated : d));
    setNewSkill({ skill_id: 0, proficiency_level: 3, years_of_experience: 0, last_used_year: 2026, certification: "" });
    toast.success("Skill added");
  };

  const handleRemoveSkill = (skillId: number) => {
    // [MODIFIED] Fallback to empty array to ensure safe filtering
    const updated = { ...dev, skills: (dev.skills || []).filter((s) => s.skill_id !== skillId) };
    setDevelopers(developers.map((d) => d.id === dev.id ? updated : d));
  };

  const handleAvailability = (v: string) => {
    const isAvailable = v === "Available";
    setDevelopers(developers.map((d) => d.id === dev.id ? { ...d, availability: isAvailable } : d));
    toast.success("Availability updated");
  };

  // [MODIFIED] Helper function to map skill_id to skill_name
  const getSkillName = (id: number) => {
    const matched = masterSkills.find(ms => Number(ms.id) === id);
    return matched ? matched.skill_name : `Skill ${id}`;
  };

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1 className="page-title">My Profile</h1>
        <p className="page-subtitle">Manage your skills and availability</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="space-y-4">
          <div className="bg-card rounded-lg border p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-12 w-12 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold"><User className="h-5 w-5" /></div>
              <div>
                <h3 className="font-semibold">{dev.name}</h3>
                <p className="text-sm text-muted-foreground">{dev.email}</p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">Role</span><span>{dev.current_role}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Department</span><span>{dev.department}</span></div>
            </div>
          </div>
          <div className="bg-card rounded-lg border p-5">
            <h3 className="font-semibold mb-3">Availability</h3>
            {/* [MODIFIED] Reads directly from dev.availability to prevent sync bugs */}
            <Select value={dev.availability ? "Available" : "Busy"} onValueChange={handleAvailability}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="Available">Available</SelectItem>
                <SelectItem value="Busy">Busy</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="bg-card rounded-lg border">
            <div className="px-5 py-3 border-b flex items-center justify-between">
              <h3 className="font-semibold">My Skills</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left py-2 px-4 font-medium text-muted-foreground">Skill</th>
                    <th className="text-left py-2 px-4 font-medium text-muted-foreground">Level</th>
                    <th className="text-left py-2 px-4 font-medium text-muted-foreground">Experience</th>
                    <th className="text-left py-2 px-4 font-medium text-muted-foreground">Last Used</th>
                    <th className="text-left py-2 px-4 font-medium text-muted-foreground">Cert</th>
                    <th className="text-left py-2 px-4 font-medium text-muted-foreground"></th>
                  </tr>
                </thead>
                <tbody>
                  {dev.skills?.map((s) => (
                    <tr key={s.skill_id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      {/* [MODIFIED] Now shows actual skill name instead of just the ID */}
                      <td className="py-2.5 px-4 font-medium">{getSkillName(s.skill_id)}</td>
                      <td className="py-2.5 px-4"><SkillLevelBar level={s.proficiency_level} /></td>
                      <td className="py-2.5 px-4 text-muted-foreground">{s.years_of_experience} yrs</td>
                      <td className="py-2.5 px-4 text-muted-foreground">{s.last_used_year}</td>
                      <td className="py-2.5 px-4 text-muted-foreground text-xs">{s.certification || "—"}</td>
                      <td className="py-2.5 px-4"><Button variant="ghost" size="sm" onClick={() => handleRemoveSkill(s.skill_id)}><Trash2 className="h-3.5 w-3.5 text-destructive" /></Button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-5 py-3 border-t bg-muted/30 flex flex-wrap gap-2 items-center">
              <Input 
                placeholder="Skill ID" 
                type="number"
                value={newSkill.skill_id || ""} 
                onChange={(e) => setNewSkill({ ...newSkill, skill_id: Number(e.target.value) })} 
                className="max-w-[140px] h-8 text-sm bg-background" 
              />
              <Select value={String(newSkill.proficiency_level)} onValueChange={(v) => setNewSkill({ ...newSkill, proficiency_level: Number(v) })}>
                <SelectTrigger className="w-24 h-8 text-sm bg-background"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {[1, 2, 3, 4, 5].map((l) => <SelectItem key={l} value={String(l)}>Level {l}</SelectItem>)}
                </SelectContent>
              </Select>
              <Input 
                placeholder="Yrs" 
                type="number" 
                value={newSkill.years_of_experience || ""} 
                onChange={(e) => setNewSkill({ ...newSkill, years_of_experience: Number(e.target.value) })} 
                className="w-16 h-8 text-sm bg-background" 
              />
              <Button size="sm" onClick={handleAddSkill} className="gap-1 h-8"><Plus className="h-3.5 w-3.5" /> Add</Button>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}