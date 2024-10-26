from models.user import User
from models.doctor import Doctor
from models.post import Post
from typing import Union, List
from pymongo import MongoClient
import gridfs
import base64
from bson import ObjectId
from config.database import fs

def individual_serial(data: dict) -> dict:
    if "u_email" in data:
        pets_data = []
        for pet in data.get("pet", []):
             if pet and all(key in pet for key in ["p_name", "p_type", "p_color", "p_age"]):
                pet_dict = {
                    "p_name": pet["p_name"],
                    "p_type": pet["p_type"],
                    "p_color": pet["p_color"],
                    "p_age": pet["p_age"]
                }
                pets_data.append(pet_dict)
        result = {
            "_id": str(data["_id"]),
            "u_email": data["u_email"],
            "u_pwd": data["u_pwd"],
            "u_PN": data["u_PN"],
            "u_birth": data["u_birth"],
            "u_sex": data["u_sex"],
            "u_name": data["u_name"],
            "u_nickname": data["u_nickname"],
            "pet": pets_data,
            "type" : data["type"]
        }
        # d_hospital 필드가 있는 경우에만 추가
        if "d_hospital" in data:
            result["d_hospital"] = data["d_hospital"]
        else:
            result["d_hospital"] = None
        
        return result
    # post 가져오기
    elif "po_detail" in data:
        images_data = []
        for image in data.get("image", []):
            image_encoded = image["image_encoded"]
            image_dict = {
                "filename": image["filename"],
                "image_encoded" : image_encoded
            }
            images_data.append(image_dict)
        like_list = []
        for like in data.get("like_list", []):
            like_dict = {
                "user_id": str(like["user_id"]),
                "po_id": str(like["po_id"])
            }
            like_list.append(like_dict)
        comment_list = []
        for comment in data.get("comment_list", []):
            comment_like_list = []
            for like in comment.get("like_list", []):
                like_dict = {
                    "user_id": str(like["user_id"]),
                    "co_id": like["co_id"]
                }
                comment_like_list.append(like_dict)
            comment_dict = {
                "user_id" : str(comment["user_id"]),
                "co_detail": comment["co_detail"],
                "like_list": comment_like_list
            }
            comment_list.append(comment_dict)
        return{
            "po_id": str(data["_id"]),
            "po_detail": data["po_detail"],
            "user_id": str(data["user_id"]),
            "type" : data["type"],
            "image": images_data,
            "like_list": like_list,
            "comment_list": comment_list,
            "pet": data["pet"]
        }
    else:
        raise ValueError("Unsupported type for serialization")

def list_serial(users: List[Union[User]]) -> List[dict]:
    return [individual_serial(user) for user in users]