import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components
import os

# ページ設定
st.set_page_config(page_title="しろくまスタジオ", layout="wide")

# APIキー設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("SecretsにGEMINI_API_KEYが設定されていません。")
    st.stop()

# お手本画像
STYLE_IMAGE_PATH = "style.jpg"
style_img = None
if os.path.exists(STYLE_IMAGE_PATH):
    try:
        style_img = Image.open(STYLE_IMAGE_PATH)
    except:
        pass

# サイドバー
with st.sidebar:
    st.title("🐻 Shirokuma Studio")
    if style_img:
        st.image(style_img, caption="お手本スタイル", width=200)
    uploaded_file = st.file_uploader("変換したい画像をアップロード", type=["png", "jpg", "jpeg"])

# メイン画面
st.title("🎨 しろくまスタイル変換")

if uploaded_file:
    try:
        source_img = Image.open(uploaded_file)
        col1, col2 = st.columns(2)
        with col1:
            st.image(source_img, width=400)
        with col2:
            if st.button("しろくま呪文を生成", type="primary"):
                if style_img is None:
                    st.error("style.jpgが読み込めません。GitHubに画像を上げ直してください。")
                else:
                    with st.spinner("生成中..."):
                        model = genai.GenerativeModel('gemini-1.5-prp-version')
                        prompt = "画像1のスタイルで、画像2の要素を持つシロクマの英語プロンプトを作ってください。"
                        response = model.generate_content([prompt, style_img, source_img])
                        st.session_state.result = response.text
            
            if "result" in st.session_state:
                st.text_area("結果", value=st.session_state.result, height=150)
                safe_text = st.session_state.result.replace("`", "\\`").replace("$", "\\$")
                copy_js = f"""<button style="width:100%;height:40px;background:#4caf50;color:white;border:none;border-radius:8px;" onclick="navigator.clipboard.writeText(`{safe_text}`).then(()=>alert('コピー成功'))">📋 コピー</button>"""
                components.html(copy_js, height=50)
                st.link_button("🚀 ImageFXへ", "https://aitestkitchen.withgoogle.com/tools/image-fx")
    except Exception as e:
        st.error(f"エラー: {e}")
