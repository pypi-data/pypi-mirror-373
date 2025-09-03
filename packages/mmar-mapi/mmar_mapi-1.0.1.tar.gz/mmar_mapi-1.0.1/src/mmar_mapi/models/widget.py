from typing import Self, Literal

from pydantic import BaseModel, model_validator


class Widget(BaseModel):
    type: Literal["widget"] = "widget"
    buttons: list[list[str]] | None = None
    ibuttons: list[list[str]] | None = None

    @model_validator(mode="after")
    def check(self) -> Self:
        if not self.buttons and not self.ibuttons:
            raise ValueError("Empty widget is not allowed!")
        if not self.ibuttons:
            return self
        for row in self.ibuttons:
            for btn in row:
                if ":" in btn:
                    continue
                raise ValueError(f"Expected buttons like `<callback>:<caption>`, found: {btn}")
        return self
