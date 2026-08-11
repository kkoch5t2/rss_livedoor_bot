import time
from google import genai
from .config import Config

class AIWriter:
    def __init__(self):
        self.key_index = 0
        self.model_index = 0

    def get_client(self):
        api_key = Config.AI_KEYS[self.key_index]
        return genai.Client(api_key=api_key)

    def switch_key(self):
        # Rotate to next key
        self.key_index = (self.key_index + 1) % len(Config.AI_KEYS)
        print(f"[*] APIを切り替えました。現在のキーインデックス: {self.key_index}")

    def switch_model(self):
        self.model_index = (self.model_index + 1) % len(Config.AI_MODELS)
        print(f"[*] AIモデルを切り替えました。現在のモデル: {Config.AI_MODELS[self.model_index]}")


    def generate_blog_post(self, data, category_name=""):
        print("[*] AI記事生成中...")
        news_title = data.get('title', '')
        news_text = data.get('text', '')

        if not news_text:
            print("[!] AI抽出スキップ: 本文データが空です。")
            return None, None, None

        prompt = f'''
    あなたは人気まとめ・ニュース解説サイトの管理人です。
    以下のニュース本文を元に、思わずクリックしたくなる魅力的なタイトルと、ブログ記事のHTML本文を作成してください。

    【入力ニュース】
    元記事タイトル: {news_title}
    本文: {news_text[:2000]}...

    【出力フォーマット】
    1行目に「CATEGORY: [カテゴリ名]」、2行目に「TITLE:タイトル」、3行目以降に「BODY:HTML本文」を記述してください。
    カテゴリは記事の内容を表す一般的な名詞（例: IT、経済、政治）にしてください。括弧は不要です。
    
    出力例:
    CATEGORY: テクノロジー
    TITLE: 【話題】〇〇の最新技術がすごい！
    BODY:
    <h3>記事の要約</h3>
    <p>ここに要約...</p>'''
        
        if category_name == "IT系ニュース":
            prompt += '''
    <h3>技術的深堀り</h3>
    <p>ここに技術的視点を交えた詳細な分析や考察...</p>

    【執筆要件】
    1. **タイトル**: 
       - 冒頭に【話題】【驚愕】【注目】【解説】などの隅付き括弧をつけること。
    2. **記事の要約**:
       - `<h3>記事の要約</h3>` という見出しで始める。
       - 3〜5行程度で分かりやすく具体的に要約すること。
    3. **技術的深堀り**:
       - `<h3>技術的深堀り</h3>` という見出しで始める。
       - データエンジニアやSREの視点から、ニュースの技術的な意義、データ基盤・インフラへの評価、実務への影響などを鋭く評論すること。
       - **※他の項目よりも少し詳しめに、4〜7行程度（または箇条書き3〜5点）でしっかりと解説すること。**
       - データエンジニアやSREが「なるほど」と思えるような、実運用に踏み込んだ専門的な知見を盛り込むこと。
    '''
        else:
            prompt += '''
    <h3>記事の分析</h3>
    <p>ここに社会的影響や将来の展望などの分析...</p>

    【執筆要件】
    1. **タイトル**: 
       - 冒頭に【話題】【驚愕】【注目】【解説】などの隅付き括弧をつけること。
    2. **記事の要約**:
       - `<h3>記事の要約</h3>` という見出しで始める。
       - 3〜5行程度で分かりやすく具体的に要約すること。
    3. **記事の分析**:
       - `<h3>記事の分析</h3>` という見出しで始める。
       - 社会的影響、将来の展望などを深く分析すること。
       - **※文字数が多くなりすぎないよう、3〜5行程度で簡潔にまとめること。**
    '''

        max_retries = len(Config.AI_KEYS) * len(Config.AI_MODELS)
        
        for attempt in range(max_retries):
            client = self.get_client()
            current_model = Config.AI_MODELS[self.model_index]
            try:
                print(f"[*] Generating content with model: {current_model} ...")
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt
                )
                
                content = response.text
                content = content.replace("```html", "").replace("```", "").strip()
                
                lines = content.split('\n')
                category = "ニュース"
                title = ""
                body = ""
                
                for i, line in enumerate(lines):
                    if line.startswith("CATEGORY:"):
                        category = line.replace("CATEGORY:", "").strip()
                    elif line.startswith("TITLE:"):
                        title = line.replace("TITLE:", "").strip()
                    elif line.startswith("BODY:"):
                        body = "\n".join(lines[i+1:]).strip()
                        break
                
                if not title:
                    title = f"【話題】{news_title}の解説"
                    body = content

                css = '''
                <style>
                h2, h3 { border-left: 5px solid #ff9900; padding-left: 10px; background: #fffcf0; margin-top: 20px; }
                </style>
                '''
                body = css + body
                
                return title, body, category

            except Exception as e:
                error_str = str(e)
                print(f"[!] AI Generation Error on attempt {attempt+1} (Model: {current_model}): {error_str}")
                if "404" in error_str or "not found" in error_str.lower() or "not supported" in error_str.lower():
                    self.switch_model()
                elif "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                    self.switch_key()
                else:
                    self.switch_model()
                time.sleep(2)
                
        print("[!] 全てのAPIキーで生成に失敗しました。")
        return None, None, None
