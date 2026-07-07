# app.py
import streamlit as st
# 自作したSDKクラスをインポート
from sholar_sdk import ScholarQuerySDK

# UIの基本設定
st.set_page_config(page_title="Scholar Query Generator", layout="wide", page_icon="🔍")

# ----------------------------------------
# 自作SDKインスタンスのキャッシュ管理
# ----------------------------------------
@st.cache_resource
def init_scholar_sdk(api_key: str) -> ScholarQuerySDK:
    """自作SDKのインスタンスを生成してキャッシュする（再実行時のオーバーヘッドを防止）"""
    return ScholarQuerySDK(api_key=api_key)


# ----------------------------------------
# アプリケーション メイン処理
# ----------------------------------------
st.title("🔍 Google Scholar 検索クエリ生成アプリ (SDKベース)")
st.markdown("自作の `ScholarQuerySDK` モジュールを利用して、選択されたGeminiモデルで最適な学術検索クエリを生成します。")

# StreamlitのSecretsからAPIキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーが設定されていません。`.streamlit/secrets.toml` または Streamlit CloudのSecretsを確認してください。")
    st.stop()

try:
    # 1. 自作SDKの初期化
    scholar_sdk = init_scholar_sdk(api_key)
    
    # 2. 自作SDKから利用可能なモデル一覧を動的に取得
    available_models = scholar_sdk.get_available_models()
    
    if not available_models:
        st.error("利用可能なGeminiモデルが見つかりませんでした。")
        st.stop()

    # デフォルトモデル（gemini-1.5-flash）がリストにあれば初期選択位置にする
    default_model = "models/gemini-1.5-flash"
    default_index = available_models.index(default_model) if default_model in available_models else 0

    # サイドバーでモデルを動的に選択
    st.sidebar.header("SDK設定")
    selected_model = st.sidebar.selectbox(
        "使用するGeminiモデルを選択",
        options=available_models,
        index=default_index,
        help="SDKが自動検知した、テキスト生成に対応しているモデル一覧です。"
    )
    st.sidebar.markdown(f"**現在アクティブなモデル:** \n`{selected_model}`")

    # メイン画面の入力フォーム
    with st.form("query_form"):
        keyword_input = st.text_input(
            "研究キーワードを入力してください", 
            placeholder="例: 自動運転 アルゴリズム 安全性評価"
        )
        submitted = st.form_submit_button("クエリを生成する", type="primary")

    # 実行処理
    if submitted:
        if not keyword_input.strip():
            st.warning("キーワードを入力してください。")
        else:
            with st.spinner(f"自作SDKを通じて {selected_model.split('/')[-1]} を呼び出し中..."):
                try:
                    # 3. 自作SDKのメソッドを使ってクエリを生成
                    result = scholar_sdk.generate_queries(
                        model_name=selected_model, 
                        keyword=keyword_input
                    )
                    st.success("クエリの生成が完了しました！")
                    st.markdown(result)
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")

except Exception as e:
    st.error(f"SDKの初期化中に致命的なエラーが発生しました: {e}")