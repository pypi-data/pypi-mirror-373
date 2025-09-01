import requests
import os
import shutil
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from byzh_core.Btqdm import B_Tqdm

from ..Bffmpeg import b_merge_videos, b_convert_video1


def download_m3u8_file(m3u8_url, save_path='./playlist.m3u8', timeout=60):
    if os.path.exists(save_path):
        print(f"⚠️ 文件已存在，跳过下载：{save_path}")
        return
    try:
        response = requests.get(m3u8_url, timeout=timeout)
        response.raise_for_status()  # 抛出 HTTP 错误（如 404）

        # 保存内容到本地
        with open(save_path, 'w', encoding='utf-8', newline='') as f:
            f.write(response.text)

        print(f"✅ 下载成功，文件已保存到: {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败：{e}")

def transform_m3u8_txt(m3u8_url, m3u8_m3u8_path, m3u8_txt_path='./playlist.txt'):
    # playlist.m3u8: 13个字符
    ts_url_prefix = m3u8_url[:-13]

    ts_list = []
    time_list = []

    # 保存内容到本地
    with open(m3u8_m3u8_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line[0] != '#':
                ts_list.append(line.strip())
            elif 'EXTINF' in line:
                num = line.strip().split(':')[1][:-1]
                time_list.append(int(num))
    seconds = sum(time_list)

    print(f"片段数量：{len(ts_list)}")
    print(f"总时长：{seconds // 60 // 60}时{seconds // 60 % 60}分{seconds % 60}秒")

    with open(m3u8_txt_path, 'w', encoding='utf-8') as f:
        for i, ts in enumerate(ts_list):
            f.write(f'{ts_url_prefix + ts}')
            if i!= len(ts_list) - 1:
                f.write('\n')

    print(f"✅ 转换成功，文件已保存到: {m3u8_txt_path}")
    return len(ts_list)

def download_ts(my_tqdm, ts_url, save_path='./video_segment.ts', timeout=60):
    if os.path.exists(save_path):
        return
    try:
        response = requests.get(ts_url, stream=True, timeout=timeout)
        response.raise_for_status()

        with open(save_path, 'wb') as f: # wb用于写入视频流数据
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 跳过空块
                    f.write(chunk)
        my_tqdm.update(1)

    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败：{e}")

def download_ts_txt(my_tqdm, ts_txt_path, save_dir='./ts_segments', max_workers=16, timeout=60):
    with open(ts_txt_path, 'r', encoding='utf-8') as f:
        ts_list = f.readlines()

    os.makedirs(save_dir, exist_ok=True)

    def _download_task(i, ts_url):
        ts_url = ts_url.strip()
        save_path = os.path.join(save_dir, f"{i}.ts")
        download_ts(my_tqdm, ts_url, save_path, timeout=timeout)

    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, ts_url in enumerate(ts_list):
            tasks.append(executor.submit(_download_task, i, ts_url))
        for future in as_completed(tasks):
            future.result()  # 抛出异常时会在此处触发


def b_download_m3u8(url, save_path, save_segments=True, max_workers=16, timeout=60):
    '''
    下载m3u8文件，然后合并为一个视频文件
    :param url: m3u8;链接
    :param save_path: 视频保存路径
    :param save_segments: 下载后是否保留ts文件
    :param max_workers: 线程数
    :param timeout: 最大请求时间
    :return:
    '''
    save_path = Path(save_path)
    file_name = save_path.name.split('.')[0]
    save_dir = save_path.parent / file_name

    os.makedirs(save_dir, exist_ok=True)

    # 下载playlist.m3u8
    m3u8_path1 = save_dir / 'playlist.m3u8'
    download_m3u8_file(url, m3u8_path1, timeout)
    # 转换为playlist.txt
    m3u8_path2 = save_dir / 'playlist.txt'
    length = transform_m3u8_txt(url, m3u8_path1, m3u8_path2)

    time.sleep(1)
    my_tqdm = B_Tqdm(range=length)

    # 下载ts文件
    segment_dir = save_dir / 'ts_segments'
    download_ts_txt(my_tqdm, m3u8_path2, segment_dir, max_workers, timeout)
    # 合并ts文件
    b_merge_videos(segment_dir, save_dir / 'video.ts')
    # 转换为指定格式
    b_convert_video1(save_dir / 'video.ts', save_path)

    time.sleep(1)
    if not save_segments:
        os.remove(m3u8_path1)
        os.remove(m3u8_path2)
        os.remove(save_dir / 'video.ts')
        shutil.rmtree(segment_dir)

    print(f"✅ 下载完成，视频已保存到: {save_path}")