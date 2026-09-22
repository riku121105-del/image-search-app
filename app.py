from io import BytesIO
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Googleレンズ風 Web画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 Web類似画像検索AI")

SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")

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
        if not SERPAPI_KEY:
            st.error("StreamlitのSecretsにSERPAPI_KEYが設定されていません。")
        else:
            with st.spinner("画像を解析・検索中..."):
                try:
                    # 1. 画像の軽量化処理
                    query_image.thumbnail((800, 800))
                    buffered = BytesIO()
                    query_image.save(buffered, format="JPEG", quality=85)
                    img_bytes = buffered.getvalue()

                    # 2. SerpApiの画像APIへアップロードして image_id を取得
                    upload_res = requests.post(
                        "https://serpapi.com/image",
                        files={"image": ("image.jpg", img_bytes, "image/jpeg")},
                        data={"api_key": SERPAPI_KEY},
                        timeout=15,
                    )
                    upload_data = upload_res.json()

                    if "image_id" not in upload_data:
                        err_msg = upload_data.get(
                            "error", "画像のアップロードに失敗しました。"
                        )
                        st.error(f"画像送信エラー: {err_msg}")
                    else:
                        image_id = upload_data["image_id"]

                        # 3. 取得した image_id を使って Google Lens 検索を実行
                        search_params = {
                            "engine": "google_lens",
                            "image_id": image_id,
                            "api_key": SERPAPI_KEY,
                            "hl": "ja",
                        }
                        search_res = requests.get(
                            "https://serpapi.com/search",
                            params=search_params,
                            timeout=30,
                        )
                        results = search_res.json()

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
