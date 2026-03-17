import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

export default function ReportsPage() {
  // [MODIFIED] Added 'skills: masterSkills' to map IDs to real names
  const { developers, skills: masterSkills, isLoading } = useAppContext();

  if (isLoading || !developers || !masterSkills) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading report data...</p>
        </div>
      </DashboardLayout>
    );
  }

  // Helper function to get real skill names
  const getSkillName = (skillId: number) => {
    const matchedSkill = masterSkills.find(ms => Number(ms.id) === Number(skillId));
    return matchedSkill ? matchedSkill.skill_name : `Skill ${skillId}`;
  };

  // [MODIFIED] Calculate unique skill counts per developer
  const skillStatsMap: Record<number, { name: string; count: number }> = {};
  
  developers.forEach((dev) => {
    // 1. Get unique skill IDs for this specific developer
    const uniqueSkillIds = new Set(dev?.skills?.map(s => Number(s.skill_id)).filter(Boolean));
    
    // 2. Count them
    uniqueSkillIds.forEach((skillId) => {
      if (!skillStatsMap[skillId]) {
        skillStatsMap[skillId] = { 
          name: getSkillName(skillId), 
          count: 0 
        };
      }
      skillStatsMap[skillId].count += 1;
    });
  });
  
  // Slicing to top 15 so the chart doesn't get infinitely wide with 180+ skills
  const skillData = Object.values(skillStatsMap).sort((a, b) => b.count - a.count).slice(0, 15);

  const availData = [
    { name: "Available", value: developers.filter((d) => d?.availability === true).length },
    { name: "Busy/Occupied", value: developers.filter((d) => d?.availability === false).length },
  ];
  const pieColors = ["hsl(142, 72%, 36%)", "hsl(36, 90%, 50%)"];

  const expRanges = [
    { range: "0-5 yrs", min: 0, max: 5 },
    { range: "6-10 yrs", min: 6, max: 10 },
    { range: "11-15 yrs", min: 11, max: 15 },
    { range: "15+ yrs", min: 16, max: Infinity },
  ];
  
  const expData = expRanges.map((r) => ({
    range: r.range,
    count: developers.filter((d) => {
      // [MODIFIED] Now uses the actual Global Career Experience directly from the database!
      const total = d.years_of_experience || 0;
      return total >= r.min && total <= r.max;
    }).length,
  }));

  // [MODIFIED] Use the mapped names for the Top Experts section
  const topExperts = Object.entries(skillStatsMap)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 6)
    .map(([skillIdStr, info]) => {
      const skillId = parseInt(skillIdStr);
      const best = developers
        .map((d) => ({ name: d.name, skill: d?.skills?.find((s) => Number(s.skill_id) === skillId) }))
        .filter((d) => d.skill)
        .sort((a, b) => (b.skill?.proficiency_level || 0) - (a.skill?.proficiency_level || 0))
        .slice(0, 2);
      return { tech: info.name, experts: best };
    });

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1 className="page-title">Reports</h1>
        <p className="page-subtitle">Organization-wide skill analytics and insights</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-card rounded-lg border p-5">
          <h3 className="font-semibold mb-4 text-sm">Skill Availability</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={skillData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(214, 20%, 90%)" />
              {/* [MODIFIED] Added interval={0} and angle so Recharts stops hiding labels */}
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-35} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="hsl(215, 80%, 28%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card rounded-lg border p-5">
          <h3 className="font-semibold mb-4 text-sm">Resource Availability (%)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={availData} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={4} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {availData.map((_, i) => <Cell key={i} fill={pieColors[i]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card rounded-lg border p-5">
          <h3 className="font-semibold mb-4 text-sm">Experience Distribution (Total Yrs)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={expData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(214, 20%, 90%)" />
              <XAxis dataKey="range" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="hsl(174, 62%, 38%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card rounded-lg border p-5">
          <h3 className="font-semibold mb-4 text-sm">Top Experts by Skill</h3>
          <div className="space-y-3">
            {topExperts.map((te) => (
              <div key={te.tech} className="flex items-center gap-3 py-2 border-b last:border-0">
                <span className="text-xs font-medium bg-primary/10 text-primary px-2 py-1 rounded-md w-24 text-center truncate" title={te.tech}>{te.tech}</span>
                <div className="flex-1 text-sm text-muted-foreground">
                  {te.experts.map((e) => `${e.name} (${e.skill?.proficiency_level}/5)`).join(", ")}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}