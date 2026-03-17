import { useAppContext } from "@/context/AppContext";
import { UserRole } from "@/mockData/types";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
// [MODIFIED] Removed the 'Search' icon and 'Input' component imports since we no longer need them here
import { Bell } from "lucide-react";

export function AppHeader() {
  const { role, setRole } = useAppContext();

  return (
    // [MODIFIED] Changed 'justify-between' to 'justify-end' so the right-side menu stays on the right
    <header className="h-14 border-b bg-card flex items-center justify-end px-6 shrink-0">
      
      {/* Search Bar section has been completely and safely removed from here */}

      <div className="flex items-center gap-4">
        <Select value={role} onValueChange={(v) => setRole(v as UserRole)}>
          <SelectTrigger className="w-36 h-9 text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Admin">Admin</SelectItem>
            <SelectItem value="Developer">Developer</SelectItem>
            <SelectItem value="Sales">Sales</SelectItem>
          </SelectContent>
        </Select>
        <button className="relative p-2 rounded-md hover:bg-muted transition-colors">
          <Bell className="h-4 w-4 text-muted-foreground" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-accent rounded-full"></span>
        </button>
        <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-medium">
          {role[0]}
        </div>
      </div>
    </header>
  );
}