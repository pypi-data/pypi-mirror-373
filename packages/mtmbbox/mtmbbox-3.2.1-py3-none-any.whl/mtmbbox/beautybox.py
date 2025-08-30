from .constants import HOST_CHAT_PIC, HOST_DATA, PaymentType
from .request import (
    AsyncBBoxCryptoTemplate,
    AsyncBBoxRequest,
    BBoxCryptoTemplate,
    BBoxRequest,
)

__func_info__ = {
    "user_login": {
        "path": "/auth/json", "method": "POST", "type": 1,
        "args": ["username", "password", "certcode", "captcha", "points", "rtype"],
        "arg_types": {"username": "str", "password": "str", "certcode": "str", "captcha": "str", "points": "str", "rtype": "str"},
        "defaults": {"captcha": "9d184bc8a496a52cfdc2594f85f2639a", "points": "26,37", "rtype": "a"},
        "data_map": {"x5": "username", "x7": "password", "x1": "certcode", "xi": "captcha", "xj": "points", "x0": "rtype"}
    },
    "user_bind": {"path": "/user/cert/bound/json", "method": "POST", "type": 1, "token": True, "args": ["paypwd"], "arg_types": {"paypwd": "str"}, "data_map": {"p": "paypwd"}},
    "user_unbind": {"path": "/user/cert/unbound/json", "method": "POST", "type": 1, "token": True, "args": ["paypwd"], "arg_types": {"paypwd": "str"}, "data_map": {"p": "paypwd"}},
    "user_assets": {"path": "/user/expire/info/json", "method": "GET", "type": 1, "token": True},
    "txn_market_orders_list": {"path": "/transaction/json", "method": "GET", "type": 1, "token": True, "args": ["rtype"], "arg_types": {"rtype": "int"}, "params_map": {"t": "rtype"}},
    "txn_seller_orders_list": {"path": "/transaction/seller/json", "method": "GET", "type": 1, "token": True},
    "txn_seller_orders_place": {"path": "/transaction/seller/new/json", "method": "POST", "type": 1, "token": True, "args": ["order_type", "paypwd"], "arg_types": {"order_type": "int", "paypwd": "str"}, "data_map": {"t": "order_type", "p": "paypwd"}},
    "txn_seller_orders_confirm": {"path": "/transaction/seller/confirm/json", "method": "POST", "type": 1, "token": True, "args": ["order_id", "paypwd"], "arg_types": {"order_id": "int", "paypwd": "str"}, "data_map": {"p": "paypwd"}, "params_map": {"id": "order_id"}},
    "txn_seller_orders_dispute": {"path": "/transaction/dispute/json", "method": "POST", "type": 1, "token": True, "args": ["order_id", "paypwd"], "arg_types": {"order_id": "int", "paypwd": "str"}, "data_map": {"p": "paypwd"}, "params_map": {"id": "order_id"}},
    "txn_buyer_orders_list": {"path": "/transaction/buyer/json", "method": "GET", "type": 1, "token": True},
    "txn_buyer_orders_place": {"path": "/transaction/buyer/place/json", "method": "GET", "type": 1, "token": True, "args": ["order_id"], "arg_types": {"order_id": "int"}, "params_map": {"id": "order_id"}},
    "txn_buyer_orders_payment": {"path": "/transaction/buyer/payment/json", "method": "GET", "type": 1, "token": True, "args": ["order_id"], "arg_types": {"order_id": "int"}, "params_map": {"id": "order_id"}},
    "txn_buyer_orders_nopayment": {"path": "/transaction/buyer/nopayment/json", "method": "GET", "type": 1, "token": True, "args": ["order_id"], "arg_types": {"order_id": "int"}, "params_map": {"id": "order_id"}},
    "txn_buyer_orders_cancel": {"path": "/transaction/buyer/cancel/json", "method": "GET", "type": 1, "token": True, "args": ["order_id", "t"], "arg_types": {"order_id": "int", "t": "str"}, "params_map": {"id": "order_id", "t": "t"}},
    "reg_market_orders_list": {"path": "/registration/json", "method": "GET", "type": 1, "token": True},
    "reg_buyer_orders_list": {"path": "/registration/buyer/json", "method": "POST", "type": 1, "token": True, "device_info": True, "data_map": {"x0": "a"}},
    "reg_buyer_orders_place": {"path": "/registration/buyer/json", "method": "POST", "type": 1, "token": True, "device_info": True, "args": ["order_id"], "arg_types": {"order_id": "int"}, "data_map": {"x6": "order_id", "x0": "b"}},
    "reg_buyer_orders_confirm": {"path": "/registration/buyer/json", "method": "POST", "type": 1, "token": True, "device_info": True, "args": ["order_id"], "arg_types": {"order_id": "int"}, "data_map": {"x6": "order_id", "x0": "d"}},
    "reg_buyer_orders_cancel": {"path": "/registration/buyer/json", "method": "POST", "type": 1, "token": True, "device_info": True, "args": ["order_id"], "arg_types": {"order_id": "int"}, "data_map": {"x6": "order_id", "x0": "f"}},
    "reg_seller_orders_list": {"path": "/registration/seller/json", "method": "POST", "type": 1, "token": True, "device_info": True, "data_map": {"x0": "a"}},
    "reg_seller_orders_place": {"path": "/registration/seller/json", "method": "POST", "type": 1, "token": True, "device_info": True, "args": ["paypwd"], "arg_types": {"paypwd": "str"}, "data_map": {"xa": 0, "x0": "b", "x9": "paypwd"}},
    "reg_seller_orders_confirm": {"path": "/registration/seller/json", "method": "POST", "type": 1, "token": True, "device_info": True, "args": ["order_id"], "arg_types": {"order_id": "int"}, "data_map": {"x6": "order_id", "x0": "d"}},
    "reg_seller_orders_dispute": {"path": "/registration/seller/json", "method": "POST", "type": 1, "token": True, "device_info": True, "args": ["order_id", "paypwd"], "arg_types": {"order_id": "int", "paypwd": "str"}, "data_map": {"x6": "order_id", "x0": "e", "x9": "paypwd"}},
    "notify_isread": {"path": "/notify/isread/json", "method": "GET", "type": 1, "token": True},
    "notify_remind": {"path": "/notify/remind/json", "method": "GET", "type": 1, "token": True, "args": ["page"], "arg_types": {"page": "int"}, "params_map": {"page": "page"}, "defaults": {"page": 1}},
    "notify_announce": {"path": "/notify/announce/json", "method": "GET", "type": 1, "token": True, "args": ["page"], "arg_types": {"page": "int"}, "params_map": {"page": "page"}, "defaults": {"page": 1}},
    "chat": {"path": "/chat/json", "method": "GET", "type": 1, "token": True},
    "chat_list": {"path": "/chat/show/json", "method": "GET", "type": 1, "token": True, "args": ["chat_id", "page"], "arg_types": {"chat_id": "int", "page": "int"}, "params_map": {"id": "chat_id", "page": "page"}, "defaults": {"page": 1}},
    "chat_send_text": {"path": "/chat/new/json", "method": "POST", "type": 1, "token": True, "args": ["chat_id", "content"], "arg_types": {"chat_id": "int", "content": "str"}, "data_map": {"chat_id": "chat_id", "content": "content", "target": 0}},
    "chat_send_image": {"path": "/chat/new/json", "method": "POST", "type": 1, "token": True, "args": ["chat_id", "image_b64"], "arg_types": {"chat_id": "int", "image_b64": "str"}, "data_map": {"chat_id": "chat_id", "image": "image_b64", "target": 0}},
    "chat_pic": {"path": "/chat", "method": "GET", "type": 6, "domain": "HOST_CHAT_PIC", "args": ["chat_id"], "arg_types": {"chat_id": "int"}, "params_map": {"id": "chat_id"}},
    "user_payment_list": {"path": "/user/payment/json", "method": "GET", "type": 1, "token": True, "params_map": {"ac": "list"}},
    "user_payment_edit": {"path": "user/payment/json", "method": "POST", "type": 1, "token": True, "args": ["payid", "payurl", "paypwd"], "arg_types": {"payid": "int", "payurl": "str", "paypwd": "str"}, "params_map": {"ac": "edit", "id": "payid"}, "data_map": {"account": "payurl", "p": "paypwd"}},
    "user_payment_delete": {"path": "user/payment/json", "method": "POST", "type": 1, "token": True, "args": ["payid", "paypwd"], "arg_types": {"payid": "int", "paypwd": "str"}, "params_map": {"ac": "del", "id": "payid"}, "data_map": {"p": "paypwd"}},
    "user_payment_new": {"path": "user/payment/json", "method": "POST", "type": 1, "token": True, "args": ["aurl", "atype", "paypwd"], "arg_types": {"aurl": "str", "atype": "Union[PaymentType, int]", "paypwd": "str"}, "params_map": {"ac": "new"}, "data_map": {"account": "aurl", "t": "atype", "p": "paypwd"}},
}


