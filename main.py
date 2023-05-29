import os
import sys
from typing import List
import requests
import time
import re
from bs4 import BeautifulSoup

TESTING = False
ROOT_DIR = '.'

def content_dl(urls: List[str], path: str):
    im_pattern = re.compile(r"imgur\.com\/(\w+)(\..*)")
    gfy_pattern = re.compile(r"gfycat\.com\/(\w+)(?:-mobile)?(\..*)")
    for url in urls:
        if url[1]:
            m = re.search(gfy_pattern, url[0])
        else:
            m = re.search(im_pattern, url[0])

        name = m.group(1)
        ext = m.group(2)
        fname = os.path.join(path, name + ext)

        if ext == '.mp4' or ext == '.gif':
            os.system(f"yt-dlp {url[0]} -P home:'{path}'")
            print(f"[written] {fname}")
        else:
            with open(fname, 'wb') as f:
                print(f"[written] {fname}")
                f.write(url[2])

def find_image_urls(soup: BeautifulSoup) -> List[str]:
    image_elements = soup.find_all('img', attrs={'class':'alignfull'})
    urls = []
    for element in image_elements:
        url = element['src'].strip()
        content = requests.get(url).content
        print(f"[downloader] {url}")
        urls.append((element['src'].strip(), False, content))
    return urls

def find_video_urls(soup: BeautifulSoup) -> List[str]:
    video_elements = soup.find_all('video')
    urls = []
    for element in video_elements:
        if element.has_attr('poster') and 'imgur' in element['poster']:
            url = element['poster']
            url = url[:url.rfind('.')] + '.mp4'
            gfy = False
        else:
            if element.find('source') != None:
                url = element.find('source')['src']
                if url.endswith('jpg'):
                    url = url[:url.rfind('.')] + '.mp4'
            else:
                url = element['poster']
            gfy = True
        if url.endswith('jpg'):
            url = url[:url.rfind('.')] + '.mp4'
        # content = requests.get(url).content
        content = None
        print(f"[downloader] {url}")
        time.sleep(0.25)
        urls.append((url, gfy, content))
    return urls

def find_title(soup: BeautifulSoup) -> str:
    return soup.find('title').text.strip()

def dl(soup: BeautifulSoup):
    title = find_title(soup)

    path = os.path.join(ROOT_DIR, title)
    if not os.path.isdir(path):
        os.mkdir(path)

    if TESTING:
        with open(os.path.join(path, title + '.html'), 'w') as f:
            f.write(soup.prettify())

    image_urls = find_image_urls(soup)
    video_urls = find_video_urls(soup)
    content_dl([*image_urls, *video_urls], path)

def main():
    if TESTING:
        url = "[REDACTED]"
    else:
        if len(sys.argv) == 3:
            global ROOT_DIR 
            ROOT_DIR = sys.argv[1]
            url = sys.argv[2]
        else:
            url = sys.argv[1]

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    dl(soup)

if __name__ == "__main__":
    main()
