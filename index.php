<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <title>GitHub Proxy - JS</title>
    <style>
        body { font-family: Tahoma; max-width: 900px; margin: 20px auto; padding: 10px; }
        input[type="text"] { width: 75%; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        iframe { width: 100%; height: 600px; border: 1px solid #ccc; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>🌐 مرورگر وب از طریق گیت‌هاب</h2>
    <form onsubmit="loadSite(event)">
        <input type="text" id="url" placeholder="https://example.com" value="https://www.wikipedia.org" required>
        <button type="submit">باز کردن</button>
    </form>
    
    <iframe id="frame" sandbox="allow-same-origin allow-scripts allow-popups allow-forms" loading="lazy"></iframe>

    <script>
        function loadSite(event) {
            event.preventDefault();
            let rawUrl = document.getElementById('url').value.trim();
            
            // اضافه کردن https:// اگر کاربر فراموش کرده باشد
            if (!rawUrl.startsWith('http://') && !rawUrl.startsWith('https://')) {
                rawUrl = 'https://' + rawUrl;
            }

            // استفاده از CORS Proxy عمومی برای رد شدن از فیلتر
            // این سرویس‌های رایگان CORS Anywhere هستند (یکی را امتحان کنید)
            const proxy = 'https://api.allorigins.win/raw?url=';
            
            document.getElementById('frame').src = proxy + encodeURIComponent(rawUrl);
        }
    </script>
</body>
</html>
