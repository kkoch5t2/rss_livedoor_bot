import os
import json
from pathlib import Path

class Config:
    # ----------------------------------------------------------------
    # Load ACCOUNTS from settings.json
    # ----------------------------------------------------------------
    SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
    ACCOUNTS = []
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                ACCOUNTS = json.load(f)
        except Exception as e:
            print(f"Error loading settings.json: {e}")
            ACCOUNTS = []
    else:
        print(f"Warning: {SETTINGS_FILE} not found. Using empty accounts list.")

    # Construct Endpoints
    for acc in ACCOUNTS:
        if acc.get('blog_id'):
            acc['endpoint'] = f"http://livedoor.blogcms.jp/atom/blog/{acc['blog_id']}/article"

    # AI Model Settings
    ai_models_env = os.getenv("AI_MODELS", "")
    if ai_models_env:
        AI_MODELS = [m.strip() for m in ai_models_env.split(",") if m.strip()]
    else:
        AI_MODELS = ['gemini-3.6-flash', 'gemini-3.5-flash-lite', 'gemini-3.1-flash-lite', 'gemini-2.5-flash', 'gemini-2.5-flash-lite']
    
    if AI_MODELS:
        AI_MODEL = AI_MODELS[0]
    else:
        AI_MODEL = "gemini-3.6-flash"
    
    # 環境変数からカンマ区切りで読み込むか、Jenkinsから渡された.envを使用
    ai_keys_env = os.getenv("AI_KEYS", "")
    if ai_keys_env:
        AI_KEYS = [k.strip() for k in ai_keys_env.split(",") if k.strip()]
    else:
        print("Warning: AI_KEYS environment variable is not set!")
        AI_KEYS = []
    
    # System
    INTERVAL = 60
    
    # Data path
    DATA_DIR = Path("data")
    HISTORY_FILE = DATA_DIR / "history.json"
    
    @staticmethod
    def validate():
        if not Config.ACCOUNTS:
            print("[Warning] No accounts loaded. Bot will not process anything.")
        if not Config.AI_KEYS:
             raise ValueError("API Keys for GenAI are missing.")
