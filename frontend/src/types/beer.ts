export interface BeerItem {
  id: number;
  pub_id: number;
  beer_name: string;
  brewery_name: string;
  style?: string | null;
  abv?: number | null;
  volume_ml?: number | null;
  price?: number | null;
  status: number;
}

export interface BeerListResponse {
  items: BeerItem[];
  offset: number;
  limit: number;
}

export interface BeerCreatePayload {
  pub_id: number;
  beer_name: string;
  brewery_name: string;
  style?: string;
  abv?: number;
  volume_ml?: number;
  price?: number;
  status?: number;
}

export interface BeerUpdatePayload {
  beer_name?: string;
  brewery_name?: string;
  style?: string;
  abv?: number;
  volume_ml?: number;
  price?: number;
  status?: number;
}
