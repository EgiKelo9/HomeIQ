"use client"

import { useEffect, useState } from "react";
import { BreadcrumbType } from "@/types";
import { AppHeader } from "@/components/main/app-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, PieChart, Pie, Cell, Legend } from "recharts";
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { fetchModelMetrics, fetchFeatureImportance, fetchDistributionData, fetchMarketSegments } from "@/services/analytics";
import { ModelMetrics, FeatureImportance, DistributionData, MarketSegment } from "@/types";
import Heading from "@/components/ui/heading";

const chartConfigDistCount = {
  count: { label: "Jumlah Listing", color: "hsl(var(--chart-1))" },
} satisfies ChartConfig;

const chartConfigDistPrice = {
  avg_price: { label: "Rata-rata Harga", color: "hsl(var(--chart-2))" },
} satisfies ChartConfig;

const chartConfigFeatureImp = {
  importance: { label: "Bobot Pengaruh", color: "hsl(var(--chart-3))" },
} satisfies ChartConfig;

const chartConfigSegments = {
  count: { label: "Jumlah Properti" },
} satisfies ChartConfig;

export default function Page() {
  const breadcrumbs: BreadcrumbType[] = [
    { label: "HomeIQ", href: "/" },
    { label: "Analytics", href: "/analytics" },
  ];

  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [featureImp, setFeatureImp] = useState<FeatureImportance[]>([]);
  const [distribution, setDistribution] = useState<DistributionData[]>([]);
  const [segments, setSegments] = useState<MarketSegment[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const [metricsData, featuresData, distData, segData] = await Promise.all([
          fetchModelMetrics(),
          fetchFeatureImportance(),
          fetchDistributionData(),
          fetchMarketSegments()
        ]);
        setMetrics(metricsData);
        setFeatureImp(featuresData);
        setDistribution(distData);
        setSegments(segData);
      } catch (error: any) {
        console.error("Gagal memuat data analitik:", error);
        setErrorMessage(
          error?.response?.data?.detail || "Gagal memuat data analitik. Pastikan model sudah ditraining."
        );
      } finally {
        setIsLoading(false);
      }
    };
    void loadData();
  }, []);

  const formatRupiah = (value: number) => {
    if (value >= 1_000_000_000) return `Rp ${(value / 1_000_000_000).toFixed(1)} Miliar`;
    if (value >= 1_000_000) return `Rp ${(value / 1_000_000).toFixed(0)} Juta`;
    return `Rp ${value.toLocaleString("id-ID")}`;
  };

  const formatDate = (isoString?: string) => {
    if (!isoString) return "-";
    return new Date(isoString).toLocaleString("id-ID", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  if (errorMessage && !isLoading) {
    return (
      <>
        <AppHeader breadcrumbs={breadcrumbs} />
        <div className="p-6 max-w-4xl mx-auto w-full">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Peringatan Data Kosong</AlertTitle>
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        </div>
      </>
    );
  }

  return (
    <>
      <AppHeader breadcrumbs={breadcrumbs} />
      <div className="flex flex-1 flex-col gap-6 p-4 pt-2 w-full mx-auto">
        <Heading title="Analytics" description="Analisis data properti terbaru." />
        {/* Top Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Akurasi Model (R² Score)</CardDescription>
              <CardTitle className="text-3xl text-primary">
                {isLoading ? <Skeleton className="h-9 w-24" /> : `${((metrics?.r2_score || 0) * 100).toFixed(2)}%`}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground">
              Model mampu menjelaskan {((metrics?.r2_score || 0) * 100).toFixed(1)}% variansi harga.
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Mean Absolute Error (MAE)</CardDescription>
              <CardTitle className="text-2xl">
                {isLoading ? <Skeleton className="h-8 w-32" /> : formatRupiah(metrics?.mae || 0)}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground">Rata-rata penyimpangan absolut prediksi.</CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Root Mean Squared Error (RMSE)</CardDescription>
              <CardTitle className="text-2xl">
                {isLoading ? <Skeleton className="h-8 w-32" /> : formatRupiah(metrics?.rmse || 0)}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground">Penalti lebih besar untuk error ekstrem.</CardContent>
          </Card>
        </div>

        <Tabs defaultValue="insights" className="w-full mt-2">
          <TabsList className="grid w-full grid-cols-3 h-auto p-1 bg-muted">
            <TabsTrigger value="insights" className="py-1.5 text-sm">
              <span>Insight</span>
              <span className="hidden sm:block">& Distribusi</span>
            </TabsTrigger>
            <TabsTrigger value="performance" className="py-1.5 text-sm">
              <span>Performa</span>
              <span className="hidden sm:block">Model ML</span>
            </TabsTrigger>
            <TabsTrigger value="segmentation" className="py-1.5 text-sm">
              <span>Segmentasi</span>
              <span className="hidden sm:block">Pasar</span>
            </TabsTrigger>
          </TabsList>

          {/* TAB 1: INSIGHT & DISTRIBUSI */}
          <TabsContent value="insights" className="mt-4 space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="col-span-1">
                <CardHeader>
                  <CardTitle>Volume Listing per Kota</CardTitle>
                  <CardDescription>Distribusi jumlah data rumah tersimpan.</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? <Skeleton className="h-80 w-full" /> : (
                    <ChartContainer config={chartConfigDistCount} className="h-80 w-full">
                      <BarChart accessibilityLayer data={distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="city" tickLine={false} axisLine={false} tickMargin={8} tick={{ fontSize: 11 }} angle={-15} textAnchor="end" height={60} />
                        <YAxis tickLine={false} axisLine={false} tickMargin={8} tick={{ fontSize: 12 }} />
                        <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
                        <Bar dataKey="count" fill="var(--color-count)" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ChartContainer>
                  )}
                </CardContent>
              </Card>

              <Card className="col-span-1">
                <CardHeader>
                  <CardTitle>Rata-rata Harga per Kota</CardTitle>
                  <CardDescription>Perbandingan harga rata-rata antar kota.</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? <Skeleton className="h-80 w-full" /> : (
                    <ChartContainer config={chartConfigDistPrice} className="h-80 w-full">
                      <BarChart accessibilityLayer data={distribution} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="city" tickLine={false} axisLine={false} tickMargin={8} tick={{ fontSize: 11 }} angle={-15} textAnchor="end" height={60} />
                        <YAxis tickLine={false} axisLine={false} tickMargin={8} tick={{ fontSize: 12 }} tickFormatter={(value) => `${Math.round(value)} JT`} />
                        <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="line" />} />
                        <Bar dataKey="avg_price" fill="var(--color-avg_price)" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ChartContainer>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* TAB 2: PERFORMA MODEL */}
          <TabsContent value="performance" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Feature Importance (Random Forest)</CardTitle>
                <CardDescription>Seberapa besar bobot fitur terhadap penentuan harga akhir.</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? <Skeleton className="h-80 w-full" /> : (
                  <ChartContainer config={chartConfigFeatureImp} className="h-80 w-full">
                    <BarChart accessibilityLayer data={featureImp} layout="vertical" margin={{ top: 10, right: 30, left: 60, bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" domain={[0, 'auto']} tickLine={false} axisLine={false} tickMargin={8} tickFormatter={(tick) => `${(tick * 100).toFixed(0)}%`} />
                      <YAxis dataKey="feature" type="category" tickLine={false} axisLine={false} tickMargin={8} tick={{ fontSize: 12 }} />
                      <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="line" />} />
                      <Bar dataKey="importance" fill="var(--color-importance)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ChartContainer>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 3: SEGMENTASI PASAR */}
          <TabsContent value="segmentation" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Cluster Properti (K-Means Segmentation)</CardTitle>
                <CardDescription>Pengelompokan data listing berdasarkan kedekatan fitur dan harga.</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col md:flex-row items-center justify-center gap-8 min-h-87.5">
                {isLoading ? <Skeleton className="h-80 w-full" /> : (
                  <>
                    <div className="w-full md:w-1/2 h-80">
                      <ChartContainer config={chartConfigSegments} className="h-full w-full">
                        <PieChart>
                          <Pie
                            data={segments}
                            cx="50%"
                            cy="50%"
                            innerRadius={70}
                            outerRadius={110}
                            paddingAngle={5}
                            dataKey="count"
                            nameKey="cluster_name"
                          >
                            {segments.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                          <Legend verticalAlign="bottom" height={36} />
                        </PieChart>
                      </ChartContainer>
                    </div>

                    <div className="w-full md:w-1/2 space-y-4">
                      <h4 className="font-semibold text-lg border-b pb-2">Karakteristik Cluster</h4>
                      {segments.map((seg, idx) => (
                        <div key={idx} className="flex items-start gap-3">
                          <div className="w-4 h-4 rounded-full mt-1 shrink-0" style={{ backgroundColor: seg.color }} />
                          <div>
                            <p className="font-medium">{seg.cluster_name} <span className="text-muted-foreground font-normal">({seg.count} properti)</span></p>
                            <p className="text-sm text-muted-foreground">{seg.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

        </Tabs>
      </div>
    </>
  );
}