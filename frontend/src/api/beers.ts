import request from "@/utils/request";
import type { BeerListResponse } from "@/types/beers";

export const fetchBeersByPub = (pubId: number) =>
  request
    .get<BeerListResponse>("/beers", { params: { pub_id: pubId, offset: 0, limit: 100 } })
    .then((res) => res.data);
