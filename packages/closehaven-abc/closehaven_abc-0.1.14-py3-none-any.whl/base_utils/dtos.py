from pydantic import BaseModel


class ResponseFailureModel(BaseModel):
    success: bool = False
    message: str
