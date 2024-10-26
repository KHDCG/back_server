from pydantic import BaseModel
from typing import List
from models.user import Pet
from models.predict import Predict
    
class Image(BaseModel):
    filename : str
    image_encoded : str
    
    
class UserPostLike(BaseModel):
    user_id : str
    po_id : str
    
    
class UserCommentLike(BaseModel):
    user_id : str
    co_id : str


class Comment(BaseModel):
    co_detail : str
    like_list : List[UserCommentLike] = []
    
class Post(BaseModel):
    po_detail : str
    image : List[Image] = []
    like_list : List[UserPostLike] = []
    comment_list : List[Comment] = []