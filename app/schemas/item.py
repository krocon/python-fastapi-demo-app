from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, examples=["MacBook Pro"])
    description: str = Field(default="", max_length=255, examples=["Arbeitslaptop 16 Zoll"])
    price: float = Field(default=0.0, ge=0.0, examples=[2499.99])


class ItemCreate(ItemBase):
    owner_id: int = Field(..., description="ID des zugeordneten Benutzers", examples=[1])


class ItemRead(ItemBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
