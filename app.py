import base64
from io import BytesIO
import streamlit as st
from PIL import Image
from serpapi import GoogleSearch

st.set_page_config(page_title="Googleレンズ風 Web画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 Web類似画像検索AI")

# --- SerpApi 設定 ---
SERPAPI_KEY = "d40d84efb3725876af1c33b63baf4..."  # ご自身のAPIキー

st.write("画像をアップロードすると、自動でWeb全体の類似画像を検索します。")

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
        if SERPAPI_KEY == "YOUR_SERPAPI_KEY_HERE" or not SERPAPI_KEY:
            st.error("SerpApiのAPIキーが設定されていません。")
        else:
            with st.spinner("Googleレンズ風にWeb上を検索中..."):
                try:
                    # 画像サイズをリサイズして容量を小さく（エラー回避対策）
                    query_image.thumbnail((800, 800))
                    buffered = BytesIO()
                    query_image.save(buffered, format="JPEG", quality=85)
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                    # SerpApi 経由で Google Lens を実行
                    params = {
                        "engine": "google_lens",
                        "url": f"data:image/jpeg;base64,{img_str}",
                        "api_key": SERPAPI_KEY,
                    }

                    search = GoogleSearch(params)
                    results = search.get_dict()

                    # エラーレスポンスが含まれるかチェック
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
