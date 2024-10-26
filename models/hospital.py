from typing import List
import requests
import urllib.request

CLIENT_ID = "AkPRrWfguSW3c8MZrLu1"
CLIENT_SECRET = "G0ObLwFcPM"

def get_hospitals(region : str) -> List[dict]:
    query = "동물병원"
    query = region + " " + query
    url = "https://openapi.naver.com/v1/search/local.json?query=" + query
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    params = {
        "query": query,
        "display": 5
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    hospitals = []
    
    for item in data["items"]:
        hospital = {
            "title": item["title"],
            "link": item["link"],
            "category": item["category"],
            "description": item["description"],
            "telephone": item["telephone"],
            "address": item["address"],
            "mapx": item["mapx"],
            "mapy": item["mapy"]
        }
        hospitals.append(hospital)
    
    return hospitals
