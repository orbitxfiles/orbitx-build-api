from pydantic import BaseModel, ConfigDict


class OrbitXSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class PaginatedMeta(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
