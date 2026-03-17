import { useState } from "react";
import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Link2, Copy, UserMinus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function AdminPage() {
  // [MODIFIED] Added isLoading to destructuring
  const { teamMembers, setTeamMembers, skills, setSkills, isLoading } = useAppContext();
  const [generatedLink, setGeneratedLink] = useState("");
  const [newSkill, setNewSkill] = useState({ skill_name: "", category: "" });
  const [showAddMember, setShowAddMember] = useState(false);
  const [newMember, setNewMember] = useState({ name: "", email: "", role: "Developer", department: "Engineering" });

  // [MODIFIED] Added loading guard clause to prevent mapping crashes
  if (isLoading || !teamMembers || !skills) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading admin data...</p>
        </div>
      </DashboardLayout>
    );
  }

  const handleGenerateLink = (name: string) => {
    const link = `https://skillmatrix.company.com/self-rank/${name.toLowerCase().replace(/\s/g, "-")}-${Date.now().toString(36)}`;
    setGeneratedLink(link);
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(generatedLink);
    toast.success("Link copied!");
  };

  const handleAddMember = () => {
    if (!newMember.name || !newMember.email) return;
    // [MODIFIED] Defensive array spreading
    setTeamMembers([...(teamMembers || []), { id: Date.now().toString(), ...newMember, status: "Active" }]);
    setNewMember({ name: "", email: "", role: "Developer", department: "Engineering" });
    setShowAddMember(false);
    toast.success("Team member added");
  };

  const handleToggleStatus = (id: string) => {
    // [MODIFIED] Defensive array mapping
    setTeamMembers((teamMembers || []).map((m) => m.id === id ? { ...m, status: m.status === "Active" ? "Inactive" : "Active" } : m));
  };

  const handleAddSkill = () => {
    if (!newSkill.skill_name) return;
    // [MODIFIED] Defensive array spreading
    setSkills([...(skills || []), { id: Date.now().toString(), ...newSkill }]);
    setNewSkill({ skill_name: "", category: "" });
    toast.success("Skill added");
  };

  const handleDeleteSkill = (id: string) => {
    // [MODIFIED] Defensive array filtering
    setSkills((skills || []).filter((s) => s.id !== id));
    toast.success("Skill removed");
  };

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1 className="page-title">Admin Panel</h1>
        <p className="page-subtitle">Manage team members, skills, and settings</p>
      </div>

      <Tabs defaultValue="team" className="space-y-4">
        <TabsList>
          <TabsTrigger value="team">Team Members</TabsTrigger>
          <TabsTrigger value="skills">Skill Management</TabsTrigger>
          <TabsTrigger value="links">Self-Ranking Links</TabsTrigger>
        </TabsList>

        <TabsContent value="team">
          <div className="bg-card rounded-lg border">
            <div className="flex items-center justify-between px-5 py-3 border-b">
              <h3 className="font-semibold">Team Members ({teamMembers.length})</h3>
              <Dialog open={showAddMember} onOpenChange={setShowAddMember}>
                <DialogTrigger asChild><Button size="sm" className="gap-1"><Plus className="h-3.5 w-3.5" /> Add Member</Button></DialogTrigger>
                <DialogContent>
                  <DialogHeader><DialogTitle>Add Team Member</DialogTitle></DialogHeader>
                  <div className="space-y-3 pt-2">
                    <Input placeholder="Name" value={newMember.name} onChange={(e) => setNewMember({ ...newMember, name: e.target.value })} />
                    <Input placeholder="Email" value={newMember.email} onChange={(e) => setNewMember({ ...newMember, email: e.target.value })} />
                    <Select value={newMember.role} onValueChange={(v) => setNewMember({ ...newMember, role: v })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Developer">Developer</SelectItem>
                        <SelectItem value="Admin">Admin</SelectItem>
                        <SelectItem value="Sales">Sales</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button onClick={handleAddMember} className="w-full">Add Member</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Name</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Email</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Role</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Department</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {teamMembers.map((m) => (
                    <tr key={m.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="py-3 px-4 font-medium">{m.name}</td>
                      <td className="py-3 px-4 text-muted-foreground">{m.email}</td>
                      <td className="py-3 px-4"><span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-md">{m.role}</span></td>
                      <td className="py-3 px-4 text-muted-foreground">{m.department}</td>
                      <td className="py-3 px-4">
                        <span className={`text-xs px-2 py-0.5 rounded-md ${m.status === "Active" ? "bg-success/10 text-success" : "bg-muted text-muted-foreground"}`}>{m.status}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm" onClick={() => handleToggleStatus(m.id)}><UserMinus className="h-3.5 w-3.5" /></Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="skills">
          <div className="bg-card rounded-lg border">
            <div className="px-5 py-3 border-b flex items-center gap-3">
              <Input placeholder="Skill name" value={newSkill.skill_name} onChange={(e) => setNewSkill({ ...newSkill, skill_name: e.target.value })} className="max-w-xs" />
              <Select value={newSkill.category} onValueChange={(v) => setNewSkill({ ...newSkill, category: v })}>
                <SelectTrigger className="w-36"><SelectValue placeholder="Category" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Frontend">Frontend</SelectItem>
                  <SelectItem value="Backend">Backend</SelectItem>
                  <SelectItem value="Database">Database</SelectItem>
                  <SelectItem value="Cloud">Cloud</SelectItem>
                  <SelectItem value="DevOps">DevOps</SelectItem>
                </SelectContent>
              </Select>
              <Button size="sm" onClick={handleAddSkill} className="gap-1"><Plus className="h-3.5 w-3.5" /> Add</Button>
            </div>
            <div className="divide-y max-h-96 overflow-auto">
              {skills.map((s) => (
                <div key={s.id} className="flex items-center justify-between px-5 py-2.5">
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-sm">{s.skill_name}</span>
                    <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-md">{s.category || "Uncategorized"}</span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleDeleteSkill(s.id)}><Trash2 className="h-3.5 w-3.5 text-destructive" /></Button>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="links">
          <div className="bg-card rounded-lg border p-5 max-w-lg">
            <h3 className="font-semibold mb-3 flex items-center gap-2"><Link2 className="h-4 w-4 text-primary" /> Generate Self-Ranking Link</h3>
            <p className="text-sm text-muted-foreground mb-4">Generate a unique URL for a developer to fill in their skill self-assessment.</p>
            <div className="space-y-2">
              {teamMembers.filter((m) => m.role === "Developer").slice(0, 5).map((m) => (
                <div key={m.id} className="flex items-center justify-between py-2 border-b last:border-0">
                  <span className="text-sm font-medium">{m.name}</span>
                  <Button variant="outline" size="sm" onClick={() => handleGenerateLink(m.name)} className="gap-1"><Link2 className="h-3.5 w-3.5" /> Generate</Button>
                </div>
              ))}
            </div>
            {generatedLink && (
              <div className="mt-4 p-3 bg-muted rounded-md">
                <p className="text-xs text-muted-foreground mb-1">Generated Link:</p>
                <div className="flex items-center gap-2">
                  <code className="text-xs flex-1 break-all">{generatedLink}</code>
                  <Button variant="ghost" size="sm" onClick={handleCopyLink}><Copy className="h-3.5 w-3.5" /></Button>
                </div>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}