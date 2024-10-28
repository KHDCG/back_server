import asyncio
import requests
from queue import Queue
from typing import Dict, Any
from fastapi import HTTPException

# 요청을 저장할 큐 생성 (선입선출)
inference_queue = Queue()

async def send_inference_request(data: Dict[str, Any]) -> Dict:
    """추론 서버에 POST 요청을 보내는 함수."""
    try:
        url = "http://cataractmodel.hunian.site/inference"
        headers = {"Content-Type": "application/json"}

        # print("[SEND INFERENCE REQUEST]")

        # HTTP POST 요청 보내기 (동기 호출)
        response = requests.post(url, json=data, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to send inference request: {response.text}"
            )

        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

async def inference_worker():
    """큐에서 작업을 꺼내 순차적으로 처리하는 Worker."""

    print("""
[INFERENCE WORKER] Ready to process inference requests.
          """)

    while True:
        # 큐가 비어있을 경우 대기
        if inference_queue.empty():
            await asyncio.sleep(1)
            continue
        else:
            print("[INFO] ready queue size : ", inference_queue.qsize())

        # 큐에서 작업 꺼내기
        infer_data, future = inference_queue.get()

        try:
            # 추론 서버에 요청 보내기
            result = await send_inference_request(infer_data)

            # 작업 완료 후 결과를 future 객체에 저장
            future.set_result(result)
        except Exception as e:
            # 예외 발생 시 future에 예외 저장
            future.set_exception(e)

        inference_queue.task_done()