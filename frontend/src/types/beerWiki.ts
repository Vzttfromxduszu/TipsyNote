/** 品类简要 */
export interface BeerStyleBrief {
  id: number;
  name: string;
  name_en: string | null;
  category: string;
  description: string | null;
  icon: string | null;
}

/** 品类详情（含雷达图数据） */
export interface BeerStyleDetail {
  id: number;
  name: string;
  name_en: string | null;
  category: string;
  description: string | null;
  origin_story: string | null;
  tasting_notes: string | null;
  ibu_min: number | null;
  ibu_max: number | null;
  srm_min: number | null;
  srm_max: number | null;
  abv_min: number | null;
  abv_max: number | null;
  icon: string | null;
}

/** 酒款简要 */
export interface BeerItemBrief {
  id: number;
  name: string;
  name_en: string | null;
  brewery: string | null;
  country: string | null;
  style_name: string | null;
  abv: number | null;
  ibu: number | null;
  image_url: string | null;
  is_classic: number;
}

/** 酒款详情 */
export interface BeerItemDetail {
  id: number;
  name: string;
  name_en: string | null;
  brewery: string | null;
  country: string | null;
  style_id: number | null;
  style_name: string | null;
  description: string | null;
  abv: number | null;
  ibu: number | null;
  og: number | null;
  image_url: string | null;
  flavor_tags: string | null;
  is_classic: number;
}

/** 搜索联想项 */
export interface BeerSuggestItem {
  type: "style" | "beer";
  id: number;
  name: string;
  subtitle: string | null;
}

/** 搜索结果 */
export interface BeerSearchResult {
  styles: BeerStyleBrief[];
  beers: BeerItemBrief[];
}

/** 品类+酒款 */
export interface StyleBeersResponse {
  style: BeerStyleBrief;
  beers: BeerItemBrief[];
  classic_beers: BeerItemBrief[];
}

/** 相关帖子（社区联动） */
export interface RelatedPost {
  id: number;
  title: string;
  content: string;
  like_count: number;
  comment_count: number;
  created_at: string | null;
  user_nickname: string | null;
  user_avatar: string | null;
  liked: boolean;
}

/** 酒款详情 + 社区联动 */
export interface BeerDetailWithPosts {
  beer: BeerItemDetail;
  related_posts: RelatedPost[];
}
