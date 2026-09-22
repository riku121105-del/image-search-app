import streamlit as st
from serpapi import GoogleSearch

st.set_page_config(page_title="Googleレンズ風 Web画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 Web類似画像検索AI")

# --- SerpApi 設定 ---
SERPAPI_KEY = "d40d84efb3725876af1c33b63baf4..."  # ご自身のAPIキー

st.write("画像のURLを入力すると、Web上の類似画像をGoogle Lensで検索します。")

# 画像URLの入力フィールド
image_url = st.text_input(
    "検索したい画像のURL（https://〜）を入力してください",
    placeholder="https://example.com/sample.jpg",
)

if image_url:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(image_url, caption="検索クエリ画像", use_container_width=True)

    with col2:
        if not SERPAPI_KEY or SERPAPI_KEY == "YOUR_SERPAPI_KEY_HERE":
            st.error("SerpApiのAPIキーが設定されていません。")
        else:
            with st.spinner("GoogleレンズでWeb上を検索中..."):
                try:
                    # SerpApi 経由で Google Lens を実行（URL指定）
                    params = {
                        "engine": "google_lens",
                        "url": image_url,
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
