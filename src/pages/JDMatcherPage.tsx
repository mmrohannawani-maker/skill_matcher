import { useState, useEffect } from "react";
import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Sparkles, FileText, Search, UserCheck, Mail, Trash2 } from "lucide-react";
import { toast } from "sonner";

export default function JDMatcherPage() {
  const { developers, skills: masterSkills } = useAppContext();
  
  const [jdText, setJdText] = useState(() => {
    return localStorage.getItem("jdMatcherText") || "";
  });
  
  const [isMatching, setIsMatching] = useState(false);
  
  const [results, setResults] = useState<any[]>(() => {
    try {
      const saved = localStorage.getItem("jdMatcherResults");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem("jdMatcherText", jdText);
  }, [jdText]);

  useEffect(() => {
    localStorage.setItem("jdMatcherResults", JSON.stringify(results));
  }, [results]);

  const handleClear = () => {
    setJdText("");
    setResults([]);
    localStorage.removeItem("jdMatcherText");
    localStorage.removeItem("jdMatcherResults");
    toast.success("Cleared job description and results");
  };

  const handleMatch = async () => {
    if (!jdText.trim()) {
      toast.error("Please paste a job description first");
      return;
    }

    setIsMatching(true);
    
    try {
      const response = await fetch("http://localhost:8000/jd/analyze", { 
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          jd_description: jdText, 
          created_by_user_id: 1, 
          jd_title: "Quick Search"
        }) 
      });

      if (!response.ok) {
        throw new Error(`Backend connection failed with status: ${response.status}`);
      }

      const backendData = await response.json();
      const rawMatches = backendData.matched_developers || [];
      
      const finalResults = rawMatches.map((backendDev: any) => {
        const fullDevProfile = developers.find(d => Number(d.id) === Number(backendDev.developer_id));
        const matchedSkillsLower = (backendDev.matched_skills || []).map((s: string) => s.toLowerCase());
        
        // Find the highest experience among the specifically matched skills
        const relevantExp = matchedSkillsLower.length > 0 && fullDevProfile?.skills
          ? Math.max(...fullDevProfile.skills
              .filter(s => {
                 const sName = masterSkills.find(ms => Number(ms.id) === Number(s.skill_id))?.skill_name.toLowerCase() || "";
                 return matchedSkillsLower.includes(sName);
              })
              .map(s => s.years_of_experience || 0)) 
          : 0;

        return {
          ...fullDevProfile, 
          name: fullDevProfile?.name || backendDev.developer_name, 
          matchedSkills: backendDev.matched_skills || [],
          matchScore: Math.round((backendDev.match_score || 0) * 100), 
          // [MODIFIED] Use relevantExp if skills matched, otherwise use their Global Profile Experience
          displayExp: relevantExp > 0 ? relevantExp : (fullDevProfile?.years_of_experience || 0),
          email: fullDevProfile?.email || "" 
        };
      })
      // [MODIFIED] Changed to >= 0 so the UI doesn't crash to an empty list when AI fails to find skills
      .filter((res: any) => res.matchScore >= 0)
      .sort((a: any, b: any) => b.matchScore - a.matchScore);

      setResults(finalResults);
      toast.success(`Found ${finalResults.length} relevant matches from the AI!`);
    } catch (error) {
      console.error("Match error:", error);
      toast.error("Failed to connect to the backend. Check the console for details.");
    } finally {
      setIsMatching(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1 className="page-title">JD Matcher</h1>
        <p className="page-subtitle">Paste a Job Description to find the best-fit developers</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm flex items-center gap-2">
              <FileText className="h-4 w-4 text-primary" />
              Job Description
            </CardTitle>
            {(jdText || results.length > 0) && (
              <Button variant="ghost" size="sm" onClick={handleClear} className="h-8 text-muted-foreground hover:text-destructive">
                <Trash2 className="h-4 w-4 mr-1" /> Clear
              </Button>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea 
              placeholder="Paste the full job description here..."
              className="min-h-[400px] resize-none"
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />
            <Button className="w-full gap-2" onClick={handleMatch} disabled={isMatching}>
              {isMatching ? <span className="animate-spin">🌀</span> : <Sparkles className="h-4 w-4" />}
              {isMatching ? "Analyzing..." : "Find Best Fit"}
            </Button>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <UserCheck className="h-4 w-4 text-primary" />
              {results.length} Matches Found
            </CardTitle>
          </CardHeader>
          <CardContent>
            {results.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-muted-foreground">
                      <th className="text-left py-3 px-2 font-medium">Developer</th>
                      <th className="text-left py-3 px-2 font-medium">Matched Skills</th>
                      <th className="text-left py-3 px-2 font-medium">Match Score</th>
                      <th className="text-left py-3 px-2 font-medium">Experience</th>
                      <th className="text-left py-3 px-2 font-medium">Contact</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {results.map((res) => (
                      <tr key={res.id} className="hover:bg-muted/50 transition-colors">
                        <td className="py-4 px-2 font-medium">{res.name}</td>
                        <td className="py-4 px-2">
                          <div className="flex flex-wrap gap-1">
                            {res.matchedSkills.map((s: string, index: number) => (
                              <Badge key={`${res.id}-${s}-${index}`} variant="secondary" className="bg-primary/10 text-primary hover:bg-primary/10 border-none capitalize">
                                {s}
                              </Badge>
                            ))}
                          </div>
                        </td>
                        <td className="py-4 px-2 w-32">
                          <div className="flex items-center gap-2">
                            <Progress value={res.matchScore} className="h-2" />
                            <span className="font-bold">{res.matchScore}%</span>
                          </div>
                        </td>
                        <td className="py-4 px-2 text-muted-foreground">
                          {res.displayExp} yrs
                        </td>
                        <td className="py-4 px-2">
                          {res.email ? (
                            <a 
                              href={`https://mail.google.com/mail/?view=cm&fs=1&to=${res.email}&body=Hi%20${res.name},%0A%0AI%20saw%20your%20profile%20and%20you%20seem%20like%20a%20great%20fit%20for%20a%20role%20we%20are%20trying%20to%20fill.`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex p-1.5 rounded hover:bg-muted transition-colors" 
                              title={`Email ${res.name} in Gmail`}
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
            ) : (
              <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
                <Search className="h-12 w-12 mb-4 opacity-20" />
                <p>Run a match to see ranked candidates</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}