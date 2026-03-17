import { Badge } from "@/components/ui/badge";
// [NEW] Import the Star icon from lucide-react
import { Star } from "lucide-react";

export function AvailabilityBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    Available: "bg-success/10 text-success border-success/20",
    Busy: "bg-warning/10 text-warning border-warning/20",
    "On Project": "bg-info/10 text-info border-info/20",
  };
  return (
    <Badge variant="outline" className={`${map[status] || ""} text-xs font-medium`}>
      {status}
    </Badge>
  );
}

export function SkillLevelBar({ level }: { level: number }) {
  return (
    // [MODIFIED] Updated container classes for proper star alignment
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((i) => (
        // [MODIFIED] Replaced the div with the Star icon component
        <Star
          key={i}
          className={`h-4 w-4 ${
            i <= level
              ? "fill-yellow-500 text-yellow-500"
              : "text-muted-foreground/30"
          }`}
        />
      ))}
    </div>
  );
}