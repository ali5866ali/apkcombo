<?php
// پروکسی ساده برای گیت هاب پیجز
$url = $_GET['url'];
if ($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $data = curl_exec($ch);
    $contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
    curl_close($ch);
    header("Content-Type: " . $contentType);
    echo $data;
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><title>GitHub Proxy</title></head>
<body>
<form method="get">
    <input type="text" name="url" placeholder="https://apkcombo.com/downloader/" style="width:80%">
    <input type="submit" value="Go">
</form>
</body>
</html>
