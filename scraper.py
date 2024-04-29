import os
import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

pinterest_sess = os.getenv('PINTEREST_SESS')

async def get_pins_html(query: str = "anime"):
    cookies = {
        '_pinterest_sess': pinterest_sess
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://ru.pinterest.com/search/pins/?q={query}&rs=typed', cookies=cookies) as response:
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