from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException, status, Depends, Request
from starlette.responses import JSONResponse
from schema.request_schema import ImageRequest
from PIL import Image
from models.user import User, LoginRequest
from models.user import Pet
from models.post import Post, Comment, UserPostLike, UserCommentLike, Predict
from models.hospital import get_hospitals, Location
from models.infer import Infer
from config.database import collection_name_hospital, fs_hospital
from schema.schemas import list_serial
from bson import ObjectId
from typing import List
import base64
import io
from fastapi.encoders import jsonable_encoder
from math import radians, cos, sin, sqrt, atan2
import requests
from worker.inference_worker import inference_queue
import asyncio

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

# 주변 병원 검색
# @router.get("/hospital")
# async def get_hospital(region : str):
#     hospitals = get_hospitals(region) # region에 따라서 병원 정보를 가져옴
#     return hospitals

hospital = []

def load_hospital():
    global hospital
    hospital = list_serial(collection_name_hospital.find())
    print(f"Loaded {len(hospital)} hospitals into memory.")

load_hospital()

@router.post("/hospital")
async def post_hospital(region : Location):

    global hospital

    latitude = region.latitude
    longitude = region.longitude

    # print("latitude : ", latitude)
    # print("longitude : ", longitude)


    near_hospital = []
    k = region.limit

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # 지구 반지름 (단위: km)
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    for hsptl in hospital:
        try:
            lat = float(hsptl["위도"])
            lon = float(hsptl["경도"])
        except ValueError:
            continue

        distance = haversine(latitude, longitude, lat, lon)

        if len(near_hospital) < k:
            near_hospital.append((distance, hsptl))
            near_hospital.sort(key=lambda x: x[0])
        else:
            if near_hospital[-1][0] > distance:
                near_hospital[-1] = (distance, hsptl)
                near_hospital.sort(key=lambda x: x[0])

    if len(near_hospital) > 0:
        dis_near_hospital = []
        for hospital in near_hospital:
            distance, hsptl = hospital
            # make json
            dis_hospital = hsptl
            dis_hospital["distance(km)"] = distance
            dis_near_hospital.append(dis_hospital)
        near_hospital = dis_near_hospital    

    top_k_hospital = {i: near_hospital[i] for i in range(len(near_hospital))}

    return top_k_hospital

@router.post("/inference_queue")
async def inference_queue_handler(infer: Infer):

    inference_data = {
        "img": infer.img
    }

    loop = asyncio.get_event_loop()
    future = loop.create_future()

    # 큐에 작업 추가 (데이터와 Future 객체 전달)
    inference_queue.put((inference_data, future))

    try:
        # 작업 완료 대기 및 결과 반환
        result = await future
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
