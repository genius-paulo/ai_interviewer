from pydantic import BaseModel


class ChatRequest(BaseModel):
    model: str
    messages: list
    temperature: float = 0.7
    max_tokens: int = 100
    top_p: float = 1.0
    frequency_penalty: float = 0.0
