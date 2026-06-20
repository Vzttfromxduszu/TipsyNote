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
