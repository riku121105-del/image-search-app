import base64
from io import BytesIO
import requests
import streamlit as st
from PIL import Image
from serpapi import GoogleSearch

st.set_page_config(page_title="Googleレンズ風 Web画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 Web類似画像検索AI")

# --- SerpApi 設定 ---
SERPAPI_KEY = "d40d84efb3725876af1c33b63baf4..."  # ご自身のAPIキー

# --- ImgBB 無料APIキー（画像一時保存用） ---
IMGBB_API_KEY = "3b0a232f38d3876be8695029f64bf876"  # 一時アップロード用の共有キー


def upload_to_imgbb(image_bytes):
    """画像を一時的にWeb公開URLに変換する"""
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": base64.b64encode(image_bytes).decode("utf-8"),
        "expiration": 600,  # 10分後に自動削除
    }
    res = requests.post(url, data=payload)
    if res.status_code == 200:
        return res.json()["data"]["url"]
    return None


st.write("画像をアップロードすると、自動でWeb上の類似画像を検索します。")

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
            with st.spinner("画像を処理して検索中..."):
                try:
                    # リサイズ＆圧縮
                    query_image.thumbnail((800, 800))
                    buffered = BytesIO()
                    query_image.save(buffered, format="JPEG", quality=85)
                    img_bytes = buffered.getvalue()

                    # 1. 一時的にWeb URLへ変換
                    public_url = upload_to_imgbb(img_bytes)

                    if not public_url:
                        st.error("画像の処理（一時アップロード）に失敗しました。")
                    else:
                        # 2. SerpApiでGoogle Lensを実行
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
