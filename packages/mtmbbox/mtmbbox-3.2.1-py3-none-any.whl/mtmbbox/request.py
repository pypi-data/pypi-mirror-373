import asyncio
import random
import time
import uuid
from json import JSONDecodeError

import httpx
import requests
from mtmqujing import AsyncQujingByHttp, QujingByHttp
from mtmqujing.convert import FormatConvert

from .constants import DEVICES_COMPANY, HEADERS_BASE, TIMEOUT_DEFAULT
from .exceptions import APPServerHighLoadError, APPTooManyRequestsError


class BBoxQujingFunctionParams:
    @staticmethod
    def ea3(strs: str, typeint: int) -> dict:
        # strs要求是json格式的string类型
        return {
            "class": "c.abc",
            "method": "9",
            "thisobj": "null",
            "param0": f"raw#{strs}",
            "parser0": "byte",
            "param1": f"{typeint}",
            "parser1": "int",
        }

    @staticmethod
    def da3(strs: str, typeint: int) -> dict:
        # strs要求是base64格式的string类型
        return {
            "class": "c.abc",
            "method": "7",
            "thisobj": "null",
            "param0": f"{strs}",
            "parser0": "byte",
            "param1": f"{typeint}",
            "parser1": "int",
        }


class BBoxCryptoTemplate:
    def encrypt(self, strs: str, typeint: int) -> dict:
        pass

    def decrypt(self, strs: str, typeint: int) -> dict:
        pass


class AsyncBBoxCryptoTemplate:
    async def encrypt(self, strs: str, typeint: int) -> dict:
        pass

    async def decrypt(self, strs: str, typeint: int) -> dict:
        pass


class BBoxCryptoFromQujing(QujingByHttp, BBoxCryptoTemplate):
    def __init__(self, host, port_config=61000, port_invoke=None):
        super().__init__(host, port_config=port_config)
        self.port_invoke = port_invoke

    def encrypt(self, strs: str, typeint: int):
        params = BBoxQujingFunctionParams.ea3(strs, typeint)
        resp = self.invoke(self.port_invoke, params)
        return resp

    def decrypt(self, strs: str, typeint: int):
        params = BBoxQujingFunctionParams.da3(strs, typeint)
        resp = self.invoke(self.port_invoke, params)
        if "data" in resp and resp["data"].startswith("H4"):
            resp["data"] = FormatConvert.ungzip_base64_to_str(resp["data"])
        return resp


class AsyncBBoxCryptoFromQujing(AsyncQujingByHttp, AsyncBBoxCryptoTemplate):
    def __init__(self, host, port_config=61000, port_invoke=None):
        super().__init__(host, port_config=port_config)
        self.port_invoke = port_invoke

    async def encrypt(self, strs: str, typeint: int):
        params = BBoxQujingFunctionParams.ea3(strs, typeint)
        resp = await self.invoke(self.port_invoke, params)
        return resp

    async def decrypt(self, strs: str, typeint: int):
        params = BBoxQujingFunctionParams.da3(strs, typeint)
        resp = await self.invoke(self.port_invoke, params)
        if "data" in resp and resp["data"].startswith("H4"):
            resp["data"] = FormatConvert.ungzip_base64_to_str(resp["data"])
        return resp


class BBoxCryptoFromQujingWithStandby(BBoxCryptoTemplate):
    def __init__(self, host_ports: list[dict]):
        self.cryptos = []
        for host_port in host_ports:
            host = host_port["host"]
            port_config = host_port["port_config"]
            port_invoke = host_port["port_invoke"]
            self.cryptos.append(BBoxCryptoFromQujing(host, port_invoke=port_invoke, port_config=port_config))

    def encrypt(self, strs: str, typeint: int):
        for crypto in self.cryptos:
            try:
                resp = crypto.encrypt(strs, typeint)
                return resp
            except Exception as e:
                _exception = e
                pass
        raise _exception

    def decrypt(self, strs: str, typeint: int):
        for crypto in self.cryptos:
            try:
                resp = crypto.decrypt(strs, typeint)
                return resp
            except Exception as e:
                _exception = e
                pass
        raise _exception


