import asyncio
import random

import httpx

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from asgi_correlation_id import correlation_id

from ..const import CORRELATION_ID_HEADER_KEY_NAME
from ..exception.internal_exception import GatewayTimeoutException, BadGatewayException


async def invoke_request(timeout: httpx.Timeout, method: str, url: str, app: FastAPI, **kwargs):
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=app.state.config.REQUEST_VERIFY_SSL) as client:
            if "json" in kwargs:
                kwargs["json"] = jsonable_encoder(kwargs["json"])

            app.state.logger.info(f"REQUEST | {kwargs.get('headers').get(CORRELATION_ID_HEADER_KEY_NAME)} | {method} | {url} | kwargs={kwargs}")

            response = await client.request(method, url, **kwargs)

            app.state.logger.info(
                f"RESPONSE | {kwargs.get('headers').get(CORRELATION_ID_HEADER_KEY_NAME)} | {method} | {url} | {response.status_code} | {response.text}"
            )

            return response
    except httpx.TimeoutException as exc:
        message = f"【{app.title}】 \nURL: {method} {url} \nkwargs: {kwargs} \ninvoke_request(), TimeoutException, exc: {exc}"
        app.state.logger.warn(message)
        raise GatewayTimeoutException(str(exc)) from exc
    except Exception as exc:
        message = f"【{app.title}】 \nURL: {method} {url} \nkwargs: {kwargs} \ninvoke_request(), Exception, exc: {exc}"
        app.state.logger.warn(message)
        raise BadGatewayException(str(exc))


async def async_request(app: FastAPI, method, url, current_user: dict = None,
                        request_conn_pool_timeout: float = -1.0, request_conn_timeout: float = -1.0,
                        request_write_timeout: float = -1.0, response_read_timeout: float = -1.0,
                        request_retry_count: int = -1, request_retry_delay_initial_seconds: float = -1.0,
                        **kwargs):
    if request_conn_pool_timeout < 0:
        request_conn_pool_timeout = app.state.config.REQUEST_CONN_POOL_TIMEOUT
    if request_conn_timeout < 0:
        request_conn_timeout = app.state.config.REQUEST_CONN_TIMEOUT
    if request_write_timeout < 0:
        request_write_timeout = app.state.config.REQUEST_WRITE_TIMEOUT
    if response_read_timeout < 0:
        response_read_timeout = app.state.config.RESPONSE_READ_TIMEOUT
    if request_retry_count < 0:
        request_retry_count = app.state.config.REQUEST_RETRY_COUNT
    if request_retry_delay_initial_seconds < 0:
        request_retry_delay_initial_seconds = app.state.config.REQUEST_RETRY_DELAY_INITIAL_SECONDS

    timeout = httpx.Timeout(connect=request_conn_timeout, read=response_read_timeout,
                            write=request_write_timeout, pool=request_conn_pool_timeout)

    if "headers" in kwargs.keys():
        kwargs.get("headers")[CORRELATION_ID_HEADER_KEY_NAME] = correlation_id.get() or ""
    else:
        kwargs["headers"] = {
            CORRELATION_ID_HEADER_KEY_NAME: correlation_id.get() or ""
        }

    if current_user and "access_token" in current_user:
        if "headers" in kwargs.keys():
            kwargs.get("headers")["Authorization"] = f"Bearer {current_user.get('access_token')}"
        else:
            kwargs["headers"] = {
                "Authorization": f"Bearer {current_user.get('access_token')}"
            }

    if request_retry_count <= 0:
        response = await invoke_request(timeout, method, url, app, **kwargs)
        return response
    else:
        retries = 0
        current_delay = request_retry_delay_initial_seconds

        while retries <= request_retry_count:
            if retries > 0:
                app.state.logger.warn(f"【{app.title}】 \nURL: {method} {url} \nkwargs: {kwargs} \n重新嘗試送請求 (第 {retries} 次嘗試)...")

            try:
                # 使用 await 關鍵字等待異步請求完成
                response = await invoke_request(timeout, method, url, app, **kwargs)
                return response
            except GatewayTimeoutException as e:
                if retries < request_retry_count:
                    # 計算下一次的延遲時間：current_delay * 2^retries + 隨機抖動
                    sleep_time = current_delay * (app.state.config.REQUEST_RETRY_DELAY_FACTOR ** retries) + random.uniform(app.state.config.REQUEST_RETRY_DELAY_RANDOM_JITTER_MIN, app.state.config.REQUEST_RETRY_DELAY_RANDOM_JITTER_MAX)
                    app.state.logger.warn(f"【{app.title}】 \nURL: {method} {url} \nkwargs: {kwargs} \n等待 {sleep_time:.2f} 秒後重試...")
                    # 使用 asyncio.sleep 進行異步等待，不會阻塞主執行緒
                    await asyncio.sleep(sleep_time)
                    retries += 1
                else:
                    message = f"【{app.title}】 \nURL: {method} {url} \nkwargs: {kwargs} \n已達到最大重試次數 ({request_retry_count})，放棄發送請求。"
                    app.state.logger.warn(message)
                    raise  # 重新拋出最後一個異常


