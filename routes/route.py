from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException, status, Depends, Request
from starlette.responses import JSONResponse
from schema.request_schema import ImageRequest
from PIL import Image
from models.user import User, LoginRequest
from models.user import Pet
from models.post import Post, Comment, UserPostLike, UserCommentLike, Predict
from models.hospital import get_hospitals
from config.database import collection_name_user, collection_name_post, collection_name_image, collection_name_comment, collection_name_user_post_like, collection_name_user_comment_like, collection_name_predict, fs
from schema.schemas import list_serial
from bson import ObjectId
from typing import List
import base64
import io
from fastapi.encoders import jsonable_encoder

router = APIRouter()

def convert_objectid_to_str(data):
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

## GET ALL

@router.get("/account/all_users")
async def get_users():
    users = list_serial(collection_name_user.find())
    return users

@router.get("/account/all_doctors")
async def get_doctors():
    users = list_serial(collection_name_user.find())
    doctors = []
    for user in users:
        if user["type"] == "doctor":
            doctors.append(user)
    return doctors

## SIGN UP

@router.post("/account/signup/user")
async def post_user(user: User):
    user_data = {
        "u_email": user.u_email,
        "u_pwd": user.u_pwd,
        "u_PN": user.u_PN,
        "u_birth": user.u_birth,
        "u_sex": user.u_sex,
        "u_name": user.u_name,
        "u_nickname": user.u_nickname,
        "pet": [pet.dict() for pet in user.pet] if user.pet else []
    }
    if user.type == "doctor":
        user_data["type"] = "doctor"
        user_data["d_hospital"] = user.d_hospital
    elif user.type == "user":
        user_data["type"] = "user"
        user_data["d_hospital"] = None
        
    json_data = jsonable_encoder(user_data)
    inserted_id = collection_name_user.insert_one(json_data).inserted_id
    user_data["_id"] = str(inserted_id)
    return user_data

## LOGIN

@router.post("/account/login/user")
async def login_user(request: LoginRequest):
    u_email = request.u_email
    u_pwd = request.u_pwd
    user = collection_name_user.find_one({"u_email": u_email, "u_pwd": u_pwd})
    if user:
        return {
            "_id": str(user["_id"]),
            "u_nickname": user["u_nickname"],
        }
    else:
        raise HTTPException(status_code=404, detail="User not found or password incorrect")

@router.delete("/account/delete/user")
async def delete_user(user_id : str):
    collection_name_user.delete_one({"_id" : ObjectId(user_id)})
    return user_id

@router.delete("/account/clear/user")
async def clear_user():
    collection_name_user.delete_many({})
    return "All users are deleted"

# add pet
@router.post("/account/user/pet")
async def post_pet(user_id : str, pet: Pet):
    pet_data = {
        "_id" : ObjectId(),
        "p_name": pet.p_name,
        "p_type": pet.p_type,
        "p_color": pet.p_color,
        "p_age": pet.p_age,
        "predict": [],
        "profile_image": pet.profile_image if pet.profile_image else None
    }
    for predict in pet.predict:
        predict_data = {
            "_id" : ObjectId(),
            "predicted_class": predict.predicted_class,
            "probability": predict.probability,
            "all_probability": predict.all_probability,
            "lime" : [lime.dict() for lime in predict.lime],
            "GradCam" : [GradCam.dict() for GradCam in predict.GradCam],
            "date" : predict.date
        }
        pet_data["predict"].append(predict_data)
    collection_name_user.update_one({"_id": ObjectId(user_id)}, {"$push": {"pet": pet_data}})
    pet_data = convert_objectid_to_str(pet_data)
    return pet_data

# delete pet
@router.delete("/account/user/pet")
async def delete_pet(user_id : str, pet_name: str):
    collection_name_user.update_one({"_id": ObjectId(user_id)}, {"$pull": {"pet": {"p_name": pet_name}}})
    return pet_name

@router.get("/account/user/pet")
async def get_pet(user_id : str, pet_name: str):
    user_data = collection_name_user.find_one({"_id" : ObjectId(user_id)})
    for pet in user_data["pet"]:
        if pet["p_name"] == pet_name:
            pet = convert_objectid_to_str(pet)
            return pet
    return "Pet not found"

@router.get("/account/user/all_pet")
async def get_all_pet(user_id : str):
    user_data = collection_name_user.find_one({"_id" : ObjectId(user_id)})
    user_data["pet"] = convert_objectid_to_str(user_data["pet"])
    return user_data["pet"]

# post predict
@router.post("/account/user/pet/{pet_name}/predict")
async def post_predict(user_id : str, predict: Predict, pet_name: str):
    predict_data = {
        "_id" : ObjectId(),
        "predicted_class": predict.predicted_class,
        "probability": predict.probability,
        "all_probability": predict.all_probability,
        "lime" : [lime.dict() for lime in predict.lime],
        "GradCam" : [GradCam.dict() for GradCam in predict.GradCam],
        "date" : predict.date
    }
    collection_name_user.update_one({"_id": ObjectId(user_id), "pet.p_name": pet_name}, {"$push": {"pet.$.predict": predict_data}})
    return "Predict added"

