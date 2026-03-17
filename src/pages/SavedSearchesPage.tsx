import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Trash2, Eye, Bookmark } from "lucide-react";
import { toast } from "sonner";

export default function SavedSearchesPage() {
  // [MODIFIED] Added isLoading to destructuring
  const { savedSearches, setSavedSearches, isLoading } = useAppContext();

  // [MODIFIED] Added loading guard clause for UI consistency across the app
  if (isLoading || !savedSearches) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading saved searches...</p>
        </div>
      </DashboardLayout>
    );
  }

  const handleDelete = (id: string) => {
    setSavedSearches(savedSearches.filter((s) => s.id !== id));
    toast.success("Search deleted");
  };

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1 className="page-title">Saved Searches</h1>
        <p className="page-subtitle">Previously saved JD match searches</p>
      </div>

      {savedSearches.length === 0 ? (
        <div className="bg-card rounded-lg border p-12 text-center">
          <Bookmark className="h-12 w-12 mx-auto text-muted-foreground/40 mb-4" />
          <h3 className="font-semibold text-muted-foreground">No saved searches</h3>
          <p className="text-sm text-muted-foreground/70 mt-1">Save a JD match search to see it here</p>
        </div>
      ) : (
        <div className="bg-card rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Search Name</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Date</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Keywords</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Results</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody>
              {savedSearches.map((s) => (
                <tr key={s.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                  <td className="py-3 px-4 font-medium">{s.name}</td>
                  <td className="py-3 px-4 text-muted-foreground">{s.date}</td>
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {s.keywords?.map((k) => (
                        <span key={k} className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-md">{k}</span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-muted-foreground">{s.resultsCount}</td>
                  <td className="py-3 px-4">
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm"><Eye className="h-3.5 w-3.5" /></Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(s.id)}><Trash2 className="h-3.5 w-3.5 text-destructive" /></Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </DashboardLayout>
  );
}