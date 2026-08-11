import feedparser

class RSSFetcher:
    def __init__(self):
        pass

    def fetch_urls(self, rss_url, limit=5):
        print(f"[*] RSS取得中: {rss_url}")
        links = []
        try:
            feed = feedparser.parse(rss_url)
            
            if getattr(feed, 'bozo', 0):
                print(f"[!] Warning: RSS parsing issue: {feed.bozo_exception}")

            for entry in feed.entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                
                # PRフィルタ
                if "PR:" in title or "プロモーション" in title or "AD:" in title:
                    continue
                    
                if link and link not in links:
                    links.append(link)
                    if len(links) >= limit:
                        break
                        
            return links
        except Exception as e:
            print(f"[!] RSS取得エラー: {e}")
            return []
