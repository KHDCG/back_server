from pydantic import BaseModel
from typing import List, Optional
from models.predict import Predict

class Image(BaseModel):
    filename : str
    image_encoded : str

class Pet(BaseModel):
    p_name: str
    p_type: str
    p_color: str
    p_age: str
    predict : List[Predict] = []
    profile_image : Optional[str] = None

class User(BaseModel):
    _id: str
    u_email: str
    u_pwd: str
    u_PN: str # Phone Number
    u_birth: str
    u_sex: str
    u_name: str
    u_nickname: str
    pet: List[Pet] = []
    type : str
    # docter
    d_hospital: Optional[str] = None
    profile_image : Optional[str] = None
    
class LoginRequest(BaseModel):
    u_email: str
    u_pwd: str
