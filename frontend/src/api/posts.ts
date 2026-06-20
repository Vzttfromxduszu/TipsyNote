import request from "@/utils/request";
import type {
  PostItem,
  PostListResponse,
  PostCreatePayload,
  PostUpdatePayload,
  CommentItem,
  CommentListResponse,
  CommentCreatePayload,
  LikeToggleResponse,
  LikeStatusResponse,
} from "@/types/posts";

// ========== 帖子 API ==========

/** 获取帖子列表 */
export const fetchPosts = (params?: {
  keyword?: string;
  user_id?: number;
  offset?: number;
  limit?: number;
}) =>
  request.get<PostListResponse>("/posts", { params }).then((res) => res.data);

/** 获取我赞过的帖子列表 */
export const fetchLikedPosts = (params?: { offset?: number; limit?: number }) =>
  request.get<PostListResponse>("/posts/liked", { params }).then((res) => res.data);

/** 获取帖子详情 */
export const fetchPostDetail = (postId: number) =>
  request.get<PostItem>(`/posts/${postId}`).then((res) => res.data);

/** 创建帖子 */
export const createPost = (payload: PostCreatePayload) =>
  request.post<PostItem>("/posts", payload).then((res) => res.data);

/** 更新帖子 */
export const updatePost = (postId: number, payload: PostUpdatePayload) =>
  request.put<PostItem>(`/posts/${postId}`, payload).then((res) => res.data);

/** 删除帖子 */
export const deletePost = (postId: number) =>
  request.delete(`/posts/${postId}`).then((res) => res.data);

// ========== 评论 API ==========

/** 获取评论列表 */
export const fetchComments = (postId: number, params?: { offset?: number; limit?: number }) =>
  request.get<CommentListResponse>(`/posts/${postId}/comments`, { params }).then((res) => res.data);

/** 创建评论 */
export const createComment = (postId: number, payload: CommentCreatePayload) =>
  request.post<CommentItem>(`/posts/${postId}/comments`, payload).then((res) => res.data);

// ========== 点赞 API ==========

/** 切换点赞 */
export const toggleLike = (postId: number) =>
  request.post<LikeToggleResponse>(`/posts/${postId}/likes/toggle`).then((res) => res.data);

/** 获取点赞状态 */
export const getLikeStatus = (postId: number) =>
  request.get<LikeStatusResponse>(`/posts/${postId}/likes/status`).then((res) => res.data);
