from pydantic import BaseModel

class Doctor(BaseModel):
    _id: str
    d_email: str
    d_pwd: str
    d_PN: str
    d_name: str
    d_nickname: str
    d_hospital: str
