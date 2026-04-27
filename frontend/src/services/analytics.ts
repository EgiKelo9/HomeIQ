import axiosInstance from "@/lib/axios";
import { ModelMetrics, FeatureImportance, DistributionData, MarketSegment } from "@/types";

export async function fetchModelMetrics(): Promise<ModelMetrics> {
    const response = await axiosInstance.get<ModelMetrics>("/analytics/metrics");
    return response.data;
}

export async function fetchFeatureImportance(): Promise<FeatureImportance[]> {
    const response = await axiosInstance.get<FeatureImportance[]>("/analytics/feature-importance");
    return response.data;
}

export async function fetchDistributionData(): Promise<DistributionData[]> {
    const response = await axiosInstance.get<DistributionData[]>("/analytics/distribution");
    return response.data;
}

export async function fetchMarketSegments(): Promise<MarketSegment[]> {
    const response = await axiosInstance.get<MarketSegment[]>("/analytics/segments");
    return response.data;
}
