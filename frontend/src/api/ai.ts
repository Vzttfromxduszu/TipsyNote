import request from "@/utils/request";
import type { AIRecommendRequest, AIRecommendResponse } from "@/types/ai";

export const fetchAIRecommend = (payload: AIRecommendRequest) =>
  request.post<AIRecommendResponse>("/ai/recommend", payload).then((res) => res.data);
