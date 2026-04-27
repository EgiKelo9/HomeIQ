"use client";

import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { BreadcrumbType, OverviewResponse } from "@/types";
import { AppHeader } from "@/components/main/app-header"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Skeleton } from "@/components/ui/skeleton";
import { fetchOverviewSummary } from "@/services/overview";
import Heading from "@/components/ui/heading";

export default function Page() {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const breadcrumbs: BreadcrumbType[] = [
    { label: "HomeIQ", href: "/" },
    { label: "Overview", href: "/overview" },
  ];

  const chartConfig = {
    average_price: {
      label: "Rata-rata Harga",
      color: "hsl(var(--chart-1))",
    },
    listing_count: {
      label: "Jumlah Listing",
      color: "hsl(var(--chart-2))",
    },
  } satisfies ChartConfig;

  useEffect(() => {
    const loadOverview = async () => {
      try {
        setIsLoading(true);
        setErrorMessage(null);
        const response = await fetchOverviewSummary();
        setOverview(response);
      } catch {
        setErrorMessage("Gagal memuat data overview. Pastikan backend sedang berjalan.");
      } finally {
        setIsLoading(false);
      }
    };

    void loadOverview();
  }, []);

  const formattedLastUpdated = useMemo(() => {
    if (!overview?.last_updated) {
      return "-";
    }

    return new Date(overview.last_updated).toLocaleString("id-ID", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  }, [overview?.last_updated]);

  return (
    <>
      <AppHeader breadcrumbs={breadcrumbs} />
      <div className="flex flex-1 flex-col gap-4 p-4 pt-2">
        <Heading title="Overview" description="Ringkasan data properti terbaru." />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
          {isLoading && Array.from({ length: 4 }).map((_, index) => (
            <Card key={`skeleton-${index}`} className="flex-1 w-full">
              <CardHeader>
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-8 w-3/4" />
              </CardHeader>
              <CardFooter>
                <Skeleton className="h-4 w-full" />
              </CardFooter>
            </Card>
          ))}

          {!isLoading && overview?.cards.map((metric) => (
            <Card key={metric.key} className="flex-1 w-full">
              <CardHeader>
                <CardDescription>{metric.label}</CardDescription>
                <CardTitle className="text-2xl font-semibold tabular-nums">
                  {metric.formatted_value}
                </CardTitle>
              </CardHeader>
              <CardFooter>
                <div className="text-sm text-muted-foreground">
                  {metric.note ?? "Data harga rumah terbaru."}
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Rata-rata Harga per Kota</CardTitle>
            <CardDescription>
              Perbandingan harga rata-rata rumah berdasarkan kota.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading && <Skeleton className="h-80 w-full" />}

            {!isLoading && !errorMessage && overview && (
              <ChartContainer config={chartConfig} className="h-80 w-full">
                <BarChart
                  accessibilityLayer
                  data={overview.chart}
                  margin={{ left: 8, right: 8, top: 8 }}
                >
                  <CartesianGrid vertical={false} />
                  <XAxis
                    dataKey="city"
                    tickLine={false}
                    axisLine={false}
                    tickMargin={8}
                  />
                  <YAxis
                    yAxisId="left"
                    tickLine={false}
                    axisLine={false}
                    tickMargin={8}
                    tickFormatter={(value) => `Rp ${(Number(value) / 1_000_000_000).toFixed(1)}B`}
                  />
                  <YAxis yAxisId="right" orientation="right" hide />
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent indicator="line" />}
                  />
                  <Bar
                    yAxisId="left"
                    dataKey="average_price"
                    fill="var(--color-average_price)"
                    radius={6}
                  />
                  <Bar
                    yAxisId="right"
                    dataKey="listing_count"
                    fill="var(--color-listing_count)"
                    radius={6}
                    fillOpacity={0.35}
                  />
                </BarChart>
              </ChartContainer>
            )}

            {!isLoading && errorMessage && (
              <div className="rounded-md border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive">
                {errorMessage}
              </div>
            )}
          </CardContent>
          <CardFooter>
            <div className="text-sm text-muted-foreground">
              Last update data: {formattedLastUpdated}
            </div>
          </CardFooter>
        </Card>

        {!isLoading && !errorMessage && overview && overview.chart.length === 0 && (
          <div className="text-sm text-muted-foreground">
            Data chart belum tersedia.
          </div>
        )}

        {!isLoading && !errorMessage && !overview && (
          <div className="text-sm text-muted-foreground">
            Tidak ada data overview yang tersedia.
          </div>
        )}

        {!isLoading && errorMessage && (
          <div className="text-sm text-muted-foreground">
            Silakan cek endpoint /api/overview/summary pada backend.
          </div>
        )}
      </div>
    </>
  );
}
