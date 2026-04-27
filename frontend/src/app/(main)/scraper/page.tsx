"use client";

import { useState, useEffect } from "react";
import { BreadcrumbType } from "@/types";
import { AppHeader } from "@/components/main/app-header";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { triggerScraping, fetchTasks, cancelTask, fetchProviders, fetchSummary } from "@/services/scraper";
import { TaskInfo, ProviderInfo, TaskSummary } from "@/types";
import Heading from "@/components/ui/heading";

const STORAGE_KEY_SCRAPER_HISTORY = "homeiq_scraper_history";
const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;

// Helper LocalStorage
const saveWithExpiry = (key: string, value: any) => {
  const item = { value, timestamp: new Date().getTime() };
  localStorage.setItem(key, JSON.stringify(item));
};

const getWithExpiry = (key: string) => {
  const itemStr = localStorage.getItem(key);
  if (!itemStr) return null;
  const item = JSON.parse(itemStr);
  const now = new Date().getTime();
  if (now - item.timestamp > TWENTY_FOUR_HOURS) {
    localStorage.removeItem(key);
    return null;
  }
  return item.value;
};

export default function Page() {
  const breadcrumbs: BreadcrumbType[] = [
    { label: "HomeIQ", href: "/" },
    { label: "Scraper", href: "/scraper" },
  ];

  // --- States ---
  const [maxPages, setMaxPages] = useState<string>("0");
  const [isTriggering, setIsTriggering] = useState(false);
  const [triggerMessage, setTriggerMessage] = useState<string | null>(null);

  const [tasks, setTasks] = useState<TaskInfo[]>([]);
  const [providers, setProviders] = useState<Record<string, ProviderInfo>>({});
  const [summary, setSummary] = useState<TaskSummary | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // --- Functions ---
  const loadInitialData = async () => {
    setIsLoadingData(true);
    try {
      const [providersData, summaryData] = await Promise.all([
        fetchProviders(),
        fetchSummary(),
      ]);
      setProviders(providersData);
      setSummary(summaryData);

      const localTasks: TaskInfo[] = getWithExpiry(STORAGE_KEY_SCRAPER_HISTORY) || [];
      const remoteTasks: TaskInfo[] = await fetchTasks();

      const taskMap = new Map<string, TaskInfo>();
      localTasks.forEach(t => taskMap.set(t.task_id, t));
      remoteTasks.forEach(t => taskMap.set(t.task_id, t));

      const mergedTasks = Array.from(taskMap.values()).sort((a, b) => {
        const dateA = a.queued_at ? new Date(a.queued_at).getTime() : 0;
        const dateB = b.queued_at ? new Date(b.queued_at).getTime() : 0;
        return dateB - dateA;
      });

      setTasks(mergedTasks);
      saveWithExpiry(STORAGE_KEY_SCRAPER_HISTORY, mergedTasks);
    } catch (error) {
      console.error("Gagal memuat data scraper:", error);
    } finally {
      setIsLoadingData(false);
    }
  };

  useEffect(() => {
    void loadInitialData();
  }, []);

  const handleTriggerScraping = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsTriggering(true);
    setTriggerMessage(null);
    try {
      const limit = maxPages === "" ? 0 : Number(maxPages);
      const res = await triggerScraping(limit);
      setTriggerMessage(res.message);
      await loadInitialData();
    } catch (error: any) {
      setTriggerMessage(error?.response?.data?.detail || "Gagal memicu scraper.");
    } finally {
      setIsTriggering(false);
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      await cancelTask(taskId);
      await loadInitialData();
    } catch (error) {
      console.error("Gagal membatalkan task:", error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case "SUCCESS": return "bg-green-500 hover:bg-green-600";
      case "STARTED": return "bg-blue-500 hover:bg-blue-600";
      case "FAILURE": return "bg-red-500 hover:bg-red-600";
      case "REVOKED": return "bg-gray-500 hover:bg-gray-600";
      default: return "bg-yellow-500 hover:bg-yellow-600";
    }
  };

  return (
    <>
      <AppHeader breadcrumbs={breadcrumbs} />
      <div className="flex flex-1 flex-col gap-6 p-4 pt-2 w-full mx-auto">
        <Heading title="Scraper" description="Panel kontrol untuk memicu dan memantau proses scraping data properti." />
        <Tabs defaultValue="trigger" className="w-full">
          <TabsList className="grid w-full grid-cols-3 h-auto p-1 bg-muted">
            <TabsTrigger value="trigger" className="py-1.5 text-sm font-medium">
              <span>Scraping</span>
              <span className="hidden sm:block">Panel</span>
            </TabsTrigger>
            <TabsTrigger value="providers" className="py-1.5 text-sm font-medium">
              <span>Data Provider</span>
              <span className="hidden sm:block">& URL</span>
            </TabsTrigger>
            <TabsTrigger value="history" className="py-1.5 text-sm font-medium">
              <span>Riwayat</span>
              <span className="hidden sm:block">& Log</span>
            </TabsTrigger>
          </TabsList>

          {/* TAB 1: TRIGGER SCRAPING */}
          <TabsContent value="trigger" className="mt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Mulai Proses Scraping</CardTitle>
                    <CardDescription>
                      Picu scraper untuk mengambil data rumah terbaru secara paralel.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleTriggerScraping} className="space-y-4" suppressHydrationWarning>
                      <div className="space-y-2">
                        <Label htmlFor="maxPages">Batas Halaman per URL (Max Pages)</Label>
                        <Input
                          id="maxPages"
                          type="number"
                          min="0"
                          max="100"
                          value={maxPages}
                          onChange={(e) => setMaxPages(e.target.value)}
                          placeholder="Isi 0 untuk scrape semua halaman"
                          suppressHydrationWarning
                        />
                        <p className="text-xs text-muted-foreground">Isi dengan 0 untuk melakukan scrape penuh. Batasi untuk pengujian agar tidak overload.</p>
                      </div>

                      <Button type="submit" disabled={isTriggering} className="w-full h-12 text-base">
                        {isTriggering ? "Memicu Tasks..." : "Mulai Scraping Sekarang"}
                      </Button>
                    </form>

                    {triggerMessage && (
                      <div className="mt-4 rounded-md border border-primary/40 bg-primary/5 p-4 text-sm text-primary">
                        {triggerMessage}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="md:col-span-1">
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle>Ringkasan Status</CardTitle>
                    <CardDescription>Status task saat ini di server</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {summary ? (
                      <div className="space-y-3">
                        <div className="flex justify-between py-2 border-b">
                          <span className="font-medium">Total Tasks</span>
                          <span className="font-bold">{summary.total}</span>
                        </div>
                        {Object.entries(summary.by_status).map(([status, count]) => (
                          <div key={status} className="flex justify-between items-center text-sm">
                            <span className="text-muted-foreground">{status}</span>
                            <Badge className={getStatusColor(status)}>{count as number}</Badge>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">Memuat ringkasan...</p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* TAB 2: PROVIDERS */}
          <TabsContent value="providers" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Data Sumber Scraping (Providers)</CardTitle>
                <CardDescription>Daftar situs dan URL spesifik yang menjadi target pengambilan data.</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoadingData ? (
                  <p className="text-sm text-muted-foreground">Memuat data providers...</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(providers).map(([providerName, info]) => (
                      <div key={providerName} className="border rounded-lg p-4 bg-card">
                        <div className="flex justify-between items-center mb-3">
                          <h3 className="text-lg font-bold capitalize">{providerName}</h3>
                          <Badge variant="secondary">{info.url_count} URL</Badge>
                        </div>
                        <ul className="space-y-2 text-sm text-muted-foreground break-all">
                          {info.urls.map((url, idx) => (
                            <li key={idx} className="bg-muted/50 p-2 rounded line-clamp-2" title={url}>
                              {url}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 3: HISTORY & LOGS */}
          <TabsContent value="history" className="mt-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Riwayat Task Scraping</CardTitle>
                  <CardDescription>Log data yang dipicu dalam 24 jam terakhir.</CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={loadInitialData} disabled={isLoadingData}>
                  {isLoadingData ? "Memuat..." : "Refresh Data"}
                </Button>
              </CardHeader>
              <CardContent>
                {tasks.length === 0 ? (
                  <div className="py-10 text-center border-2 border-dashed rounded-lg">
                    <p className="text-sm text-muted-foreground">Belum ada riwayat task scraping.</p>
                  </div>
                ) : (
                  <div className="rounded-md border overflow-hidden">
                    <table className="w-full text-sm">
                      <thead className="bg-muted">
                        <tr>
                          <th className="px-4 py-3 text-left font-medium">Task ID / Waktu</th>
                          <th className="px-4 py-3 text-left font-medium">Sumber & URL</th>
                          <th className="px-4 py-3 text-center font-medium">Status</th>
                          <th className="px-4 py-3 text-right font-medium">Aksi</th>
                        </tr>
                      </thead>
                      <tbody>
                        {tasks.map((task) => (
                          <tr key={task.task_id} className="border-t">
                            <td className="px-4 py-3">
                              <div className="font-mono text-xs text-primary">{task.task_id.substring(0, 8)}...</div>
                              <div className="text-xs text-muted-foreground mt-1">
                                {task.finished_at ? new Date(task.finished_at).toLocaleString('id-ID') : 
                                  task.started_at ? new Date(task.started_at).toLocaleString('id-ID') : 
                                  task.queued_at ? new Date(task.queued_at).toLocaleString('id-ID') : '-'}
                              </div>
                            </td>
                            <td className="px-4 py-3 max-w-50">
                              <div className="font-medium capitalize">{task.provider}</div>
                              <div className="text-xs text-muted-foreground truncate" title={task.url}>
                                {task.url}
                              </div>
                              {task.error && <div className="text-xs text-red-500 mt-1 line-clamp-1">{task.error}</div>}
                            </td>
                            <td className="px-4 py-3 text-center">
                              <Badge className={getStatusColor(task.status)}>{task.status}</Badge>
                            </td>
                            <td className="px-4 py-3 text-right">
                              {task.status.toUpperCase() === "QUEUED" && (
                                <Button
                                  variant="destructive"
                                  size="sm"
                                  onClick={() => handleCancelTask(task.task_id)}
                                >
                                  Batalkan
                                </Button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

        </Tabs>
      </div>
    </>
  );
}