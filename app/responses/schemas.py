from pydantic import BaseModel, Field



class ResponseCreate(BaseModel):
    answers: dict = Field(default_factory=dict)
    # raw_transcript: str | None = None


class ResponseRead(BaseModel):
    id: str
    form_id: str
    # answers: list[AnswerOut]

    model_config = {"from_attributes": True}
    
    
class TotalResponses(BaseModel):
    form_id: str
    count: int

    model_config = {"from_attributes": True}
    

class AnswerIn(BaseModel):
    field_id: str
    value: str


class AnswerOut(BaseModel):
    field_id: str
    value: str

    model_config = {"from_attributes": True}



