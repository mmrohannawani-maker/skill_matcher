import { LayoutDashboard, Users, Code2, FileSearch, BarChart3, Upload, Bookmark, Settings, ChevronLeft, ChevronRight } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";
import { useAppContext } from "@/context/AppContext";
import { useState } from "react";

const allNavItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard, roles: ["Admin", "Developer", "Sales"] },
  { title: "Developers", url: "/developers", icon: Users, roles: ["Admin", "Sales"] },
  { title: "Skills", url: "/skills", icon: Code2, roles: ["Admin", "Developer"] },
  { title: "JD Matcher", url: "/jd-matcher", icon: FileSearch, roles: ["Admin", "Sales"] },
  { title: "Reports", url: "/reports", icon: BarChart3, roles: ["Admin", "Sales"] },
  { title: "Excel Upload", url: "/excel-upload", icon: Upload, roles: ["Admin"] },
  { title: "Saved Searches", url: "/saved-searches", icon: Bookmark, roles: ["Admin", "Sales"] },
  { title: "Admin Panel", url: "/admin", icon: Settings, roles: ["Admin"] },
  { title: "My Profile", url: "/profile", icon: Users, roles: ["Developer"] },
];

export function AppSidebar() {
  const { role } = useAppContext();
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navItems = allNavItems.filter((item) => item.roles.includes(role));

  return (
    <aside className={`${collapsed ? "w-16" : "w-60"} min-h-screen bg-sidebar flex flex-col transition-all duration-200 border-r border-sidebar-border`}>
      <div className={`flex items-center ${collapsed ? "justify-center" : "px-5"} h-16 border-b border-sidebar-border`}>
        {!collapsed && (
          <div>
            <h1 className="text-sm font-bold text-sidebar-primary-foreground tracking-tight">Skill Matrix</h1>
            <p className="text-[10px] text-sidebar-foreground opacity-60">Resource Finder</p>
          </div>
        )}
        {collapsed && <Code2 className="h-5 w-5 text-sidebar-primary" />}
      </div>
      <nav className="flex-1 py-4 space-y-1 px-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.url || (item.url !== "/" && location.pathname.startsWith(item.url));
          return (
            <NavLink
              key={item.url}
              to={item.url}
              end={item.url === "/"}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors ${isActive ? "" : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"}`}
              activeClassName="bg-sidebar-accent text-sidebar-primary font-medium"
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.title}</span>}
            </NavLink>
          );
        })}
      </nav>
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-10 border-t border-sidebar-border text-sidebar-foreground hover:text-sidebar-accent-foreground transition-colors"
      >
        {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>
    </aside>
  );
}