@router.get("/account/user/pet/{pet_name}/predict")
async def get_predict(user_id : str, pet_name: str):
    user_data = collection_name_user.find_one({"_id" : ObjectId(user_id)})
    for pet in user_data["pet"]:
        if pet["p_name"] == pet_name:
            pet["predict"] = convert_objectid_to_str(pet["predict"])
            return pet["predict"]
    return "Predict not found"

@router.delete("/account/user/pet/{pet_name}/predict")
async def delete_predict(user_id : str, pet_name: str, predict_id: str):
    collection_name_user.update({"_id": ObjectId(user_id), "pet.p_name": pet_name}, {"$pull": {"pet.$.predict": {"_id": ObjectId(predict_id)}}})
    

## post article
@router.get("/posting/feed_all")
async def get_feed_all():
    posts = list_serial(collection_name_post.find())
    posts = convert_objectid_to_str(posts)
    return posts

@router.post("/posting/feed")
async def post_feed(post: Post, user_id : str, predict_id : str, pet_name : str):
    user_record = collection_name_user.find_one({"_id" : ObjectId(user_id)})
    image_ids = []
    for image_data in post.image:
        image_record = {
            "filename": image_data.filename,  # 실제 파일명을 원하면 클라이언트에서 받도록 수정 가능
            "image_encoded": image_data.image_encoded
        }
        collection_name_image.insert_one(image_record)
        image_ids.append(image_record)
    for pet in user_record["pet"]:
        if str(pet["p_name"]) == pet_name:
            pet_data = {
                "p_name": pet["p_name"],
                "p_type": pet["p_type"],
                "p_color": pet["p_color"],
                "p_age": pet["p_age"],
                "profile_image": pet["profile_image"] if pet["profile_image"] else None
            }
            for predict in pet["predict"]:
                if str(predict["_id"]) == predict_id:
                    predict_data = {
                        "_id" : ObjectId(predict_id),
                        "predicted_class": predict["predicted_class"],
                        "probability": predict["probability"],
                        "all_probability": predict["all_probability"],
                        "lime" : predict["lime"],
                        "GradCam" : predict["GradCam"],
                        "date" : predict["date"]
                    }
    post_data = {
        "po_detail": post.po_detail,
        "user_id": user_record["_id"],
        "type" : user_record["type"],
        "image": image_ids,
        "pet" : pet_data,
        "final_predict" : predict_data
    }
    inserted_id = collection_name_post.insert_one(post_data).inserted_id
    return {"_id": str(inserted_id)}

# get article
@router.get("/posting/feed{post_id}")
async def get_feed(post_id: str):
    post = collection_name_post.find_one({"_id": ObjectId(post_id)})
    user = collection_name_user.find_one({"_id" : ObjectId(post["user_id"])})
    post = convert_objectid_to_str(post)
    user_data = {
        "u_nickname": user["u_nickname"],
        "profile_image": user["profile_image"] if "profile_image" in user else None
    }
    if "comment_list" in post:
        for comment in post["comment_list"]:
            user_record = collection_name_user.find_one({"_id" : ObjectId(comment["user_id"])})
            comment["u_nickname"] = user_record["u_nickname"]
            comment["profile_image"] = user_record["profile_image"] if "profile_image" in user_record else None
    return post, user_data

@router.delete("/posting/feed/{post_id}")
async def delete_feed(post_id: str):
    collection_name_post.delete_one({"_id": ObjectId(post_id)})
    return post_id

# comment
@router.post("/posting/feed/{post_id}/comment")
async def post_comment(post_id: str, comment: Comment, user_id : str):
    user_record = collection_name_user.find_one({"_id" : ObjectId(user_id)})
    comment_data = {
        "_id" : ObjectId(),
        "co_detail": comment.co_detail,
        "user_id": user_record["_id"],
        "type" : user_record["type"],
        "like_list" : [] 
    }
    collection_name_post.update_one({"_id" : ObjectId(post_id)}, {"$push": {"comment_list": comment_data}})
    return {"message" : "Commented"}

@router.get("/posting/feed/{post_id}/comment")
async def get_comment(post_id: str):
    post_record = collection_name_post.find_one({"_id" : ObjectId(post_id)})
    if not "comment_list" in post_record:
        collection_name_post.update_one({"_id": ObjectId(post_id)}, {"$set": {"comment_list": []}})
        post_record["comment_list"] = []
    comments = post_record["comment_list"]
    for comment in comments:
        user_record = collection_name_user.find_one({"_id" : ObjectId(comment["user_id"])})
        comment["u_nickname"] = user_record["u_nickname"]
        comment["profile_image"] = user_record["profile_image"] if "profile_image" in user_record else None
    comments = convert_objectid_to_str(comments)
    return comments

