from pydantic import BaseModel


class TokenOutput(BaseModel):
    access_token: str
    token_type: str | None = "bearer"
