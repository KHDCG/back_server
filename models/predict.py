from pydantic import BaseModel
from typing import List

class Image(BaseModel):
    filename : str
    image_encoded : str

class Predict(BaseModel):
    predicted_class : str
    probability : float
    all_probability : List[List[float]] = []
    lime : List[Image] = []
    GradCam : List[Image] = []
    date : str