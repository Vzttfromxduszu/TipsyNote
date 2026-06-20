export interface AIRecommendRequest {
  mood: string;
  tastes: string[];
  scene: string;
  style: string;
}

export interface AIRecommendItem {
  beer_name: string;
  brewery_name: string;
  reason: string;
}

export interface AIRecommendResponse {
  items: AIRecommendItem[];
}
