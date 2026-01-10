import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components
import os

# --- 1. ページ設定とデザイン ---
st.set_page_config(page_title="しろくまスタイル・スタジオ", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f7f9; }
    .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .copy-btn { width: 100%; height: 3.5em; background-color: #4caf50; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; }
    .copy-btn:hover { background-color: #43a047; }
    </style>
""", unsafe_allow_html=True)

# --- 2. お手本画像の読み込み (.jpgに対応) ---
STYLE_IMAGE_PATH = "style.jpg" 

def get_style_image():
    # .jpg が存在するかチェック
    if os.path.exists(STYLE_IMAGE_PATH):
        return Image.open(STYLE_IMAGE_PATH)
    return None

style_img = get_style_image()

# --- 3. サイドバー ---
with st.sidebar:
    st.title("🐻 Shirokuma Studio")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    
    st.divider()
    if style_img:
        st.subheader("🎨 ベーススタイル（固定）")
        st.image(style_img, caption="このシロクマをお手本にします", use_container_width=True)
    else:
        st.error(f"エラー: '{STYLE_IMAGE_PATH}' が見つかりません。")
        st.info("app.pyと同じフォルダに 'style.jpg' を置いてください。")

    uploaded_file = st.file_uploader("変換したい元の画像", type=["png", "jpg", "jpeg"])

# --- 4. メインコンテンツ ---
st.title("🎨 しろくまスタイル変換ジェネレーター")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

if uploaded_file and api_key and style_img:
    source_img = Image.open(uploaded_file)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📸 変換元の画像")
        st.image(source_img, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📝 スタイル融合プロンプト")
        
        if st.button("お手本に合わせて呪文を生成"):
            with st.status("2枚の画像を融合して分析中...") as status:
                try:
                    # 最新モデル Gemini 3 Flash Preview を使用
                    model = genai.GenerativeModel('gemini-3-flash-preview')
                    
                    # 2枚の画像を融合させる強力なプロンプト
                    instruction = """
                    あなたは、既存のキャラクターデザインの「スタイル」を別の要素へ移植するプロフェッショナルです。
                    
                    【入力データ】
                    1. 画像1（お手本）: ターゲットとなるシロクマの「絵柄・スタイル」。
                    2. 画像2（変換元）: 移植したい「服装・ポーズ・持ち物」。

                    【あなたのタスク】
                    画像1の「線の太さ」「色使い」「顔の描き方（目の位置や鼻の形）」を完璧に守ったまま、
                    画像2のキャラクターがしている「格好やポーズ」を再現するための、画像生成AI用プロンプト（英語）を作成してください。

                    【出力形式】
                    ■分析（日本語）: 画像2のどの要素を、画像1のスタイルでどう再現するか。
                    ■英語プロンプト: そのままコピーしてImageFX等の生成AIで使える、詳細な英文。
                    """
                    
                    # 2枚の画像とお手本を同時に渡す
                    response = model.generate_content([instruction, style_img, source_img])
                    st.session_state.analysis_result = response.text
                    status.update(label="融合完了！", state="complete")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

        if st.session_state.analysis_result:
            st.text_area("生成結果", value=st.session_state.analysis_result, height=200)
            
            # クリップボードコピー機能
            safe_text = st.session_state.analysis_result.replace("`", "\\`").replace("$", "\\$")
            copy_js = f"""
                <script>
                function copyToClipboard() {{
                    const text = `{safe_text}`;
                    navigator.clipboard.writeText(text).then(() => alert("プロンプトをクリップボードにコピーしました！"));
                }}
                </script>
                <button class="copy-btn" onclick="copyToClipboard()">📋 プロンプトをコピー</button>
            """
            components.html(copy_js, height=70)
            st.link_button("🚀 ImageFXを開く", "https://aitestkitchen.withgoogle.com/tools/image-fx", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("APIキーを入力し、変換したい画像をアップロードしてください。")
