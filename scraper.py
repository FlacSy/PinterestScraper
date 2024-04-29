import os
import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

async def get_pins_html(query: str = "anime"):
    cookies = {
        # Твои куки (проще всего их получить через розширение в браузере или используя https://curlconverter.com/python/)
    }

    headers = {
        'authority': 'ru.pinterest.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'referer': 'https://ru.pinterest.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-full-version-list': '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.130", "Google Chrome";v="120.0.6099.130"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"7.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'service-worker-navigation-preload': 'true',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }


    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://ru.pinterest.com/search/pins/?q={query}&rs=typed', cookies=cookies, headers=headers) as response:
            html = await response.text()
            status_code = response.status
            return html, status_code

    
async def get_pin_links(html, status_code):
    if status_code != 200:
        print(f"Error: {status_code}")
        return None
        
    soup = BeautifulSoup(html, 'html.parser')
    pin_links = soup.find_all('a', class_='Wk9 xQ4 CCY S9z DUt iyn kVc agv LIa')

    urls = []

    for link in pin_links:   
        urls.append(f"https://ru.pinterest.com{link['href']}")
    return urls

async def download_pintrest_content(links: list, save_path: str = 'tests'):
    downloaded_files = []

    async with aiohttp.ClientSession() as session:
        for link in links:
            async with session.get(link) as response:
                html = await response.text()
                status_code = response.status

            if status_code == 200:
                soup = BeautifulSoup(html, 'html.parser')
                img_tags = soup.find_all('img')

                for img_tag in img_tags:
                    content_url = img_tag.get('src')
                    if content_url:
                        filename = content_url.split('/')[-1]
                        file_path = os.path.join(save_path, filename)

                        async with session.get(content_url) as content_response:
                            content = await content_response.read()

                        image = Image.open(BytesIO(content))
                        width, height = image.size
                        if width > 240 or height > 240:
                            async with aiofiles.open(file_path, mode='wb') as f:
                                await f.write(content)

                            downloaded_files.append(file_path)

    return downloaded_files

async def main():
    query = input("Enter search query: ")
    html, status_code = await get_pins_html(query)
    links = await get_pin_links(html, status_code)
    downloaded_files = await download_pintrest_content(links)
    for file in downloaded_files:
        print(f"Downloaded: {file}")

asyncio.run(main())