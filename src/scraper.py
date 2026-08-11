import requests
from newspaper import Article
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_article(self, url):
        print(f"[*] 記事データ取得: {url}")
        try:
            article = Article(url, language='ja')
            article.download()
            article.parse()
            
            title = article.title
            text = article.text
            image_url = article.top_image

            # Fallback to BeautifulSoup if newspaper3k fails
            if not text:
                res = requests.get(url, headers=self.headers, timeout=10)
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.content, "lxml")
                
                if not title:
                    title = soup.title.string if soup.title else "タイトル不明"
                
                paragraphs = soup.find_all("p")
                text = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                
                if not image_url:
                    og_img = soup.find("meta", property="og:image")
                    if og_img:
                        image_url = og_img.get("content")

            return {
                "title": title,
                "text": text,
                "image_url": image_url,
                "url": url
            }

        except Exception as e:
            print(f"[!] 記事スクレイピングエラー: {e}")
            return None
