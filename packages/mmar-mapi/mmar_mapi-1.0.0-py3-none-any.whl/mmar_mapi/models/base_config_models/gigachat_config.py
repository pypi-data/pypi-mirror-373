from typing import Self

from pydantic import BaseModel, model_validator, SecretStr


class GigaChatConfig(BaseModel):
    client_id: SecretStr = SecretStr("")
    client_secret: SecretStr = SecretStr("")

    @model_validator(mode="after")
    def empty_validator(self) -> Self:
        if not (self.client_id and self.client_secret):
            raise ValueError("creds for gigachat is not filled")
        return self
