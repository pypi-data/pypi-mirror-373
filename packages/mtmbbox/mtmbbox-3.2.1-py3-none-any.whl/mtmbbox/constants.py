from enum import IntEnum


class PaymentType(IntEnum):
    alipay = 1
    wxpay = 2

APP_VERSION = "5.1.5"
APP_OS = "13"
APP_RES = "1080x2400"

TIMEOUT_DEFAULT = 10

HOST_DATA = ("qq.taoqq163.com", "baidu.taokuai163.com")
HOST_GAME = "sina.taokuai163.com"
HOST_LONG_VIDEO = "rr2sn.taobaoqq126.com"
HOST_LONG_VIDEO_COVER = "p.qqsina163.com"
HOST_CHAT_PIC = "store.c13579.com"

HEADERS_BASE = {
    "Cache-Control": "no-cache",
    "Content-Type": "application/json; charset=utf-8",
    "Accept-Encoding": "gzip",
    "Os": APP_OS,
    "Ver": APP_VERSION,
    "Res": APP_RES,
}

DEVICES_COMPANY = (
    "vivo(vivo V1)",
    "HONOR(PCT-AL10)",
    "HUAWEI(HUAWEI NXT-CL00)",
    "HUAWEI(HUAWEI TAG-AL00)",
    "Xiaomi(MI 3W)",
    "Xiaomi(MI 6X)",
    "HUAWEI(MLD-AL10)",
    "HUAWEI(HUAWEI G7-L11)",
    "HUAWEI(G620S-UL0)",
    "OnePlus(ONEPLUS)",
    "OPPO(PAHM00)",
    "OPPO(PDNT00)",
    "HUAWEI(HUAWEI C8816D)",
    "OPPO(OPPO R11)",
    "TP-LINK(Neffos Y5L)",
    "Xiaomi(MI 5)",
    "Redmi(Redmi K30 Pro Zoom Edition)",
    "HUAWEI(generic_a53_32)",
    "OPPO(OPPO R9)",
    "vivo(Y29L)",
    "Redmi(M2010J19SC)",
    "realme(RMX3461)",
    "OPPO(A57)",
    "vivo(vivo Y913)",
)


