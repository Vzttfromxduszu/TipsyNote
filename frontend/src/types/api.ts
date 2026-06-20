export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface ApiListResponse<T> {
  items: T[];
  offset: number;
  limit: number;
}
