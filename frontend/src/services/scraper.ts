import axiosInstance from "@/lib/axios";
import { TaskInfo, TriggerResponse, ProviderInfo, TaskSummary } from "@/types";

export async function triggerScraping(maxPages: number = 0): Promise<TriggerResponse> {
    const response = await axiosInstance.post<TriggerResponse>(`/scraper/trigger?max_pages=${maxPages}`);
    return response.data;
}

export async function fetchTasks(): Promise<TaskInfo[]> {
    const response = await axiosInstance.get<TaskInfo[]>("/scraper/tasks");
    return response.data;
}

export async function cancelTask(taskId: string): Promise<any> {
    const response = await axiosInstance.delete(`/scraper/tasks/${taskId}/cancel`);
    return response.data;
}

export async function fetchProviders(): Promise<Record<string, ProviderInfo>> {
    const response = await axiosInstance.get<Record<string, ProviderInfo>>("/scraper/providers");
    return response.data;
}

export async function fetchSummary(): Promise<TaskSummary> {
    const response = await axiosInstance.get<TaskSummary>("/scraper/summary");
    return response.data;
}