import request from "@/utils/request";
import type {
  BeerStyleBrief,
  BeerStyleDetail,
  BeerSearchResult,
  BeerSuggestItem,
  StyleBeersResponse,
  BeerDetailWithPosts,
} from "@/types/beerWiki";

// ── 搜索联想 ──
export const fetchSuggestions = (q: string, limit = 8) =>
  request
    .get<{ items: BeerSuggestItem[] }>("/beer-wiki/suggest", { params: { q, limit } })
    .then((res) => res.data.items);

// ── 搜索 ──
export const searchBeerWiki = (q: string, limit = 10) =>
  request
    .get<BeerSearchResult>("/beer-wiki/search", { params: { q, limit } })
    .then((res) => res.data);

// ── 所有品类 ──
export const fetchAllStyles = () =>
  request.get<BeerStyleBrief[]>("/beer-wiki/styles").then((res) => res.data);

// ── 品类详情 + 酒款列表 ──
export const fetchStyleDetail = (styleId: number) =>
  request.get<StyleBeersResponse>(`/beer-wiki/styles/${styleId}`).then((res) => res.data);

// ── 品类百科完整详情（含雷达图数据） ──
export const fetchStyleDetailFull = (styleId: number) =>
  request.get<BeerStyleDetail>(`/beer-wiki/styles/${styleId}/detail`).then((res) => res.data);

// ── 所有经典酒款 ──
export const fetchClassicBeers = () =>
  request.get<BeerItemBrief[]>("/beer-wiki/classics").then((res) => res.data);

// ── 酒款详情 + 社区联动 ──
export const fetchBeerDetail = (beerId: number) =>
  request.get<BeerDetailWithPosts>(`/beer-wiki/items/${beerId}`).then((res) => res.data);
