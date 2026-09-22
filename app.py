import base64
from io import BytesIO
import requests
import streamlit as st
from PIL import Image
from serpapi import GoogleSearch

st.set_page_config(page_title="Googleレンズ風 Web画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 Web類似画像検索AI")

# --- SerpApi 設定 ---
SERPAPI_KEY = "d40d84efb3725876af1c33b63baf4xxxxxxxxxxxx"



def get_public_image_url(image_bytes):
    """複数サービスをフォールバック試行して画像URLを取得する"""
    # 1. tmpfiles.org
    try:
        res = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": ("image.jpg", image_bytes, "image/jpeg")},
            timeout=5,
        )
        if res.status_code == 200:
            url = res.json()["data"]["url"]
            # tmpfiles.org のURLを直リンク用 (dl/) に変換
            return url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    except Exception:
        pass

    # 2. file.io
    try:
        res = requests.post(
            "https://file.io",
            files={"file": ("image.jpg", image_bytes, "image/jpeg")},
            timeout=5,
        )
        if res.status_code == 200:
            return res.json()["link"]
    except Exception:
        pass

    # 3. ImgBB (フォールバック)
    try:
        payload = {
            "key": "3b0a232f38d3876be8695029f64bf876",
            "image": base64.b64encode(image_bytes).decode("utf-8"),
            "expiration": 600,
        }
        res = requests.post(
            "https://api.imgbb.com/1/upload", data=payload, timeout=5
        )
        if res.status_code == 200:
            return res.json()["data"]["url"]
    except Exception:
        pass

    return None


st.write("画像をアップロードすると、GoogleレンズでWeb上の類似画像を検索します。")

query_file = st.file_uploader(
    "検索したい画像をアップロードしてください", type=["jpg", "jpeg", "png"]
)

if query_file is not None:
    col1, col2 = st.columns([1, 2])
    query_image = Image.open(query_file).convert("RGB")

    with col1:
        st.image(
            query_image, caption="検索クエリ画像", use_container_width=True
        )

    with col2:
        if not SERPAPI_KEY or SERPAPI_KEY == "YOUR_SERPAPI_KEY_HERE":
            st.error("SerpApiのAPIキーが設定されていません。")
        else:
            with st.spinner("画像をGoogleレンズで解析・検索中..."):
                try:
                    # 画像軽量化 (800x800)
                    query_image.thumbnail((800, 800))
                    buffered = BytesIO()
                    query_image.save(buffered, format="JPEG", quality=85)
                    img_bytes = buffered.getvalue()

                    # 公開URLの取得（複数サービス試行）
                    public_url = get_public_image_url(img_bytes)

                    if not public_url:
                        st.error(
                            "画像の転送に失敗しました。少し時間をおいて再度お試しください。"
                        )
                    else:
                        # 本物の Google Lens エンジンを実行
                        params = {
                            "engine": "google_lens",
                            "url": public_url,
                            "api_key": SERPAPI_KEY,
                        }

                        search = GoogleSearch(params)
                        results = search.get_dict()

                        if "error" in results:
                            st.error(f"APIエラー: {results.get('error')}")
                        else:
                            visual_matches = results.get("visual_matches", [])

                            if visual_matches:
                                st.subheader("🎯 Web上の類似画像・見つかったページ")
                                for item in visual_matches[:5]:
                                    title = item.get("title", "タイトルなし")
                                    link = item.get("link", "#")
                                    thumbnail = item.get("thumbnail")
                                    source = item.get("source", "")

                                    res_col1, res_col2 = st.columns([1, 3])
                                    with res_col1:
                                        if thumbnail:
                                            st.image(
                                                thumbnail,
                                                use_container_width=True,
                                            )
                                    with res_col2:
                                        st.markdown(f"**[{title}]({link})**")
                                        if source:
                                            st.caption(f"出元: {source}")
                                    st.write("---")
                            else:
                                st.warning("類似画像が見つかりませんでした。")

                except Exception as e:
                    st.error(f"検索エラーが発生しました: {e}")
