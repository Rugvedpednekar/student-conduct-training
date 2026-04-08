from pydantic import BaseModel, Field


class ContentUpdateForm(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=10000)


class LoginForm(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=7, max_length=255)
