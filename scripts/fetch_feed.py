"""인스타그램 최근 게시물을 받아 docs/feed.json과 docs/img/에 저장한다.

인스타그램 CDN 주소는 시간이 지나면 만료되므로 이미지를 저장소에 내려받아 둔다.
"""
import json
import os
import pathlib
import urllib.parse
import urllib.request

COUNT = 9
ROOT = pathlib.Path(__file__).resolve().parent.parent / "docs"
IMG = ROOT / "img"
FIELDS = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp"


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()


def main():
    token = os.environ["IG_TOKEN"]
    q = urllib.parse.urlencode({"fields": FIELDS, "limit": COUNT, "access_token": token})
    # IG_USER_ID가 있으면 Facebook 페이지 토큰 방식, 없으면 Instagram 로그인 토큰 방식.
    user_id = os.environ.get("IG_USER_ID", "").strip()
    if user_id:
        url = f"https://graph.facebook.com/v21.0/{user_id}/media?{q}"
    else:
        url = f"https://graph.instagram.com/me/media?{q}"
    data = json.loads(get(url))["data"]

    IMG.mkdir(parents=True, exist_ok=True)
    posts, keep = [], set()
    for m in data:
        # 동영상은 썸네일, 사진·캐러셀은 대표 이미지를 쓴다.
        src = m.get("thumbnail_url") if m["media_type"] == "VIDEO" else m.get("media_url")
        if not src:
            continue
        name = f"{m['id']}.jpg"
        path = IMG / name
        if not path.exists():
            path.write_bytes(get(src))
        keep.add(name)
        caption = (m.get("caption") or "").strip()
        posts.append({
            "id": m["id"],
            "image": f"img/{name}",
            "link": m["permalink"],
            "caption": caption[:120],
            "type": m["media_type"],
            "time": m["timestamp"],
        })

    for f in IMG.glob("*.jpg"):
        if f.name not in keep:
            f.unlink()

    (ROOT / "feed.json").write_text(json.dumps({"posts": posts}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"saved {len(posts)} posts")


if __name__ == "__main__":
    main()
