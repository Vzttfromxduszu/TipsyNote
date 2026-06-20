/** 帖子 */
export interface PostItem {
  id: number;
  user_id: number;
  title: string;
  content: string;
  like_count: number;
  comment_count: number;
  status: number;
  created_at: string;
  updated_at: string;
  user_nickname: string | null;
  user_avatar: string | null;
  liked: boolean;
}

/** 帖子列表响应 */
export interface PostListResponse {
  items: PostItem[];
  offset: number;
  limit: number;
}

/** 创建帖子参数 */
export interface PostCreatePayload {
  title: string;
  content: string;
}

/** 更新帖子参数 */
export interface PostUpdatePayload {
  title?: string;
  content?: string;
}

/** 评论 */
export interface CommentItem {
  id: number;
  post_id: number;
  user_id: number;
  content: string;
  created_at: string;
  user_nickname: string | null;
  user_avatar: string | null;
}

/** 评论列表响应 */
export interface CommentListResponse {
  items: CommentItem[];
}

/** 创建评论参数 */
export interface CommentCreatePayload {
  content: string;
}

/** 点赞切换响应 */
export interface LikeToggleResponse {
  liked: boolean;
  like_count: number;
}

/** 点赞状态响应 */
export interface LikeStatusResponse {
  liked: boolean;
}
