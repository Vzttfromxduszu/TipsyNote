import type { PubInfo } from "@/types/pubs";
import type { BeerItem } from "@/types/beers";

export interface BeerStyleItem {
  beer: BeerItem;
  pub: PubInfo;
}

export interface BeerStyleSearchResponse {
  items: BeerStyleItem[];
  offset: number;
  limit: number;
}

export interface BeerStyleQuery {
  style: string;
  offset?: number;
  limit?: number;
}
