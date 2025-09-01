from bs4 import BeautifulSoup
import re
import requests
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from byzh_core.Btqdm import B_Tqdm

from ..Bconvert import b_imgs2ppt, b_imgs2pdf
from byzh_core import B_os

def download_part(my_tqdm, url, save_path='./awa.ts', timeout=60):
    if os.path.exists(save_path):
        return
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        with open(save_path, 'wb') as f: # wb用于写入二进制数据
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 跳过空块
                    f.write(chunk)
        my_tqdm.update(1)

    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败：{e}")

def download_urls(url_lst, save_dir, ext, max_workers=16, timeout=60):
    os.makedirs(save_dir, exist_ok=True)

    my_tqdm = B_Tqdm(range=len(url_lst))
    def _download_task(i, url):
        url = url.strip()
        save_path = os.path.join(save_dir, f"{i}.{ext}")
        download_part(my_tqdm, url, save_path, timeout=timeout)

    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, url in enumerate(url_lst):
            tasks.append(executor.submit(_download_task, i, url))
        for future in as_completed(tasks):
            future.result()  # 抛出异常时会在此处触发




#获取网页信息
def getHTMLText(url):
    # 模拟了一个iPhone用户通过微信浏览器访问网页的行为
    headers = {
        # "User-Agent" 告诉服务器请求的来源，这里模拟的是iPhone上的微信浏览器
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.28(0x18001c2d) NetType/WIFI Language/zh_CN",
        # "Referer" 表示请求的来源页面，这里设置为微信公众号的主页。
        "Referer": "https://mp.weixin.qq.com/",
        # "Accept" 表示客户端能够接收的内容类型，这里包括HTML、XML和图片等。
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    r = requests.get(url, timeout=30, headers=headers)

    r.raise_for_status() # 检查HTTP请求是否成功完成
    r.encoding = r.apparent_encoding

    return r.text


#解析网页，获取所有图片url
def getimgURL(html):
    soup = BeautifulSoup(html, "html.parser")
    img_lst = []
    for i in soup.find_all("img"):
        img = re.findall(r'src\s*=\s*["\'](.*?)["\']', str(i))
        if len(img) == 0 or (len(img)==1 and img[0]==''):
            continue
        img_lst.extend(img)

    return img_lst

def getrooturl(url):
    # 包含前缀https://
    if url.startswith("https"):
        return "https://" + url.split("/")[2]
    elif url.startswith("http"):
        return "http://" + url.split("/")[2]
    else:
        return "http://" + url.split("/")[0]

def b_url2imgs(url, save_dir, logout=False):
    html = getHTMLText(url)

    img_lst = getimgURL(html)
    # 加工url
    for i in range(len(img_lst)):
        if img_lst[i].startswith("//"):
            img_lst[i] = "http:" + img_lst[i]
        if img_lst[i].startswith("/"):
            # url的根目录作为前缀
            img_lst[i] = getrooturl(url) + img_lst[i]


    print("[url2imgs] 共有" + f" {len(img_lst)} " + "张图片")
    if logout:
        print("[url2imgs] 图片链接如下：")
        for i in img_lst:
            print("\t", i)

    download_urls(img_lst, save_dir, ext='png')

def b_url2ppt(url, save_path):
    save_dir = Path(save_path).parent
    os.makedirs(save_dir, exist_ok=True)

    b_url2imgs(url, save_dir/'src')
    b_imgs2ppt(save_dir/'src', save_path)

    B_os.rm(save_dir/'src')

def b_url2pdf(url, save_path):
    save_dir = Path(save_path).parent
    os.makedirs(save_dir, exist_ok=True)

    b_url2imgs(url, save_dir / 'src')
    b_imgs2pdf(save_dir /'src', save_path)

    B_os.rm(save_dir /'src')


if __name__ == '__main__':
    url = 'https://mp.weixin.qq.com/s/HaccH2xg2aya5ZqAWlML0Q'
    b_url2imgs(url, 'D://公众号爬取/', logout=False)