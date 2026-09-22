import base64
import streamlit as st
from PIL import Image
from serpapi import GoogleSearch

st.set_page_config(page_title="Googleレンズ風 Web画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 Web類似画像検索AI")

# --- Secrets から APIキーを取得 ---
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
            with st.spinner("画像をGoogleレンズで解析・検索中..."):
                try:
                    # 画像をBase64形式に変換（外部画像アップロードを使わない方式）
                    import io

                    buffered = io.BytesIO()
                    query_image.save(buffered, format="JPEG", quality=85)
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    data_url = f"data:image/jpeg;base64,{img_str}"

                    params = {
                        "engine": "google_lens",
                        "url": data_url,
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
