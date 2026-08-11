import json
import time
import schedule
import sys
from pathlib import Path
from .config import Config
from .rss import RSSFetcher
from .scraper import WebScraper
from .ai import AIWriter
from .livedoor import LivedoorPoster

def load_history():
    if not Config.HISTORY_FILE.exists():
        print("  -> 履歴ファイルが存在しません")
        return []
    try:
        with open(Config.HISTORY_FILE, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"  -> 履歴読み込み時にエラー発生: {e}")
        return []

def save_history(history):
    Config.DATA_DIR.mkdir(exist_ok=True)
    with open(Config.HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def job(draft=False):
    print("--- ジョブ開始 ---")
    history = load_history()
    
    fetcher = RSSFetcher()
    scraper = WebScraper()
    ai = AIWriter() 
    
    for account in Config.ACCOUNTS:
        account_name = account.get('name', 'Unknown')
        print(f"\n=== Processing Account: {account_name} ({account.get('user_id')}) ===")
        
        try:
             poster = LivedoorPoster(account)
        except Exception as e:
             print(f"[!] Init failed for {account.get('id', 'unknown')}: {e}")
             continue

        target_urls = account.get("target_urls", [])
        
        total_process_count = 0
        
        for rss_url in target_urls:
            # 1メディアごと最新10記事まで確認
            links = fetcher.fetch_urls(rss_url, limit=10)
            
            media_process_count = 0
            max_per_media = 3
            
            for link in links:
                if media_process_count >= max_per_media:
                    break

                if link in history:
                    continue

                print(f"\n[Media: {media_process_count + 1}/{max_per_media}] 記事を処理中: {link}")
                
                article_data = scraper.fetch_article(link)
                
                if article_data and article_data.get('text'):
                    if len(article_data['text']) < 100:
                        print("[!] 記事が短すぎるためスキップ。")
                        continue

                    title, body, category = ai.generate_blog_post(article_data, account_name)
                    
                    if title and body:
                        # 参照元URLをカード形式で追記
                        if article_data.get('image_url'):
                            thumb_url = article_data['image_url']
                            source_html = f'''
<div style="margin-bottom: 20px; max-width: 600px; font-family: sans-serif;">
    <a href="{link}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: #333;">
        <div style="display: flex; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); height: 110px;">
            <div style="width: 110px; flex-shrink: 0; background-image: url('{thumb_url}'); background-size: cover; background-position: center; border-right: 1px solid #e0e0e0;"></div>
            <div style="padding: 12px; display: flex; flex-direction: column; justify-content: center; overflow: hidden; width: 100%;">
                <div style="font-weight: bold; font-size: 15px; line-height: 1.4; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{article_data.get('title', '元記事を見る')}</div>
                <div style="font-size: 11px; color: #888; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{link}</div>
            </div>
        </div>
    </a>
</div>'''
                        else:
                            source_html = f'''
<div style="margin-bottom: 20px; max-width: 600px; font-family: sans-serif;">
    <a href="{link}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: #333;">
        <div style="padding: 12px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="font-weight: bold; font-size: 15px; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{article_data.get('title', '元記事を見る')}</div>
            <div style="font-size: 11px; color: #888; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{link}</div>
        </div>
    </a>
</div>'''
                        
                        body = source_html + "\n" + body
                        
                        if poster.post(title, body, category=category, draft=draft):
                            history.append(link)
                            save_history(history[-2000:])
                            
                            media_process_count += 1
                            total_process_count += 1
                            
                            # バン対策で1記事ごとに間隔をあける (60s)
                            print("    次まで待機 (60s)...")
                            time.sleep(60)

        if total_process_count == 0:
            print(f"  新しい記事はありませんでした (Account: {account_name})")
            
    print("--- ジョブ終了 ---")

def main():
    try:
        Config.validate()
        print(f"Bot起動: {len(Config.ACCOUNTS)} アカウントを監視中...")
        
        is_draft = "--draft" in sys.argv
        if is_draft:
            print("[INFO] Mode: DRAFT")

        job(draft=is_draft)
        
        if "--once" in sys.argv:
            print("ワンショット実行完了。終了します。")
            return

        schedule.every(Config.INTERVAL).minutes.do(job, draft=is_draft)
        
        print(f"スケジュール実行モード: {Config.INTERVAL}分ごとに実行します。")
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
