import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppProvider } from "@/context/AppContext";
import Dashboard from "./pages/Dashboard";
import DevelopersPage from "./pages/DevelopersPage";
import SkillsPage from "./pages/SkillsPage";
// [NEW] Imported the Skills Search Page
import SkillsSearchPage from "./pages/SkillsSearch"; 
import JDMatcherPage from "./pages/JDMatcherPage";
import ReportsPage from "./pages/ReportsPage";
import ExcelUploadPage from "./pages/ExcelUploadPage";
import SavedSearchesPage from "./pages/SavedSearchesPage";
import AdminPage from "./pages/AdminPage";
import ProfilePage from "./pages/ProfilePage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AppProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/developers" element={<DevelopersPage />} />
            <Route path="/skills" element={<SkillsPage />} />
            {/* [NEW] Registered the new route for the View All Skills button */}
            <Route path="/skills-search" element={<SkillsSearchPage />} />
            <Route path="/jd-matcher" element={<JDMatcherPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/excel-upload" element={<ExcelUploadPage />} />
            <Route path="/saved-searches" element={<SavedSearchesPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AppProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;