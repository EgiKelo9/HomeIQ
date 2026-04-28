import * as React from "react";
import { LucideIcon } from "lucide-react";
import { ColumnDef } from "@tanstack/react-table";

export interface BaseEntity {
    id: number;
    [key: string]: any;
}

export interface BaseFormProps<T> {
    isEdit?: boolean;
    isReadOnly?: boolean;
    initialData?: Partial<T>;
    onSuccess?: () => void;
    onCancel?: () => void;
}

export interface BreadcrumbType {
    label: string;
    href: string;
}

export interface OverviewMetric {
    key: string;
    label: string;
    value: number;
    formatted_value: string;
    note?: string;
}

export interface OverviewChartItem {
    city: string;
    average_price: number;
    listing_count: number;
    formatted_average_price: string;
}

export interface OverviewResponse {
    total_listings: number;
    average_price: number;
    median_price: number;
    max_price: number;
    cards: OverviewMetric[];
    chart: OverviewChartItem[];
    last_updated?: string | null;
}

export interface PredictRequest {
    bedrooms: number;
    bathrooms: number;
    building_size_m2: number;
    land_size_m2: number;
    city: string;
    district: string;
}

export interface PredictResponse {
    predicted_price: number;
}

export interface TrainResponse {
    message: string;
    status: string;
}

export interface TrainingStatus {
    status: "IDLE" | "RUNNING" | "COMPLETED" | "FAILED";
    progress?: number;
    last_error?: string | null;
    [key: string]: any;
}

export interface TaskInfo {
    task_id: string;
    status: string;
    provider: string;
    city: string;
    url?: string;
    queued_at?: string;
    started_at?: string;
    finished_at?: string;
    result?: any;
    error?: string;
}

export interface TriggerResponse {
    message: string;
    total_tasks: number;
    tasks: TaskInfo[];
}

export interface ProviderInfo {
    url_count: number;
    urls: string[];
}

export interface TaskSummary {
    total: number;
    by_status: Record<string, number>;
}

export interface ModelMetrics {
    r2_score: number;
    rmse: number;
    mae: number;
    silhouette_score?: number;
    last_trained: string;
}

export interface FeatureImportance {
    feature: string;
    importance: number;
}

export interface DistributionData {
    city: string;
    count: number;
    avg_price: number;
}

export interface MarketSegment {
    cluster_name: string;
    count: number;
    description: string;
    color: string;
}
