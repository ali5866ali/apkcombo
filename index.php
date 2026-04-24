<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Browser</title>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; }
        iframe { width: 100vw; height: 100vh; border: none; position: fixed; top: 0; left: 0; }
    </style>
</head>
<body>
    <iframe id="frame" src="about:blank"></iframe>
    <script>
        // لیست پروکسی‌های عمومی
        const proxies = [
            'https://api.allorigins.win/raw?url=',
            'https://api.codetabs.com/v1/proxy?quest=',
            'https://corsproxy.io/?',
            'https://proxy.cors.sh/'
        ];
        
        let currentProxy = 0;
        
        function load() {
            let url = prompt('آدرس سایت را وارد کنید (با https://):', 'https://wikipedia.org');
            if (url) {
                if (!url.startsWith('http')) url = 'https://' + url;
                document.getElementById('frame').src = proxies[currentProxy] + url;
            }
        }
        
        function switchProxy() {
            currentProxy = (currentProxy + 1) % proxies.length;
            alert('پروکسی عوض شد');
        }
        
        load();
    </script>
</body>
</html>
