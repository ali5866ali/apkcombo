import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import webbrowser

# فایل‌های مورد نیاز
package_list_file = 'packages_list.txt'
packages_file = 'packages.json'
progress_file = 'progress.json'
output_html_file = 'updated_packages.html'

# تابع تبدیل اعداد فارسی به انگلیسی
def convert_persian_numbers_to_english(input_str):
    persian_numbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
    english_numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for p, e in zip(persian_numbers, english_numbers):
        input_str = input_str.replace(p, e)
    return input_str

# بارگذاری فایل‌های پکیج و پیشرفت
if os.path.exists(packages_file):
    with open(packages_file, 'r', encoding='utf-8') as f:
        packages = json.load(f)
else:
    packages = {}

if os.path.exists(progress_file):
    with open(progress_file, 'r', encoding='utf-8') as f:
        progress = json.load(f)
else:
    progress = {}

# خواندن نام پکیج‌ها از فایل لیست
with open(package_list_file, 'r', encoding='utf-8') as f:
    package_names = [line.strip() for line in f if line.strip()]

total_packages = len(package_names)
processed_packages = 0
changed_packages = []
packages_to_remove = []  # لیست پکیج‌هایی که باید حذف شوند

semaphore = asyncio.Semaphore(10)  # محدود کردن تعداد وظایف همزمان به 10

async def process_package(session, package_name, retries=3):
    global processed_packages
    async with semaphore:  # محدود کردن تعداد وظایف همزمان
        processed_packages += 1
        progress_percentage = (processed_packages / total_packages) * 100
        print(f"پردازش پکیج {package_name} ({processed_packages}/{total_packages}) - درصد پیشرفت: {progress_percentage:.2f}%")
        
        if progress.get(package_name) == 'checked':
            return
        
        url = f"https://apkcombo.app/1/{package_name}"
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=30) as response:  # افزایش Timeout به 30 ثانیه
                    if response.status == 404:
                        print(f"خطای 404: پکیج {package_name} وجود ندارد و از لیست حذف خواهد شد.")
                        packages_to_remove.append(package_name)
                        return
                    elif response.status != 200:
                        print(f"خطا در دریافت اطلاعات برای پکیج {package_name}: HTTP {response.status}")
                        return
                    html = await response.text()
                    break  # اگر درخواست موفق بود، از حلقه خارج شوید
            except asyncio.TimeoutError:
                if attempt < retries - 1:
                    print(f"خطای Timeout برای پکیج {package_name} - تلاش مجدد ({attempt + 1}/{retries})...")
                    await asyncio.sleep(2)  # تاخیر کوتاه قبل از تلاش مجدد
                else:
                    print(f"خطای Timeout: پکیج {package_name} پس از {retries} تلاش.")
                    return
            except Exception as e:
                print(f"خطا در دریافت اطلاعات برای پکیج {package_name}: {e}")
                return
        
        # استخراج نام اپلیکیشن
        soup = BeautifulSoup(html, 'html.parser')
        app_name_div = soup.find('div', class_='app_name')
        app_name = app_name_div.find('a').text.strip() if app_name_div else ''

        # استخراج نسخه
        version_div = soup.find('div', class_='version')
        if version_div:
            latest_version_persian = version_div.text.strip()
            latest_version = convert_persian_numbers_to_english(latest_version_persian)
            if package_name in packages:
                old_version = packages[package_name]['new-ver']
                if old_version != latest_version:
                    packages[package_name]['old-ver'] = old_version
                    packages[package_name]['new-ver'] = latest_version
                    changed_packages.append({
                        'name': package_name,
                        'app_name': app_name,
                        'old_ver': old_version,
                        'new_ver': latest_version,
                        'url': url
                    })
                else:
                    packages[package_name]['old-ver'] = old_version
                    packages[package_name]['new-ver'] = latest_version
            else:
                packages[package_name] = {
                    'old-ver': latest_version,
                    'new-ver': latest_version,
                    'app_name': app_name
                }
            progress[package_name] = 'checked'

async def main():
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [process_package(session, package_name) for package_name in package_names]
        await asyncio.gather(*tasks)
    
    # ذخیره پیشرفت و پکیج‌ها پس از پردازش
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=4)
    
    with open(packages_file, 'w', encoding='utf-8') as f:
        json.dump(packages, f, ensure_ascii=False, indent=4)
    
    # حذف پکیج‌های با خطا 404 از لیست
    if packages_to_remove:
        with open(package_list_file, 'r', encoding='utf-8') as f:
            current_packages = [line.strip() for line in f if line.strip()]
        updated_packages = [pkg for pkg in current_packages if pkg not in packages_to_remove]
        with open(package_list_file, 'w', encoding='utf-8') as f:
            for pkg in updated_packages:
                f.write(pkg + '\n')
        print(f"{len(packages_to_remove)} پکیج با خطا 404 از فایل حذف شدند.")
    
    # تولید خروجی HTML برای پکیج‌های آپدیت‌شده
    if changed_packages:
        html_output = '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سایت apkcombo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            direction: rtl;
            text-align: right;
            margin: 20px;
            background-color: #f9f9f9;
        }
        h1 {
            color: #333;
            font-size: 24px;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        table, th, td {
            border: 1px solid #ccc;
        }
        th, td {
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>پکیج‌های آپدیت‌شده</h1>
    <table>
        <tr>
            <th>نام اپلیکیشن</th>
            <th>نام پکیج</th>
            <th>نسخه قبلی</th>
            <th>نسخه جدید</th>
            <th>لینک به APKCombo</th>
        </tr>'''
        for package in changed_packages:
            html_output += f'''
            <tr>
                <td>{package['app_name']}</td>
                <td>{package['name']}</td>
                <td>{package['old_ver']}</td>
                <td>{package['new_ver']}</td>
                <td><a href="{package['url']}" target="_blank">مشاهده در APKCombo</a></td>
            </tr>'''
        html_output += '''
        </table>
    </body>
    </html>'''
if changed_packages:
    with open(output_html_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    print("فایل HTML ساخته شد.")
else:
    print("هیچ پکیج آپدیت‌شده‌ای یافت نشد.")

print("عملیات به پایان رسید.")

# اجرای تابع اصلی
if __name__ == "__main__":
    asyncio.run(main())