class BeautyBox:
    HOST_DATA = HOST_DATA[0]
    HOST_CHAT_PIC = HOST_CHAT_PIC

    @staticmethod
    def __request__(crypto, typeint, method: str, path: str, **kwargs):
        domain = kwargs.pop("domain", BeautyBox.HOST_DATA)
        url = f"https://{domain}{path}"
        return BBoxRequest.request(crypto, typeint, method, url, **kwargs)


class AsyncBeautyBox:
    HOST_DATA = HOST_DATA[0]
    HOST_CHAT_PIC = HOST_CHAT_PIC

    @staticmethod
    async def __request__(crypto, typeint, method: str, path: str, **kwargs):
        domain = kwargs.pop("domain", AsyncBeautyBox.HOST_DATA)
        url = f"https://{domain}{path}"
        return await AsyncBBoxRequest.request(crypto, typeint, method, url, **kwargs)


def _create_api_method(name, config, is_async=False):
    """Dynamically create a static method for an API endpoint based on its configuration."""
    cls = AsyncBeautyBox if is_async else BeautyBox
    
    # 1. Build function signature
    arg_defs = ["crypto"]
    if config.get("token"):
        arg_defs.append("token")

    defined_args = config.get("args", [])
    defaults = config.get("defaults", {})
    for arg in defined_args:
        if arg in defaults:
            arg_defs.append(f"{arg}={repr(defaults[arg])}")
        else:
            arg_defs.append(arg)
    
    signature = ", ".join(arg_defs) + ", **kwargs"

    # 2. Build function body
    body_lines = []

    if 'atype' in defined_args:
        body_lines.append("    if isinstance(atype, PaymentType): atype = atype.value")

    def _format_value(v):
        return v if isinstance(v, str) and v in defined_args else repr(v)

    params_map = config.get("params_map", {})
    data_map = config.get("data_map", {})
    params_str = "{" + ", ".join(f"{repr(k)}: {_format_value(v)}" for k, v in params_map.items()) + "}"
    data_str = "{" + ", ".join(f"{repr(k)}: {_format_value(v)}" for k, v in data_map.items()) + "}"
    
    body_lines.append(f"    params = {params_str}")

    if config.get("device_info"):
        body_lines.append("    headers = BBoxRequest.update_headers(token=token if 'token' in locals() else None, **kwargs)")
        body_lines.append("    kwargs['headers'] = headers")
        device_data_str = "{'x2': headers['Device'], 'x3': int(headers['Os']), 'x4': headers['Com']}"
        body_lines.append(f"    data = {{**{data_str}, **{device_data_str}}}")
    else:
        body_lines.append(f"    data = {data_str}")

    # 3. Build the __request__ call
    domain = f"cls.{config.get('domain', 'HOST_DATA')}"
    
    request_kwargs = {"params": "params", "data": "data", "domain": domain}
    if config.get("token"):
        request_kwargs["token"] = "token"

    # We pass other kwargs through. The __request__ will pass them to the underlying request call.
    request_kwargs_str = ", ".join(f"{k}={v}" for k, v in request_kwargs.items())
    
    call_line = f"cls.__request__(crypto, {config['type']}, '{config['method']}', '{config['path']}', {request_kwargs_str}, **kwargs)"
    body_lines.append(f"    return {'await ' if is_async else ''}{call_line}")
    
    # 4. Create the function using exec
    full_body = "\n".join(body_lines)
    async_prefix = "async " if is_async else ""
    func_def = f"{async_prefix}def {name}({signature}):\n{full_body}"
    
    scope = {"cls": cls, "BBoxRequest": BBoxRequest, "PaymentType": PaymentType}
    exec(func_def, scope)
    return staticmethod(scope[name])


