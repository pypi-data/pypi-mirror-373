from pydantic import BaseModel

class PIIPromptRequest(BaseModel):
    prompt: str

class PIIPromptLiteRequest(BaseModel):
    prompt: str
    top_n: int = None