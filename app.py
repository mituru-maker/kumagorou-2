import streamlit as st
import google.generativeai as genai

st.title("API接続テスト")

# Secretsの確認
if "GEMINI_API_KEY" in st.secrets:
    key = st.secrets["GEMINI_API_KEY"]
    st.success("APIキーはSecretsから読み込めています")
    
    # 接続テスト
    try:
        genai.configure(api_key=key)
        # モデル名を「models/」付きで指定（404対策）
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content("Hello")
        st.write("AIからの返答:", response.text)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
else:
    st.error("Secretsに GEMINI_API_KEY が見つかりません")