class AsyncBBoxCryptoFromQujingWithStandby(AsyncBBoxCryptoTemplate):
    def __init__(self, host_ports: list[dict]):
        self.cryptos = []
        for host_port in host_ports:
            host = host_port["host"]
            port_config = host_port["port_config"]
            port_invoke = host_port["port_invoke"]
            self.cryptos.append(AsyncBBoxCryptoFromQujing(host, port_invoke=port_invoke, port_config=port_config))

    async def encrypt(self, strs: str, typeint: int):
        _exception = None
        for crypto in self.cryptos:
            try:
                resp = await crypto.encrypt(strs, typeint)
                return resp
            except Exception as e:
                _exception = e
                pass
        raise _exception

    async def decrypt(self, strs: str, typeint: int):
        _exception = None
        for crypto in self.cryptos:
            try:
                resp = await crypto.decrypt(strs, typeint)
                return resp
            except Exception as e:
                _exception = e
                pass
        raise _exception


class BBoxRequest:
    IP_CHECK_URLS = (
        "https://checkip.amazonaws.com",
        "https://api.ipify.org",
        "https://ifconfig.me",
    )

    @staticmethod
    def check_ip(proxies=None):
        # 从IP检查网站获取ip
        error = Exception("Function check_ip error!")
        for url in BBoxRequest.IP_CHECK_URLS:
            try:
                ip = requests.get(url, proxies=proxies).text.strip()
                return ip
            except Exception as e:
                error = e
                time.sleep(1)
        # 获取失败, 则抛出异常
        raise error

    @staticmethod
    def renew_device():
        return uuid.uuid4().hex[:16]

    @staticmethod
    def update_headers(headers: dict = None, **kwargs):
        headers = HEADERS_BASE.copy() if headers is None else headers
        if "token" not in headers and "token" in kwargs:
            headers["Authorization"] = f'Bearer {kwargs["token"]}'
        if "device" not in headers:
            if "device" in kwargs:
                headers["Device"] = str(kwargs["device"])
            else:
                headers["Device"] = str(BBoxRequest.renew_device())
        if "company" not in headers:
            if "company" in kwargs:
                headers["Com"] = str(kwargs["company"])
            else:
                headers["Com"] = str(random.choice(DEVICES_COMPANY))
        headers["User-Agent"] = (
            f"Dalvik/2.1.0 (Linux; U; Android {headers['Os']}; {headers['Com']} Build/{headers['Com']})"
        )
        return headers

    @staticmethod
    def encrypt_before_request(data: dict, crypto: BBoxCryptoTemplate, typeint: int, **kwargs):
        # 将data转为str
        str_json_request = FormatConvert.json2str(data)
        # 优先从数据库中查找, 如果没有则使用crypto.encrypt对象去请求, 并将结果存入数据库
        if "encryptdict" in kwargs:
            if str_json_request in kwargs["encryptdict"]:
                bytes_request = kwargs["encryptdict"][str_json_request]
            else:
                strs = crypto.encrypt(str_json_request, typeint=typeint)["data"]
                bytes_request = FormatConvert.base642bytes(strs)
                kwargs["encryptdict"][str_json_request] = bytes_request
        elif "encryptredisdb" in kwargs:
            key = f"{typeint}#{str_json_request}"
            strs = kwargs["encryptredisdb"].get(key)
            if strs is None:
                strs = crypto.encrypt(str_json_request, typeint=typeint)["data"]
                kwargs["encryptredisdb"].set(key, strs)
            bytes_request = FormatConvert.base642bytes(strs)
        else:
            strs = crypto.encrypt(str_json_request, typeint=typeint)["data"]
            bytes_request = FormatConvert.base642bytes(strs)
        return bytes_request

    @staticmethod
    def decrypt_after_response(data: bytes, crypto: BBoxCryptoTemplate, typeint: int, **kwargs):
        # 优先从数据库中查找, 如果没有则使用crypto.encrypt对象去请求
        if "decryptdict" in kwargs:
            if data in kwargs["decryptdict"]:
                str_json_response = kwargs["decryptdict"][data]
            else:
                # 将返回的bytes转为str
                str_base64_response = FormatConvert.bytes2base64(data)
                str_json_response = crypto.decrypt(str_base64_response, typeint=typeint)["data"]
                kwargs["decryptdict"][data] = str_json_response
        elif "decryptredisdb" in kwargs:
            str_base64_response = FormatConvert.bytes2base64(data)
            key = f"{typeint}#{str_base64_response}"
            str_json_response = kwargs["decryptredisdb"].get(key)
            if str_json_response is None:
                str_json_response = crypto.decrypt(str_base64_response, typeint=typeint)["data"]
                kwargs["decryptredisdb"].set(key, str_json_response)
        else:
            str_base64_response = FormatConvert.bytes2base64(data)
            str_json_response = crypto.decrypt(str_base64_response, typeint=typeint)["data"]

        # 将str转为dict
        if kwargs.get("todict", True):
            try:
                dict_response = FormatConvert.str2json(str_json_response)
                return dict_response
            except Exception as e:
                raise JSONDecodeError({"error": e, "str": str_json_response})
        else:
            return str_json_response

    @staticmethod
    def request(crypto, typeint, method: str, url: str, **kwargs):
        # 更新请求头
        headers = BBoxRequest.update_headers(**kwargs)
        # 生成请求参数
        request_kwargs = {
            "params": kwargs.pop("params", None),
            "headers": headers,
            "proxies": kwargs.pop("proxies", None),
            "timeout": kwargs.pop("timeout", TIMEOUT_DEFAULT),
            "verify": kwargs.pop("verify", None),
        }
        if method == "POST":
            data = kwargs.pop("data")
            bytes_request = BBoxRequest.encrypt_before_request(data, crypto, typeint, **kwargs)
            request_kwargs["data"] = bytes_request
        elif method == "GET":
            data = request_kwargs["params"]
            pass
        else:
            raise Exception("method must be POST or GET")
        # 发送请求
        client_request_ts_start = time.time()
        resp = requests.request(method, url, **request_kwargs)
        client_request_ts_end = time.time()
        # 处理返回状态码
        if resp.status_code == 200:
            if kwargs.get("isdecrypt", True):
                # 处理返回
                if "data" in kwargs:
                    kwargs.pop("data")
                dict_response = BBoxRequest.decrypt_after_response(resp.content, crypto, typeint, **kwargs)
                # 添加请求时间和返回时间
                if isinstance(dict_response, dict) and "code" in dict_response:
                    dict_response["cts"] = [int(client_request_ts_start * 1000), int(client_request_ts_end * 1000)]
                return dict_response
            else:
                return resp.content
        else:
            if str(resp.status_code).startswith("5"):
                raise APPServerHighLoadError(resp.status_code, url, data)
            else:
                raise APPTooManyRequestsError(resp.status_code, url, data)


