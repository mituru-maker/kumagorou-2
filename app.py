import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components
import os

# --- 1. ページ設定とデザイン ---
st.set_page_config(page_title="アニマル・スタイル・スタジオ", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f7f9; }
    .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .copy-btn { width: 100%; height: 3.5em; background-color: #4caf50; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; }
    .copy-btn:hover { background-color: #43a047; }
    </style>
""", unsafe_allow_html=True)

# --- 2. APIキーの設定 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secretsに 'GEMINI_API_KEY' を登録してください。")
    st.stop()

# --- 3. サイドバー：お手本選択 ---
with st.sidebar:
    st.title("🐾 Animal Studio")
    
    # お手本の種類を選択（3種類に絞り込み）
    style_type = st.radio(
        "お手本を選択してください：",
        ["シロクマ", "カバ", "シャチ"],
        index=0
    )

    # 選択に合わせてファイル名を決定
    style_files = {
        "シロクマ": "style.jpg",
        "カバ": "hippo.jpg",
        "シャチ": "orca.jpg"
    }
    target_file = style_files[style_type]

    # 画像の読み込み
    style_img = None
    if os.path.exists(target_file):
        style_img = Image.open(target_file)
        st.subheader(f"🎨 {style_type}スタイル")
        st.image(style_img, use_container_width=True)
    else:
        st.error(f"'{target_file}' が見つかりません。")
        st.info(f"GitHubに {target_file} という名前で画像をアップロードしてください。")

    st.divider()
    uploaded_file = st.file_uploader("変換したい元の画像", type=["png", "jpg", "jpeg"])

# --- 4. メインコンテンツ ---
st.title(f"🎨 {style_type}スタイル変換ジェネレーター")

# 選択が変わったときに結果をリセット
if "last_style" not in st.session_state:
    st.session_state.last_style = style_type

if st.session_state.last_style != style_type:
    st.session_state.analysis_result = ""
    st.session_state.last_style = style_type

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

if uploaded_file and style_img:
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
        
        if st.button(f"{style_type}に合わせて呪文を生成"):
            with st.status(f"{style_type}のスタイルを分析中...") as status:
                try:
                    model = genai.GenerativeModel('gemini-3-flash-preview')
                    
                    instruction = f"""
                    あなたはキャラクターデザインのプロフェッショナルです。
                    
                    1. 画像1（お手本）: ターゲットとなる{style_type}の特定の「絵柄・スタイル」。
                    2. 画像2（変換元）: 移植したい「服装・ポーズ・持ち物」。

                    画像1の「線の太さ」「色使い」「独特な顔の描き方」を完璧に守りつつ、
                    画像2のキャラクターがしている「格好やポーズ」を{style_type}で再現するための、
                    画像生成AI（ImageFX等）で使える詳細な英語プロンプトを作成してください。
                    """
                    
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
                    navigator.clipboard.writeText(text).then(() => alert("プロンプトをコピーしました！"));
                }}
                </script>
                <button class="copy-btn" onclick="copyToClipboard()">📋 プロンプトをコピー</button>
            """
            components.html(copy_js, height=70)
            st.link_button("🚀 ImageFXを開く", "https://aitestkitchen.withgoogle.com/tools/image-fx", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    if not style_img:
        st.info(f"サイドバーで「{style_type}」の画像が正しく表示されているか確認してください。")
    else:
        st.info("変換したい画像をアップロードしてください。")
