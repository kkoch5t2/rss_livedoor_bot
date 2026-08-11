import requests
import hashlib
import base64
import datetime
import secrets
import email.utils
from .config import Config

class LivedoorPoster:
    def __init__(self, account_config):
        self.account = account_config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Python/RSSLivedoorBot 1.0',
        })

    def _get_server_time_offset(self):
        try:
            resp = self.session.head(self.account['endpoint'], timeout=5)
            if 'Date' in resp.headers:
                server_time = email.utils.parsedate_to_datetime(resp.headers['Date'])
                local_time = datetime.datetime.now(datetime.timezone.utc)
                return server_time - local_time
        except Exception as e:
            pass
        return datetime.timedelta(0)

    def _get_wsse_header(self):
        offset = self._get_server_time_offset()
        nonce = secrets.token_bytes(16)
        now = datetime.datetime.now(datetime.timezone.utc) + offset
        created = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        password = self.account['api_key'].encode('utf-8')
        created_bytes = created.encode('utf-8')
        
        sha1 = hashlib.sha1()
        sha1.update(nonce)
        sha1.update(created_bytes)
        sha1.update(password)
        digest = sha1.digest()
        
        digest_b64 = base64.b64encode(digest).decode('utf-8')
        nonce_b64 = base64.b64encode(nonce).decode('utf-8')

        return {
            'X-WSSE': f'UsernameToken Username="{self.account["user_id"]}", PasswordDigest="{digest_b64}", Nonce="{nonce_b64}", Created="{created}"'
        }

    def post(self, title, body, category=None, draft=False):
        status_msg = "下書き" if draft else "公開"
        print(f"[*] Livedoorへ投稿開始({status_msg}): {title}")
        
        category_xml = f'<category term="{category}" />\n' if category else ""
        draft_xml = "<app:control><app:draft>yes</app:draft></app:control>" if draft else ""
        
        xml = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://purl.org/atom/ns#" xmlns:app="http://www.w3.org/2007/app">
    <title>{title}</title>
    <content type="html">
        <![CDATA[{body}]]>
    </content>
    {category_xml}
    {draft_xml}
</entry>'''

        headers = self._get_wsse_header()
        headers['Content-Type'] = 'application/x.atom+xml'

        try:
            resp = self.session.post(self.account['endpoint'], data=xml.encode('utf-8'), headers=headers)
            
            if resp.status_code == 201:
                print(f"[+] 投稿成功！ ({status_msg})")
                return True
            else:
                print(f"[!] 投稿失敗: {resp.status_code}")
                return False
        except Exception as e:
            print(f"[!] 通信エラー: {e}")
            return False
