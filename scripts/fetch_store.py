"""store_config.json의 제품 목록으로 docs/store.json과 docs/store-img/를 만든다.

네이버 쇼핑 검색 API는 2026-07-31에 종료됐고, 스마트스토어 페이지는 robots.txt로 수집이 금지돼 있다.
그래서 제품 목록은 수민 PC에서 커머스API로 받은 결과(scripts/naver_products_pc.py)를 store_config.json에 옮겨 적고,
이 스크립트는 이미지를 저장소로 옮겨 오는 일만 한다. 목록을 고친 뒤 직접 실행해 docs와 함께 커밋한다.
"""
import hashlib
import json
import pathlib
import re
import urllib.parse
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
ROOT = REPO / "docs"
IMG = ROOT / "store-img"
CONFIG = REPO / "store_config.json"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (hwasim-store-feed)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def thumb(url):
    """네이버 상품 이미지는 원본이 수 MB라 CDN의 축소본(가로 640px JPEG)을 받는다."""
    if urllib.parse.urlparse(url).netloc == "shop-phinf.pstatic.net" and "?" not in url:
        return url + "?type=f640", ".jpg"
    return url, ext(url)


def ext(url):
    suffix = pathlib.PurePosixPath(urllib.parse.urlparse(url).path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"} else ".jpg"


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    IMG.mkdir(parents=True, exist_ok=True)
    out, keep = {}, set()
    for brand, products in cfg["products"].items():
        out[brand] = []
        for p in products:
            src = p["image"]
            # 대표 이미지를 바꾸면 주소도 바뀌므로 주소 해시를 파일 이름에 넣는다.
            url, suffix = thumb(src)
            name = re.sub(r"[^\w-]", "_", p["id"]) + "-" + hashlib.sha1(url.encode()).hexdigest()[:8] + suffix
            path = IMG / name
            if not path.exists():
                path.write_bytes(get(url))
            keep.add(name)
            item = {"id": p["id"], "name": p["name"], "link": p["link"], "image": f"store-img/{name}"}
            if p.get("name_en"):
                item["name_en"] = p["name_en"]
            if p.get("soldout"):
                item["soldout"] = True
            out[brand].append(item)

    for f in IMG.iterdir():
        if f.name not in keep:
            f.unlink()

    (ROOT / "store.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved " + ", ".join(f"{b} {len(v)}" for b, v in out.items()))


if __name__ == "__main__":
    main()
