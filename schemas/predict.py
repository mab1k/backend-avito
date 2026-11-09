from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    seller_id: int = Field(..., gt=0, description="Идентификатор продавца")
    is_verified_seller: bool = Field(..., description="Прошёл ли продавец верификацию")
    item_id: int = Field(..., gt=0, description="Идентификатор объявления")
    name: str = Field(..., min_length=1, description="Название объявления")
    description: str = Field(..., min_length=1, description="Описание объявления")
    category: int = Field(..., ge=0, description="Идентификатор категории")
    images_qty: int = Field(..., ge=0, description="Количество изображений")


class PredictResponse(BaseModel):
    item_id: int
    has_violation: bool
