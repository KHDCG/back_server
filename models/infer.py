from pydantic import BaseModel
from typing import List

class Infer(BaseModel):
    img: str
    user_id: str
    pet_name: str

class InferTest(BaseModel):
    img: str