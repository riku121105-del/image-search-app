import os
import chromadb
from PIL import Image
import streamlit as st
import torch
from transformers import CLIPModel, CLIPProcessor

st.set_page_config(page_title="Googleレンズ風 画像検索AI", layout="wide")
st.title("🔍 Googleレンズ風 類似画像検索AI")


@st.cache_resource
def load_clip_model():
    model_name = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    return model, processor


model, processor = load_clip_model()


def extract_features(image):
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        # CLIPで画像特徴量を抽出
        features = model.get_image_features(**inputs)

        # 出力がBaseModelOutput等のオブジェクトの場合、tensorを取り出す
        if not isinstance(features, torch.Tensor):
            features = getattr(
                features,
                "image_embeds",
                getattr(features, "logits_per_image", features[0]),
            )

        # 正規化
        features = features / features.norm(p=2, dim=-1, keepdim=True)

    return features.cpu().numpy().flatten().tolist()


@st.cache_resource
def get_chroma_collection():
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_or_create_collection(
        name="image_search", metadata={"hnsw:space": "cosine"}
    )


collection = get_chroma_collection()

st.sidebar.header("📁 検索対象画像の登録")
uploaded_data_files = st.sidebar.file_uploader(
    "データベースに登録する画像を複数選択",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if st.sidebar.button("データベースに保存・インデックス化"):
    if uploaded_data_files:
        os.makedirs("./saved_images", exist_ok=True)
        progress_bar = st.sidebar.progress(0)

        for i, file in enumerate(uploaded_data_files):
            save_path = os.path.join("./saved_images", file.name)
            image = Image.open(file).convert("RGB")
            image.save(save_path)

            feature_vector = extract_features(image)
            collection.upsert(
                ids=[file.name],
                embeddings=[feature_vector],
                metadatas=[{"path": save_path}],
            )
            progress_bar.progress((i + 1) / len(uploaded_data_files))

        st.sidebar.success(
            f"{len(uploaded_data_files)} 枚の画像を登録しました！"
        )
    else:
        st.sidebar.warning("画像を選択してください。")

st.write("---")
st.subheader("📸 画像をアップロードして類似画像を検索")

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
        if st.button("似ている画像を検索する", type="primary"):
            if collection.count() == 0:
                st.error(
                    "データベースに画像が登録されていません。左のサイドバーから画像を登録してください。"
                )
            else:
                with st.spinner("AIが類似画像を検索中..."):
                    query_vector = extract_features(query_image)
                    results = collection.query(
                        query_embeddings=[query_vector], n_results=3
                    )

                    st.subheader("🎯 検索結果")
                    res_cols = st.columns(3)

                    for idx, (doc_id, distance, metadata) in enumerate(
                        zip(
                            results["ids"][0],
                            results["distances"][0],
                            results["metadatas"][0],
                        )
                    ):
                        similarity_score = max(0, (1 - distance) * 100)
                        img_path = metadata["path"]

                        with res_cols[idx]:
                            if os.path.exists(img_path):
                                result_img = Image.open(img_path)
                                st.image(
                                    result_img,
                                    caption=f"順位 {idx+1}\n類似度: {similarity_score:.1f}%",
                                    use_container_width=True,
                                )
