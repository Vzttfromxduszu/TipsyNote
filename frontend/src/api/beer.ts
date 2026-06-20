import request from "@/utils/request";
import type { BeerCreatePayload, BeerItem, BeerListResponse, BeerUpdatePayload } from "@/types/beer";

/** 获取某酒馆的全部酒款 */
export const fetchBeersByPub = (pubId: number) =>
  request
    .get<BeerListResponse>("/beers", { params: { pub_id: pubId, limit: 200 } })
    .then((res) => res.data);

/** 创建酒款 */
export const createBeer = (payload: BeerCreatePayload) =>
  request.post<BeerItem>("/beers", payload).then((res) => res.data);

/** 更新酒款 */
export const updateBeer = (beerId: number, payload: BeerUpdatePayload) =>
  request.put<BeerItem>(`/beers/${beerId}`, payload).then((res) => res.data);

/** 删除酒款 */
export const deleteBeer = (beerId: number) =>
  request.delete(`/beers/${beerId}`).then((res) => res.data);
