import base64
from io import BytesIO
import streamlit as st
from PIL import Image
from serpapi import GoogleSearch

st.set_page_config(page_title="Googleレンズ風 Web画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 Web類似画像検索AI")

# --- SerpApi 設定 ---
SERPAPI_KEY = "d40d84efb3725876af1c33b63baf4..."  # ご自身のAPIキー

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
            with st.spinner("Web上を自動検索中..."):
                try:
                    # 画像をリサイズして軽量化
                    query_image.thumbnail((600, 600))
                    buffered = BytesIO()
                    query_image.save(buffered, format="JPEG", quality=80)
                    img_base64 = base64.b64encode(buffered.getvalue()).decode(
                        "utf-8"
                    )

                    # Google Reverse Image Search（直接画像送信に対応）
                    params = {
                        "engine": "google_reverse_image",
                        "image_url": f"data:image/jpeg;base64,{img_base64}",
                        "api_key": SERPAPI_KEY,
                    }

                    search = GoogleSearch(params)
                    results = search.get_dict()

                    if "error" in results:
                        st.error(f"APIエラー: {results.get('error')}")
                    else:
                        inline_images = results.get("inline_images", [])
                        image_results = results.get("image_results", [])
                        matches = inline_images or image_results

                        if matches:
                            st.subheader("🎯 Web上の類似画像・見つかったページ")
                            for item in matches[:5]:
                                title = item.get("title", "関連ページ")
                                link = item.get("link", "#")
                                thumbnail = item.get("thumbnail") or item.get(
                                    "original"
                                )
                                source = item.get("source", "")

                                res_col1, res_col2 = st.columns([1, 3])
                                with res_col1:
                                    if thumbnail:
                                        st.image(
                                            thumbnail, use_container_width=True
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
