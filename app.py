import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="Googleレンズ風 Web画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 Web類似画像検索AI")

SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")

st.write("画像をアップロードすると、GoogleでWeb上の類似画像を検索します。")

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
        if not SERPAPI_KEY:
            st.error("StreamlitのSecretsにSERPAPI_KEYが設定されていません。")
        else:
            with st.spinner("画像を解析・検索中..."):
                try:
                    query_file.seek(0)
                    file_bytes = query_file.read()

                    # google_reverse_image エンジンを使用し、直接ファイルを送信
                    url = "https://serpapi.com/search"
                    params = {
                        "engine": "google_reverse_image",
                        "api_key": SERPAPI_KEY,
                        "hl": "ja",
                    }
                    files = {"image_url": ("image.jpg", file_bytes, "image/jpeg")}

                    response = requests.post(
                        url, params=params, files=files, timeout=30
                    )
                    results = response.json()

                    if "error" in results:
                        st.error(f"APIエラー: {results.get('error')}")
                    else:
                        image_results = results.get("image_results", []) or results.get("inline_images", [])

                        if image_results:
                            st.subheader("🎯 Web上の類似画像・見つかったページ")
                            for item in image_results[:5]:
                                title = item.get("title", "タイトルなし")
                                link = item.get("link", "#")
                                thumbnail = item.get("thumbnail") or item.get("original")
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