@router.delete("/posting/feed/{post_id}/comment/{comment_id}")
async def delete_comment(post_id : str, comment_id : str):
    post_record = collection_name_post.find_one({"_id" : ObjectId(post_id)})
    for comment in post_record["comment_list"]:
        if comment["_id"] == ObjectId(comment_id):
            post_record["comment_list"].remove(comment)
            collection_name_post.update_one({"_id" : ObjectId(post_id)}, {"$pull" : {"comment_list": comment}})
            return "comment deleted"
    return "comment not found"

## like
@router.post("/posting/feed/{post_id}/like")
async def post_like(post_id: str, user_id : str):
    user_post_like_data = {
        "user_id": ObjectId(user_id),
        "po_id": ObjectId(post_id)
    }
    post = collection_name_post.find_one({"_id": ObjectId(post_id)})
    if not "like_list" in post:
        collection_name_post.update_one({"_id": ObjectId(post_id)}, {"$set": {"like_list": []}})
        post["like_list"] = []
    for like in post["like_list"]:
        if like["user_id"] == user_post_like_data["user_id"]:
            return {"message": "Already liked"}
    collection_name_post.update_one({"_id": ObjectId(post_id)}, {"$push": {"like_list": user_post_like_data}})
    return {"message": "Liked"}

@router.post("/posting/feed/{post_id}/comment/{comment_id}/like")
async def post_comment_like(post_id : str, comment_id: str, user_id : str):
    user_comment_like_data = {
        "user_id": ObjectId(user_id),
        "co_id": ObjectId(comment_id)
    }
    post_record = collection_name_post.find_one({"_id" : ObjectId(post_id)})
    for comment in post_record["comment_list"]:
        if comment["_id"] == ObjectId(comment_id):
            if not "like_list" in comment:
                collection_name_post.update_one({"_id" : ObjectId(post_id), "comment_list._id": ObjectId(comment_id)}, {"$set": {"comment_list.$.like_list": []}})
                comment["like_list"] = []
            for like in comment["like_list"]:
                if like["user_id"] == user_comment_like_data["user_id"]:
                    return {"message": "Already liked"}
            collection_name_post.update_one({"_id" : ObjectId(post_id), "comment_list._id": ObjectId(comment_id)}, {"$push": {"comment_list.$.like_list": user_comment_like_data}})
            return {"message": "Liked"}
    return {"message": "Comment not found"}

@router.get("/posting/feed/{post_id}/like")
async def get_like(post_id: str):
    post = collection_name_post.find_one({"_id": ObjectId(post_id)})
    if not "like_list" in post:
        collection_name_post.update_one({"_id": ObjectId(post_id)}, {"$set": {"like_list": []}})
        post["like_list"] = []
    like_list = post["like_list"]
    for like in like_list:
        user = collection_name_user.find_one({"_id" : ObjectId(like["user_id"])})
        like["u_nickname"] = user["u_nickname"]
        like["profile_image"] = user["profile_image"] if "profile_image" in user else None
    like_list = convert_objectid_to_str(like_list)
    return like_list

@router.get("/posting/feed/{post_id}/comment/{comment_id}/like")
async def get_comment_like(post_id : str, comment_id: str):
    post_record = collection_name_post.find_one({"_id" : ObjectId(post_id)})
    for comment in post_record["comment_list"]:
        if comment["_id"] == ObjectId(comment_id):
            like_list = comment["like_list"]
            for like in like_list:
                user = collection_name_user.find_one({"_id" : ObjectId(like["user_id"])})
                like["u_nickname"] = user["u_nickname"]
                like["profile_image"] = user["profile_image"] if "profile_image" in user else None
            return like_list

@router.delete("/posting/feed/{post_id}/like")
async def post_delete_like(post_id : str, user_id : str):
    post_record = collection_name_post.find_one({"_id" : ObjectId(post_id)})
    for post_like in post_record["like_list"]:
        if post_like["user_id"] == ObjectId(user_id):
            collection_name_post.update_one({"_id" : ObjectId(post_id)}, {"$pull" : {"like_list": post_like}})
            return "Like deleted"
    return "Like not found"

@router.delete("/posting/feed/{post_id}/comment/{comment_id}/like")
async def post_delete_comment_like(post_id : str, comment_id : str, user_id : str):
    post_record = collection_name_post.find_one({"_id" : ObjectId(post_id)})
    for comment in post_record["comment_list"]:
        if comment["_id"] == ObjectId(comment_id):
            for like in comment["like_list"]:
                if like["user_id"] == ObjectId(user_id):
                    collection_name_post.update_one({"_id" : ObjectId(post_id), "comment_list._id": ObjectId(comment_id)}, {"$pull" : {"comment_list.$.like_list": like}})
                    return "Comment like deleted"
            return "User not found"
    return "Comment not found"

# 주변 병원 검색
@router.get("/hospital")
async def get_hospital(region : str):
    hospitals = get_hospitals(region) # region에 따라서 병원 정보를 가져옴
    return hospitals