# Dynamically attach methods to classes
for name, config in __func_info__.items():
    if not config.get("manual"):
        # Create and attach synchronous method
        sync_method = _create_api_method(name, config, is_async=False)
        setattr(BeautyBox, name, sync_method)

        # Create and attach asynchronous method
        async_method = _create_api_method(name, config, is_async=True)
        setattr(AsyncBeautyBox, name, async_method)


def _generate_pyi_stubs():
    """Generates a .pyi stub file for IDE type hinting and autocompletion."""
    import os

    pyi_content = """\
# This file is generated automatically by beautybox.py.
# Do not edit this file manually.

from typing import Any, Union
from .constants import PaymentType
from .request import BBoxCryptoTemplate, AsyncBBoxCryptoTemplate

class BeautyBox:
"""

    # Generate stubs for BeautyBox (sync)
    for name, config in __func_info__.items():
        arg_defs = ["crypto: BBoxCryptoTemplate"]
        if config.get("token"):
            arg_defs.append("token: str")

        defined_args = config.get("args", [])
        arg_types = config.get("arg_types", {})
        defaults = config.get("defaults", {})
        for arg in defined_args:
            arg_type_str = f": {arg_types.get(arg, 'Any')}"
            if arg in defaults:
                arg_defs.append(f"{arg}{arg_type_str} = {repr(defaults[arg])}")
            else:
                arg_defs.append(f"{arg}{arg_type_str}")

        signature = ", ".join(arg_defs) + ", **kwargs"
        pyi_content += f"    @staticmethod\n    def {name}({signature}) -> Any: ...\n\n"

    pyi_content += """
class AsyncBeautyBox:
"""

    # Generate stubs for AsyncBeautyBox (async)
    for name, config in __func_info__.items():
        arg_defs = ["crypto: AsyncBBoxCryptoTemplate"]
        if config.get("token"):
            arg_defs.append("token: str")

        defined_args = config.get("args", [])
        arg_types = config.get("arg_types", {})
        defaults = config.get("defaults", {})
        for arg in defined_args:
            arg_type_str = f": {arg_types.get(arg, 'Any')}"
            if arg in defaults:
                arg_defs.append(f"{arg}{arg_type_str} = {repr(defaults[arg])}")
            else:
                arg_defs.append(f"{arg}{arg_type_str}")

        signature = ", ".join(arg_defs) + ", **kwargs"
        pyi_content += f"    @staticmethod\n    async def {name}({signature}) -> Any: ...\n\n"

    # Write to file
    file_path = os.path.join(os.path.dirname(__file__), "beautybox.pyi")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(pyi_content)
    print(f"Successfully generated stub file: {file_path}")


if __name__ == "__main__":
    _generate_pyi_stubs()
