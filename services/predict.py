from exceptions import PredictionError
from repositories.predict import PredictRepository
from schemas.predict import PredictRequest, PredictResponse


class PredictService:
    def __init__(self, repository: PredictRepository | None = None) -> None:
        self._repository = repository or PredictRepository()

    def predict(self, payload: PredictRequest) -> PredictResponse:
        try:
            has_violation = self._repository.predict(payload)
        except Exception as exc:
            raise PredictionError(str(exc)) from exc

        return PredictResponse(item_id=payload.item_id, has_violation=has_violation)
