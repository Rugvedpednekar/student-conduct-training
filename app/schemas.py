from pydantic import BaseModel, Field


class ContentUpdateForm(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=10000)


class LoginForm(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=7, max_length=255)


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
