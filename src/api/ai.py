from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from dtos.ai import AIRecommendDTO
from schema.ai import AIRecommendRequest, AIRecommendResponse
from services.ai_recommend_service import AIRecommendService


router = APIRouter(tags=["ai"])


@router.post("/ai/recommend", response_model=AIRecommendResponse)
def ai_recommend(
    payload: AIRecommendRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AIRecommendService(db)
    try:
        items = service.recommend(current_user.id, AIRecommendDTO(**payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"items": items}
