from schemas.predict import PredictRequest


class PredictRepository:
    """Репозиторий с правилами модерации"""

    FORBIDDEN_WORDS = (
        "казино",
        "наркотик",
        "telegram",
        "whatsapp",
        "вайбер",
        "обход модерации",
    )

    # Специальное значение для эмуляции сбоя на уровне хранилища
    FAILING_ITEM_ID = 999_999_999

    def predict(self, payload: PredictRequest) -> bool:
        if payload.item_id == self.FAILING_ITEM_ID:
            raise RuntimeError("Модель модерации временно недоступна")

        text = f"{payload.name} {payload.description}".lower()
        if any(word in text for word in self.FORBIDDEN_WORDS):
            return True

        if payload.images_qty == 0:
            return True

        if not payload.is_verified_seller and len(payload.description.strip()) < 20:
            return True

        return False
