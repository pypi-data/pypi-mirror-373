from pydantic import BaseModel

class GreetingResponse(BaseModel):
    greeting: str
    name: str