async def invoke_webhook_message_api(app: FastAPI, message: str):
    payload = {"text": message}
    response = await async_request(app, "POST", app.state.config.WEBHOOK_BASE_URL, request_retry_count=0,
                                   request_retry_delay_initial_seconds=0.0, json=payload)
    response.raise_for_status()
    return response


async def send_webhook_message(app: FastAPI, message: str):
    if not app.state.config.WEBHOOK_BASE_URL:
        app.state.logger.warn(f"Skip notify webhook url is null")
        return None

    retry_count = app.state.config.WEBHOOK_RETRY_COUNT
    if retry_count <= 0:
        try:
            response = await invoke_webhook_message_api(app, message)
            return response
        except Exception as e:
            app.state.logger.warn(f"Notify failure, Exception:{e}")
    else:
        retries = 0
        current_delay = app.state.config.WEBHOOK_RETRY_DELAY_INITIAL_SECONDS

        while retries <= retry_count:
            if retries > 0:
                app.state.logger.warn(f"重新嘗試發送訊息 (第 {retries} 次嘗試)...")

            try:
                # 使用 await 關鍵字等待異步請求完成
                response = await invoke_webhook_message_api(app, message)
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    app.state.logger.warn(f"收到 429 錯誤：{e.response.status_code} - {e.response.text}")
                    if retries < retry_count:
                        # 計算下一次的延遲時間：current_delay * 2^retries + 隨機抖動
                        sleep_time = current_delay * (app.state.config.WEBHOOK_RETRY_DELAY_FACTOR ** retries) + random.uniform(app.state.config.WEBHOOK_RETRY_DELAY_RANDOM_JITTER_MIN, app.state.config.WEBHOOK_RETRY_DELAY_RANDOM_JITTER_MAX)
                        app.state.logger.warn(f"等待 {sleep_time:.2f} 秒後重試...")
                        # 使用 asyncio.sleep 進行異步等待，不會阻塞主執行緒
                        await asyncio.sleep(sleep_time)
                        retries += 1
                    else:
                        app.state.logger.warn(
                            f"已達到最大重試次數 ({app.state.config.WEBHOOK_RETRY_COUNT})，放棄發送訊息。")
                        raise  # 重新拋出最後一個異常
                else:
                    app.state.logger.warn(f"發生其他 HTTP 錯誤：{e.response.status_code} - {e.response.text}")
                    raise  # 對於非 429 錯誤，直接拋出

            except httpx.RequestError as e:
                # 處理網絡錯誤，例如 DNS 查找失敗、連接超時等
                app.state.logger.warn(f"發生網絡錯誤：{e}")
                if retries < retry_count:
                    sleep_time = current_delay * (2 ** retries) + random.uniform(0, 0.5)
                    app.state.logger.warn(f"等待 {sleep_time:.2f} 秒後重試...")
                    await asyncio.sleep(sleep_time)
                    retries += 1
                else:
                    app.state.logger.warn(f"已達到最大重試次數 ({retry_count})，放棄發送訊息。")
                    raise

        return None  # 如果重試次數用盡仍未成功
