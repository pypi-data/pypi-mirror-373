import base64


def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read())
    return image_base64


def url2proxies(url):
    if not isinstance(url, str) or url.lower() == "none" or url.lower() == "null":
        return None
    return {"http": url, "https": url}
