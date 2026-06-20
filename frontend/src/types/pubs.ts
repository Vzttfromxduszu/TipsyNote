export interface PubInfo {
  id: number;
  merchant_user_id: number;
  pub_name: string;
  cover_url: string | null;
  address: string | null;
  longitude: number | null;
  latitude: number | null;
  contact_phone: string | null;
  business_hours: string | null;
  status: number;
}

export interface BeerPubItem {
  pub: PubInfo;
  beer_name: string;
  brewery_name: string | null;
  style?: string | null;
  price: number | null;
  status: number;
  distance_km?: number;
}

export interface BeerPubSearchResponse {
  items: BeerPubItem[];
  offset: number;
  limit: number;
}

export interface BeerNearbyQuery {
  beer_name: string;
  lat: number;
  lng: number;
  radius_km: number;
  in_stock_only?: boolean;
  offset?: number;
  limit?: number;
}

export interface PubRouteResponse {
  mode: "walking" | "driving";
  distance_m: number;
  duration_min: number;
  origin: { lng: number; lat: number };
  destination: { lng: number; lat: number };
}

export interface PubNearbyItem {
  pub: PubInfo;
  distance_km: number;
}

export interface PubNearbyResponse {
  items: PubNearbyItem[];
  total: number;
}

export interface PubListResponse {
  items: PubInfo[];
  offset: number;
  limit: number;
}

export interface PubNearbyQuery {
  lat: number;
  lng: number;
  radius_km?: number;
  offset?: number;
  limit?: number;
}

export interface PubUpdatePayload {
  pub_name?: string;
  cover_url?: string;
  address?: string;
  city?: string;
  longitude?: number;
  latitude?: number;
  contact_phone?: string;
  business_hours?: string;
  status?: number;
}
