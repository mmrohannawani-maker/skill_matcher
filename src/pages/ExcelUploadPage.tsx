import { useState, useCallback } from "react";
import { useAppContext } from "@/context/AppContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Upload, FileSpreadsheet, CheckCircle, Users, Code2 } from "lucide-react";
import { toast } from "sonner";
import * as XLSX from "xlsx";

export default function ExcelUploadPage() {
  const { setDevelopers, isLoading } = useAppContext(); // [CORRECTION] Added isLoading
  const [preview, setPreview] = useState<any[]>([]);
  const [stats, setStats] = useState<{ devs: number; skills: number } | null>(null);
  const [dragging, setDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // [CORRECTION] Guard clause to prevent interaction during initial app sync
  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground animate-pulse">Syncing system state...</p>
        </div>
      </DashboardLayout>
    );
  }

  const generatePreview = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: "array" });
        const sheetName = workbook.SheetNames[0];
        const rows = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName]);
        setPreview(rows.slice(0, 10));
      } catch (err) {
        console.error("Preview error:", err);
      }
    };
    reader.readAsArrayBuffer(file);
  };

  const processFile = async (file: File) => {
    generatePreview(file);
    const formData = new FormData();
    formData.append("file", file);
    setIsUploading(true);

    try {
      const response = await fetch("http://localhost:8000/excel/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const result = await response.json();
      
      setStats({ 
        devs: result.developers_created, 
        skills: result.skills_mapped, 
      });

      toast.success(`Successfully imported ${result.developers_created} developers`);

      // [CORRECTION] Use the same endpoint the AppContext uses to ensure data consistency
      const refreshRes = await fetch("http://localhost:8000/developers/");
      if (refreshRes.ok) {
        const updatedDevs = await refreshRes.json();
        setDevelopers(updatedDevs);
      }

    } catch (error) {
      console.error("Upload Error:", error);
      toast.error("Failed to process Excel file. Check backend terminal.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); 
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1 className="page-title">Excel Upload</h1>
        <p className="page-subtitle">Import developer skill matrix from an Excel file</p>
      </div>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`bg-card rounded-lg border-2 border-dashed p-12 text-center transition-colors ${dragging ? "border-primary bg-primary/5" : "border-border"}`}
      >
        <Upload className={`h-12 w-12 mx-auto mb-4 ${isUploading ? "animate-bounce text-primary" : "text-muted-foreground/40"}`} />
        <h3 className="font-semibold mb-1">{isUploading ? "Uploading to SQLite Database..." : "Drop your Excel file here"}</h3>
        <p className="text-sm text-muted-foreground mb-4">Supports .xlsx, .xls files</p>
        <label>
          <input type="file" accept=".xlsx,.xls" onChange={handleFileInput} className="hidden" disabled={isUploading} />
          <Button variant="outline" className="gap-2" asChild disabled={isUploading}>
            <span><FileSpreadsheet className="h-4 w-4" /> {isUploading ? "Processing..." : "Browse Files"}</span>
          </Button>
        </label>
      </div>

      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          <div className="stat-card flex items-center gap-3">
            <Users className="h-5 w-5 text-primary" />
            <div><p className="text-sm text-muted-foreground">Devs Created</p><p className="text-xl font-bold">{stats.devs}</p></div>
          </div>
          <div className="stat-card flex items-center gap-3">
            <Code2 className="h-5 w-5 text-accent" />
            <div><p className="text-sm text-muted-foreground">Skills Mapped</p><p className="text-xl font-bold">{stats.skills}</p></div>
          </div>
          <div className="stat-card flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-success" />
            <div><p className="text-sm text-muted-foreground">Database Status</p><p className="text-xl font-bold text-success font-mono uppercase">Synced</p></div>
          </div>
        </div>
      )}

      {preview.length > 0 && (
        <div className="bg-card rounded-lg border mt-6 overflow-hidden">
          <div className="px-5 py-3 border-b bg-muted/20">
            <h3 className="font-semibold text-sm">Source Data Preview</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b bg-muted/50">
                  {Object.keys(preview[0]).map((k) => (
                    <th key={k} className="text-left py-2 px-4 font-medium text-muted-foreground whitespace-nowrap">{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.map((row, i) => (
                  <tr key={i} className="border-b last:border-0 hover:bg-muted/30">
                    {Object.values(row).map((v, j) => (
                      <td key={j} className="py-2 px-4 whitespace-nowrap">{String(v)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}