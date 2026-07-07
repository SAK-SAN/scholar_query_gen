# scholar_sdk.py
from google import genai
from typing import List

class ScholarQuerySDK:
    """
    Google Scholar用の検索クエリを生成するための自作SDKクラス。
    内部でGoogle GenAI SDKを利用し、モデルの動的取得とクエリ生成を行います。
    """
    def __init__(self, api_key: str):
        """APIキーを受け取り、Google GenAIクライアントを初期化する"""
        if not api_key:
            raise ValueError("APIキーが空です。有効なGemini APIキーを指定してください。")
        
        # Google公式の最新Clientインスタンスを保持
        self._client = genai.Client(api_key=api_key)

    def get_available_models(self) -> List[str]:
        """
        利用可能なGeminiモデルの中から、
        テキスト生成（generateContent）に対応しているモデルを動的に取得してリストで返します。
        """
        try:
            models = []
            # 公式SDKの機能でモデル一覧を取得
            for model in self._client.models.list():
                # テキスト生成（generateContent）をサポートしているか検証
                if "generateContent" in model.supported_generation_methods:
                    models.append(model.name)
            return models
        except Exception as e:
            # エラー時は空リストを返し、上位層（UI）へログを残せるように例外を再送出するか、ハンドリングする
            print(f"[ScholarQuerySDK Error] モデル一覧の取得に失敗しました: {e}")
            return []

    def generate_queries(self, model_name: str, keyword: str) -> str:
        """
        指定されたモデルと研究キーワードから、4パターンの検索クエリ（各10個）を生成します。
        """
        if not keyword.strip():
            raise ValueError("キーワードが指定されていません。")

        prompt = f"""
        あなたは学術リサーチの専門家です。
        以下の研究キーワードに対して、Google Scholar等の学術検索エンジンで精度の高い検索を行うためのクエリを生成してください。

        キーワード: {keyword}

        以下の4パターンについて、それぞれ10個ずつクエリを出力してください。
        検索精度を最大化するため、パターン2と4では検索演算子（AND, OR, "", site:ac.jp, site:edu, filetype:pdf, intitle: など）を効果的に組み込んでください。

        【出力形式】
        各パターンごとにマークダウンのヘッダー（###）を用い、各クエリは必ずワンライナーのコードブロック（```text ... ```）にして、ユーザーが1クリックでコピーできるようにしてください。箇ページ番号や箇条書きの番号はコードブロックの外に記述してください。

        1. 日本語 × 文章形式
        2. 日本語 × ブール演算形式
        3. 英語 × 文章形式
        4. 英語 × ブール演算形式
        """

        try:
            # 指定されたモデル名でコンテンツ生成を実行
            response = self._client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini APIによるクエリ生成中にエラーが発生しました: {e}")