class AsyncBBoxRequest:
    @staticmethod
    async def check_ip(proxies=None):
        # 从IP检查网站获取ip
        error = Exception("Function check_ip error!")
        async with httpx.AsyncClient() as client:
            for url in BBoxRequest.IP_CHECK_URLS:
                try:
                    resp = await client.get(url, proxies=proxies)
                    ip = resp.text.strip()
                    return ip
                except Exception as e:
                    error = e
                    await asyncio.sleep(1)
        # 获取失败, 则抛出异常
        raise error

    @staticmethod
    async def encrypt_before_request(data: dict, crypto: AsyncBBoxCryptoTemplate, typeint: int, **kwargs):
        # 将data转为str
        str_json_request = FormatConvert.json2str(data)
        # 优先从数据库中查找, 如果没有则使用crypto.encrypt对象去请求, 并将结果存入数据库
        if "encryptdict" in kwargs:
            if str_json_request in kwargs["encryptdict"]:
                bytes_request = kwargs["encryptdict"][str_json_request]
            else:
                strs = (await crypto.encrypt(str_json_request, typeint=typeint))["data"]
                bytes_request = FormatConvert.base642bytes(strs)
                kwargs["encryptdict"][str_json_request] = bytes_request
        elif "encryptredisdb" in kwargs:
            key = f"{typeint}#{str_json_request}"
            strs = kwargs["encryptredisdb"].get(key)
            if strs is None:
                strs = (await crypto.encrypt(str_json_request, typeint=typeint))["data"]
                kwargs["encryptredisdb"].set(key, strs)
            bytes_request = FormatConvert.base642bytes(strs)
        else:
            strs = (await crypto.encrypt(str_json_request, typeint=typeint))["data"]
            bytes_request = FormatConvert.base642bytes(strs)
        return bytes_request

    @staticmethod
    async def decrypt_after_response(data: bytes, crypto: AsyncBBoxCryptoTemplate, typeint: int, **kwargs):
        # 优先从数据库中查找, 如果没有则使用crypto.encrypt对象去请求
        if "decryptdict" in kwargs:
            if data in kwargs["decryptdict"]:
                str_json_response = kwargs["decryptdict"][data]
            else:
                # 将返回的bytes转为str
                str_base64_response = FormatConvert.bytes2base64(data)
                str_json_response = (await crypto.decrypt(str_base64_response, typeint=typeint))["data"]
                kwargs["decryptdict"][data] = str_json_response
        elif "decryptredisdb" in kwargs:
            str_base64_response = FormatConvert.bytes2base64(data)
            key = f"{typeint}#{str_base64_response}"
            str_json_response = kwargs["decryptredisdb"].get(key)
            if str_json_response is None:
                str_json_response = (await crypto.decrypt(str_base64_response, typeint=typeint))["data"]
                kwargs["decryptredisdb"].set(key, str_json_response)
        else:
            str_base64_response = FormatConvert.bytes2base64(data)
            str_json_response = (await crypto.decrypt(str_base64_response, typeint=typeint))["data"]

        # 将str转为dict
        if kwargs.get("todict", True):
            try:
                dict_response = FormatConvert.str2json(str_json_response)
                return dict_response
            except Exception as e:
                raise JSONDecodeError({"error": e, "str": str_json_response})
        else:
            return str_json_response

    @staticmethod
    async def request(crypto, typeint, method: str, url: str, **kwargs):
        # 更新请求头
        headers = BBoxRequest.update_headers(**kwargs)
        # 生成请求参数
        request_kwargs = {
            "params": kwargs.pop("params", None),
            "headers": headers,
            "timeout": kwargs.pop("timeout", TIMEOUT_DEFAULT),
            "verify": kwargs.pop("verify", None),
        }
        if method == "POST":
            data = kwargs.pop("data")
            bytes_request = await AsyncBBoxRequest.encrypt_before_request(data, crypto, typeint, **kwargs)
            request_kwargs["content"] = bytes_request
        elif method == "GET":
            data = request_kwargs["params"]
            pass
        else:
            raise Exception("method must be POST or GET")
        # 发送请求
        client_request_ts_start = time.time()
        proxy = kwargs.pop("proxies", None)
        verify = request_kwargs.pop("verify", None)
        async with httpx.AsyncClient(proxy=proxy, verify=verify) as client:
            resp = await client.request(method, url, **request_kwargs)
        client_request_ts_end = time.time()
        # 处理返回状态码
        if resp.status_code == 200:
            if kwargs.get("isdecrypt", True):
                # 处理返回
                if "data" in kwargs:
                    kwargs.pop("data")
                dict_response = await AsyncBBoxRequest.decrypt_after_response(resp.content, crypto, typeint, **kwargs)
                # 添加请求时间和返回时间
                if isinstance(dict_response, dict) and "code" in dict_response:
                    dict_response["cts"] = [int(client_request_ts_start * 1000), int(client_request_ts_end * 1000)]
                return dict_response
            else:
                return resp.content
        else:
            if str(resp.status_code).startswith("5"):
                raise APPServerHighLoadError(resp.status_code, url, data)
            else:
                raise APPTooManyRequestsError(resp.status_code, url, data)
