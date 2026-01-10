import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# ページ設定
st.set_page_config(page_title="しろくまスタジオ", layout="wide")

# APIキー設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secretsにキーが設定されていません。")
    st.stop()

# 画像読み込み
style_img = None
if os.path.exists("style.jpg"):
    try:
        style_img = Image.open("style.jpg")
    except:
        pass

st.title("🎨 しろくまスタイル変換")

uploaded_file = st.sidebar.file_uploader("画像をアップ", type=["png", "jpg", "jpeg"])

if uploaded_file and style_img:
    source_img = Image.open(uploaded_file)
    
    if st.button("呪文を生成"):
        with st.spinner("AIが解析中..."):
            try:
                # 【ここを修正】最も標準的なモデル名に変更
                # flashで404が出る場合は、この gemini-1.5-pro が正解のケースが多いです
                model = genai.GenerativeModel('gemini-1.5-pro') 
                
                prompt = "画像1の画風で、画像2のポーズをしたクマを描く英語プロンプトを作ってください。"
                response = model.generate_content([prompt, style_img, source_img])
                st.write(response.text)
                
            except Exception as e:
                # エラーが出た場合、別の名前で自動リトライ
                try:
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    response = model.generate_content([prompt, style_img, source_img])
                    st.write(response.text)
                except Exception as e2:
                    st.error(f"モデルが見つかりません。APIキーの設定を確認してください。詳細: {e2}")

elif not style_img:
    st.warning("style.jpg が見つかりません。GitHubにアップロードされているか確認してください。")
