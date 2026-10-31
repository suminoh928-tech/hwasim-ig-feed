"""네이버 커머스API로 화심주조 스마트스토어 상품 목록을 받아 같은 폴더의 products.json에 저장한다.

수민 PC(호출 IP로 등록된 사무실 PC)에서 Remote Control로 필요할 때만 실행한다.
키는 Windows 사용자 환경 변수 NAVER_COMMERCE_ID, NAVER_COMMERCE_SECRET에서 읽고, 화면·파일 어디에도 남기지 않는다.
"""
import base64
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import winreg

import bcrypt

API = "https://api.commerce.naver.com/external"
STORE = "https://smartstore.naver.com/hwasimjujo/products/"
OUT = pathlib.Path(__file__).with_name("products.json")
STATUSES = ["SALE", "OUTOFSTOCK"]


def env(name):
    # Remote Control 프로세스가 환경 변수 등록 전에 떠 있어도 읽히도록 레지스트리에서 직접 읽는다.
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
        return str(winreg.QueryValueEx(key, name)[0]).strip()


def call(path, data, token=None):
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode()
    if token is None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urllib.parse.urlencode(data).encode()
    else:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API + path, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        # 오류 본문에는 키가 들어 있지 않다. IP 미등록이면 GW.IP_NOT_ALLOWED가 보인다.
        sys.exit("HTTP %s %s: %s" % (e.code, path, e.read().decode("utf-8", "replace")[:300]))


def issue_token(client_id, secret):
    ts = str(int(time.time() * 1000))
    sign = base64.b64encode(bcrypt.hashpw((client_id + "_" + ts).encode(), secret.encode())).decode()
    form = {"client_id": client_id, "timestamp": ts, "client_secret_sign": sign,
            "grant_type": "client_credentials", "type": "SELF"}
    return call("/v1/oauth2/token", form)["access_token"]


def main():
    token = issue_token(env("NAVER_COMMERCE_ID"), env("NAVER_COMMERCE_SECRET"))
    products, page = [], 1
    while True:
        data = call("/v1/products/search", {"productStatusTypes": STATUSES, "page": page, "size": 100, "orderType": "REG_DATE"}, token)
        for content in data.get("contents", []):
            for ch in content.get("channelProducts", []):
                if ch.get("channelServiceType") != "STOREFARM":
                    continue
                products.append({
                    "id": str(ch["channelProductNo"]),
                    "name": ch.get("name", ""),
                    "status": ch.get("statusType"),
                    "display": ch.get("channelProductDisplayStatusType"),
                    "link": STORE + str(ch["channelProductNo"]),
                    "image": (ch.get("representativeImage") or {}).get("url", ""),
                })
        if data.get("last", True) or page >= data.get("totalPages", 1):
            break
        page += 1
    OUT.write_text(json.dumps({"fetched": time.strftime("%Y-%m-%d %H:%M"), "products": products}, ensure_ascii=False, indent=1), encoding="utf-8")
    for p in products:
        print("%s | %s | %s | %s | %s" % (p["status"], p["display"], p["name"], p["link"], p["image"]))
    print("총 %d개, 저장: %s" % (len(products), OUT))


if __name__ == "__main__":
    main()
