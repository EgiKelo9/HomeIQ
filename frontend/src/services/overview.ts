import axiosInstance from "@/lib/axios";
import { OverviewResponse } from "@/types";

export async function fetchOverviewSummary(topCities = 8): Promise<OverviewResponse> {
    const response = await axiosInstance.get<OverviewResponse>("/overview/summary", {
        params: {
            top_cities: topCities,
        },
    });

    return response.data;
}
