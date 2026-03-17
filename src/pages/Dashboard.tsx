import { useState } from "react";
import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button"; 
// [MODIFIED] Added 'X' to the lucide-react imports
import { Users, Code2, CheckCircle, TrendingUp, Star, Mail, Search, ChevronLeft, ChevronRight, X } from "lucide-react"; 
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { AvailabilityBadge } from "@/components/StatusBadges";

const PAGE_SIZE = 5;

export default function Dashboard() {
  const { developers, skills, isLoading } = useAppContext();
  
  const [selectedTechs, setSelectedTechs] = useState<string[]>([]);
  const [clickedGraphTech, setClickedGraphTech] = useState<string | null>(null);
  const [skillSearch, setSkillSearch] = useState<string>("");
  const [page, setPage] = useState<number>(0); 

  if (isLoading || !developers) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading dashboard data...</p>
        </div>
      </DashboardLayout>
    );
  }

  const getSkillName = (skillId: number | string) => {
    if (!skills || skills.length === 0) return `Skill ${skillId}`;
    const foundSkill = skills.find(s => Number(s.id) === Number(skillId));
    return foundSkill ? foundSkill.skill_name : `Skill ${skillId}`;
  };

  const totalDevs = developers.length;
  const availableDevs = developers.filter((d) => d?.availability === true).length;
  const allSkillEntries = developers.flatMap((d) => d?.skills || []);
  const uniqueSkills = new Set(allSkillEntries.map((s) => s?.skill_id).filter(Boolean)).size;
  
  const avgRating = allSkillEntries.length 
    ? (allSkillEntries.reduce((a, b) => a + (b?.proficiency_level || 0), 0) / allSkillEntries.length).toFixed(1) 
    : "0";

  const counts: Record<string, number> = {};
  developers.forEach((dev) => {
    const uniqueSkillsForDev = new Set(dev?.skills?.map(s => s.skill_id).filter(Boolean));
    uniqueSkillsForDev.forEach((skillId) => {
      const skillLabel = getSkillName(skillId as number);
      counts[skillLabel] = (counts[skillLabel] || 0) + 1;
    });
  });
  
  const topSkills = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, count]) => ({ name, value: count })); 

  const uniqueIds = new Set(developers.flatMap((d) => d.skills?.map((s) => s.skill_id.toString()) || []));
  const allTechs = Array.from(uniqueIds)
    .map(id => ({ id: String(id), name: getSkillName(id) }))
    .sort((a, b) => a.name.localeCompare(b.name));
    
  const filteredTechs = allTechs.filter(t => 
    t.name.toLowerCase().includes(skillSearch.toLowerCase())
  );

  let chartData = [];
  if (selectedTechs.length === 0) {
    chartData = topSkills;
  } else {
    chartData = selectedTechs.map(techId => {
      const techName = getSkillName(techId);
      const specificTechCount = developers.filter(d => 
        d.skills?.some(s => s.skill_id.toString() === techId)
      ).length;
      return { name: techName, value: specificTechCount, id: techId };
    });
  }

  const shouldBeDiagonal = chartData.length > 4;

  let allMatchingExperts = [];
  if (selectedTechs.length === 0) {
    allMatchingExperts = [...developers]
      .map((d) => ({
        ...d,
        maxSkill: (d?.skills && d.skills.length > 0) ? Math.max(...d.skills.map((s) => s?.proficiency_level || 0)) : 0,
        totalExp: d.years_of_experience || 0
      }))
      .sort((a, b) => b.maxSkill - a.maxSkill || b.totalExp - a.totalExp);
  } else {
    const targetTechs = clickedGraphTech ? [clickedGraphTech] : selectedTechs;
    
    allMatchingExperts = developers
      .filter(d => d.skills?.some(s => targetTechs.includes(s.skill_id.toString())))
      .map(d => {
        const relevantSkills = d.skills?.filter(sk => targetTechs.includes(sk.skill_id.toString())) || [];
        const maxProf = relevantSkills.length > 0 ? Math.max(...relevantSkills.map(s => s.proficiency_level || 0)) : 0;
        const maxExp = relevantSkills.length > 0 ? Math.max(...relevantSkills.map(s => s.years_of_experience || 0)) : 0;
        
        return {
          ...d,
          maxSkill: maxProf,
          totalExp: maxExp 
        };
      })
      .sort((a, b) => b.maxSkill - a.maxSkill || b.totalExp - a.totalExp);
  }

  const totalPages = Math.ceil(allMatchingExperts.length / PAGE_SIZE);
  const pagedExperts = allMatchingExperts.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const handleBarClick = (data: any) => {
    if (selectedTechs.length === 0 && data && data.name) {
      const matched = allTechs.find(t => t.name === data.name);
      if (matched) {
        setSelectedTechs([matched.id]);
        setClickedGraphTech(null);
        setPage(0);
        setSkillSearch("");
      }
    } else if (selectedTechs.length > 0 && data && data.id) {
      setClickedGraphTech(data.id === clickedGraphTech ? null : data.id);
      setPage(0);
    }
  };

  const toggleTech = (techId: string) => {
    setSelectedTechs(prev => {
      if (prev.includes(techId)) return prev.filter(t => t !== techId);
      return [...prev, techId];
    });
    setClickedGraphTech(null);
    setPage(0);
  };

  const availData = [
    { name: "Available", value: developers.filter((d) => d?.availability === true).length },
    { name: "Occupied", value: developers.filter((d) => d?.availability === false).length },
  ];
  const pieColors = ["hsl(142, 72%, 36%)", "hsl(36, 90%, 50%)"];

  const stats = [
    { label: "Total Developers", value: totalDevs, icon: Users, color: "text-primary" },
    { label: "Available Now", value: availableDevs, icon: CheckCircle, color: "text-success" },
    { label: "Unique Skills", value: uniqueSkills, icon: Code2, color: "text-accent" },
    { label: "Avg Skill Rating", value: avgRating, icon: TrendingUp, color: "text-warning" },
  ];

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Welcome back! Here's your organization's skill overview.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((s) => (
          <div key={s.label} className="stat-card flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground">{s.label}</p>
              <p className="text-2xl font-bold mt-1">{s.value}</p>
            </div>
            <s.icon className={`h-5 w-5 ${s.color} mt-1`} />
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 bg-card rounded-lg border p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Skills Distribution</h3>
            
            <Select 
              value={selectedTechs.length === 0 ? "all" : selectedTechs.join(',')} 
              onValueChange={(val) => { 
                if (val === "all") {
                  setSelectedTechs([]);
                  setClickedGraphTech(null);
                  setPage(0);
                }
              }}
            >
              <SelectTrigger className="w-[220px] h-9 text-sm capitalize">
                <SelectValue>
                  {selectedTechs.length === 0 
                    ? "Overall Top Skills" 
                    : selectedTechs.length === 1 
                      ? getSkillName(selectedTechs[0])
                      : `${selectedTechs.length} Skills Selected`}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {/* [MODIFIED] Added the flex layout and X clear button to the search header */}
                <div className="px-2 py-2 sticky top-0 bg-popover z-10 border-b mb-1 flex items-center gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                    <Input 
                      placeholder="Search skills..." 
                      value={skillSearch} 
                      onChange={(e) => setSkillSearch(e.target.value)}
                      onKeyDown={(e) => e.stopPropagation()} 
                      className="h-8 pl-7 text-xs"
                    />
                  </div>
                  {selectedTechs.length > 0 && (
                    <div
                      className="flex h-8 cursor-pointer items-center justify-center gap-1 rounded-md px-2 text-xs font-medium text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setSelectedTechs([]);
                        setClickedGraphTech(null);
                        setPage(0);
                      }}
                      title="Clear all selected skills"
                    >
                      <X className="h-3.5 w-3.5" /> Clear
                    </div>
                  )}
                </div>
                
                <SelectItem value="all" className="font-semibold text-primary">
                  Overall Top Skills
                </SelectItem>
                
                {filteredTechs.map((t) => (
                  <div
                    key={t.id}
                    className="relative flex w-full cursor-pointer select-none items-center rounded-sm py-1.5 pl-2 pr-2 text-sm outline-none hover:bg-accent hover:text-accent-foreground capitalize transition-colors"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      toggleTech(t.id);
                    }}
                  >
                    <div className={`mr-2 flex h-4 w-4 items-center justify-center rounded-sm border ${selectedTechs.includes(t.id) ? 'bg-primary border-primary text-primary-foreground' : 'border-muted-foreground'}`}>
                      {selectedTechs.includes(t.id) && <CheckCircle className="h-3 w-3 text-white" />}
                    </div>
                    {t.name}
                  </div>
                ))}

                {selectedTechs.length > 0 && (
                  <SelectItem value={selectedTechs.join(',')} className="hidden">
                    {selectedTechs.join(',')}
                  </SelectItem>
                )}
                
                {filteredTechs.length === 0 && (
                  <div className="text-center py-4 text-xs text-muted-foreground">No skills found</div>
                )}
              </SelectContent>
            </Select>
            
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(214, 20%, 90%)" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 11 }} 
                interval={0} 
                angle={shouldBeDiagonal ? -35 : 0} 
                textAnchor={shouldBeDiagonal ? "end" : "middle"} 
                height={shouldBeDiagonal ? 60 : 30} 
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value: number) => [value, "Developers"]} />
              <Bar 
                dataKey="value" 
                fill="hsl(215, 80%, 28%)" 
                radius={[4, 4, 0, 0]} 
                cursor={selectedTechs.length > 0 || selectedTechs.length === 0 ? "pointer" : "default"} 
                onClick={handleBarClick} 
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={clickedGraphTech && clickedGraphTech !== entry.id ? "hsl(215, 80%, 80%)" : "hsl(215, 80%, 28%)"} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="bg-card rounded-lg border p-5">
          <h3 className="font-semibold mb-4">Resource Availability</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={availData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value">
                {availData.map((_, i) => <Cell key={i} fill={pieColors[i]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {availData.map((d, i) => (
              <div key={d.name} className="flex items-center gap-1.5 text-xs">
                <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: pieColors[i] }} />
                <span className="text-muted-foreground">{d.name} ({d.value})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-card rounded-lg border overflow-hidden mb-6">
        <div className="p-5 border-b bg-muted/10">
          <h3 className="font-semibold flex items-center gap-2 capitalize">
            {selectedTechs.length === 0 
              ? "Top Experts (Overall)" 
              : clickedGraphTech 
                ? `Experts in ${getSkillName(clickedGraphTech)}`
                : "Experts in Selected Skills"
            }
            {selectedTechs.length !== 0 && (
              <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full ml-2 font-bold">
                {allMatchingExperts.length} Total
              </span>
            )}
            
            {clickedGraphTech && (
              <Button variant="ghost" size="sm" className="ml-auto h-7 text-xs" onClick={() => setClickedGraphTech(null)}>
                View All Selected
              </Button>
            )}
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-muted-foreground bg-muted/5">
                <th className="text-left py-3 px-5 font-medium">Developer</th>
                <th className="text-left py-3 px-5 font-medium">Max Rating</th>
                <th className="text-left py-3 px-5 font-medium">Relevant Exp</th>
                <th className="text-left py-3 px-5 font-medium">Availability</th>
                <th className="text-left py-3 px-5 font-medium">Contact</th>
              </tr>
            </thead>
            <tbody>
              {pagedExperts.length > 0 ? (
                pagedExperts.map((d) => (
                  <tr key={d.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                    <td className="py-3 px-5 font-medium">{d?.name || "Unknown"}</td>
                    <td className="py-3 px-5">
                      <div className="flex items-center gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star 
                            key={star} 
                            className={`h-4 w-4 ${
                              star <= d.maxSkill 
                                ? "fill-yellow-500 text-yellow-500" 
                                : "text-muted-foreground/30"
                            }`} 
                          />
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-5">{d.totalExp} yrs</td>
                    <td className="py-3 px-5"><AvailabilityBadge status={d.availability ? "Available" : "Busy"} /></td>
                    <td className="py-3 px-5">
                      {d.email ? (
                        <a 
                          href={`https://mail.google.com/mail/?view=cm&fs=1&to=${d.email}&body=Hi%20${d.name},%0A%0AI%20am%20reaching%20out%20to%20discuss%20a%20potential%20opportunity.`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex p-1.5 rounded hover:bg-muted transition-colors" 
                          title={`Email ${d?.name || 'Developer'} in Gmail`}
                        >
                          <Mail className="h-4 w-4 text-primary" />
                        </a>
                      ) : (
                        <span className="text-xs text-muted-foreground">No Email</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-muted-foreground">
                    No experts found for these skills.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-3 border-t bg-muted/5">
            <span className="text-xs text-muted-foreground">Page {page + 1} of {totalPages}</span>
            <div className="flex gap-1">
              <Button variant="outline" size="sm" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}