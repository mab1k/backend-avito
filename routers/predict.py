from fastapi import APIRouter, HTTPException, status

from exceptions import PredictionError
from schemas.predict import PredictRequest, PredictResponse
from services.predict import PredictService

router = APIRouter(tags=["predict"])
_service = PredictService()


@router.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Некорректные входные данные"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Ошибка бизнес-логики"},
    },
)
async def predict(payload: PredictRequest) -> PredictResponse:
    try:
        return _service.predict(payload)
    except PredictionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
