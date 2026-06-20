import request from "@/utils/request";
import type { BeerNearbyQuery, BeerPubSearchResponse, PubInfo, PubListResponse, PubNearbyQuery, PubNearbyResponse, PubRouteResponse, PubUpdatePayload } from "@/types/pubs";

export const searchPubsByBeerNearby = (params: BeerNearbyQuery) =>
  request.get<BeerPubSearchResponse>("/pubs/by-beer-nearby", { params }).then((res) => res.data);

export const fetchNearbyPubs = (params: PubNearbyQuery) =>
  request.get<PubNearbyResponse>("/pubs/nearby", { params }).then((res) => res.data);

export const fetchAllPubs = () =>
  request.get<PubListResponse>("/pubs", { params: { limit: 999 } }).then((res) => res.data);

export const fetchPubDetail = (pubId: number) =>
  request.get<PubInfo>(`/pubs/${pubId}`).then((res) => res.data);

export const updatePub = (pubId: number, payload: PubUpdatePayload) =>
  request.put<PubInfo>(`/pubs/${pubId}`, payload).then((res) => res.data);

export const uploadPubCover = (pubId: number, file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return request.post<{ cover_url: string }>(`/pubs/${pubId}/cover`, formData).then((res) => res.data);
};

export const fetchPubRoute = (pubId: number, originLng: number, originLat: number) =>
  request
    .get<PubRouteResponse>(`/pubs/${pubId}/route`, {
      params: { origin_lng: originLng, origin_lat: originLat },
    })
    .then((res) => res.data);

