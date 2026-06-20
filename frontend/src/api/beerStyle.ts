import request from "@/utils/request";
import type { BeerStyleSearchResponse, BeerStyleQuery } from "@/types/beerStyle";

export const searchBeersByStyle = (params: BeerStyleQuery) =>
  request.get<BeerStyleSearchResponse>("/beers/by-style", { params }).then((res) => res.data);
