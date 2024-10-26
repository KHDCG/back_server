from pymongo import MongoClient
from gridfs import GridFS
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

mongo_url = os.getenv("MONGO_URL")
# print("mongo_url : ", mongo_url)
client = MongoClient(mongo_url, tls=True)

db = client.account

collection_name_user = db["user"]
collection_name_doctor = db["doctor"]
collection_name_pet = db["pet"]
collection_name_post = db["post"]
collection_name_comment = db["comment"]
collection_name_image = db["image"]
collection_name_user_post_like = db["user_post_like"]
collection_name_user_comment_like = db["user_comment_like"]
collection_name_predict = db["predict"]
fs = GridFS(db)