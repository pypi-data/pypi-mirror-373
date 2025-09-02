from pydantic import BaseModel

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
    email:str | None = None