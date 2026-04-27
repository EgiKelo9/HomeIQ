import axiosInstance from "@/lib/axios";
import { TrainResponse, TrainingStatus, PredictRequest, PredictResponse } from "@/types";

export async function triggerTrainingModel(): Promise<TrainResponse> {
    const response = await axiosInstance.post<TrainResponse>("/model/train");
    return response.data;
}

export async function fetchTrainingStatus(): Promise<TrainingStatus> {
    const response = await axiosInstance.get<TrainingStatus>("/model/status");
    return response.data;
}

export async function predictHousePrice(payload: PredictRequest): Promise<PredictResponse> {
    const response = await axiosInstance.post<PredictResponse>("/model/predict", payload);
    return response.data;
}