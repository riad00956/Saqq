import os
import yt_dlp
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

# আপনার দেওয়া কুকি ডাটা
COOKIES_DATA = [
    {"name": "VISITOR_PRIVACY_METADATA", "value": "CgJCRBIEGgAgYA%3D%3D", "domain": ".youtube.com", "path": "/"},
    {"name": "__Secure-3PSID", "value": "g.a0007Qh-KGxeDQ4tL6lHNqcGLlQ3hbEOK4v4ObSNdzdYRLEUNKiDJRd3TtUJ5GuBUBjw7mfrzAACgYKAbYSARUSFQHGX2MiUz2e-GJOgXWX4fvpnkG7gxoVAUF8yKqOs0FAUupZU3M0GMUEf9-b0076", "domain": ".youtube.com", "path": "/"},
    {"name": "SIDCC", "value": "AKEyXzUovatPak49pqYcCoDO4Pk3bpU4AETVws_IXgsTiXUzWRuxcOexZIX_OPkm-1KBQjWb", "domain": ".youtube.com", "path": "/"},
    {"name": "YSC", "value": "gXYspOvJiO0", "domain": ".youtube.com", "path": "/"},
    {"name": "SID", "value": "g.a0007Qh-KGxeDQ4tL6lHNqcGLlQ3hbEOK4v4ObSNdzdYRLEUNKiDb-Gv4yE-rxc86YS9MWTrwAACgYKARkSARUSFQHGX2MiF-cRiZ9dYHehtsPLjcJOyxoVAUF8yKr6z8CJ1TIe6oXyVMxHScXg0076", "domain": ".youtube.com", "path": "/"},
    {"name": "LOGIN_INFO", "value": "AFmmF2swRAIgVieAEn6MN57R7yb1h-y4CtZQfgegzyU_KIT5wMh-rmkCIBKIxGhhlC4_mPXqXIyLzqkOC_IuM9psdpspluayEsKi:QUQ3MjNmeXdoa0hCSzA1WXp3X2ZCM2RaQzJKalRMcWowNGhIdXhZWnR6LWdKMkhieTJsVXI4NHd6QmpzMHIyOXFiMV9ydFJ3U1UxRGdUdUo3dVV4NmRWQzA2Q25UcGVXUklLa3FUQmZDbzA1cVFXbTFqdFdfRUYtS3liVU5QYVIxc0R5TjVnUl9sTmt5OFJLdGdIaFI5dlVXSzk1clpKSWRR", "domain": ".youtube.com", "path": "/"},
    {"name": "VISITOR_INFO1_LIVE", "value": "jQN6-EZIGbQ", "domain": ".youtube.com", "path": "/"}
]

HTML_PAGE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ইউটিউব ভিডিও ডাউনলোডার</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #121212; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e1e1e; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; width: 90%; max-width: 400px; }
        h2 { color: #ff0000; margin-bottom: 25px; }
        input[type="text"] { width: 100%; padding: 12px; border: none; border-radius: 8px; margin-bottom: 20px; box-sizing: border-box; background: #333; color: white; }
        button { background-color: #ff0000; color: white; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%; transition: 0.3s; }
        button:hover { background-color: #cc0000; }
        .footer { margin-top: 20px; font-size: 11px; color: #888; }
    </style>
</head>
<body>
    <div class="card">
        <h2>YT Downloader</h2>
        <form action="/download" method="POST">
            <input type="text" name="url" placeholder="ভিডিওর লিঙ্ক দিন..." required>
            <button type="submit">ডাউনলোড করুন</button>
        </form>
        <div class="footer">কুকি ব্যবহার করে ভিডিও প্রসেস করা হচ্ছে</div>
    </div>
</body>
</html>
"""

def create_cookie_file():
    cookie_file = "temp_cookies.txt"
    with open(cookie_file, "w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for c in COOKIES_DATA:
            domain = c.get('domain', '.youtube.com')
            path = c.get('path', '/')
            name = c.get('name', '')
            value = c.get('value', '')
            # domain, flag, path, secure, expiration, name, value
            f.write(f"{domain}\tTRUE\t{path}\tTRUE\t0\t{name}\t{value}\n")
    return cookie_file

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    cookie_file = create_cookie_file()
    
    ydl_opts = {
        'format': 'best',
        'cookiefile': cookie_file,
        'outtmpl': '/tmp/%(title)s.%(ext)s', # রেন্ডারের জন্য /tmp ফোল্ডার ব্যবহার করা নিরাপদ
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"ভুল হয়েছে: {str(e)}"
    finally:
        if os.path.exists(cookie_file):
            os.remove(cookie_file)

if __name__ == '__main__':
    # রেন্ডারের জন্য পোর্ট সেটআপ
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
