import subprocess
import os
from pathlib import Path

CURRENT_DIR = Path(__file__).parent
PACKAGE_DIR = CURRENT_DIR.parent

FFMPEG_PATH = PACKAGE_DIR / 'bin/ffmpeg.exe'


def b_merge_videos(dir_path: Path | str, output_path: Path | str):
    dir_path = Path(dir_path)
    parent_path = dir_path.parent

    if not dir_path.is_dir():
        return f"输入路径 {dir_path} 不是一个有效的文件夹。"

    # 收集所有符合条件的视频文件
    dir_path_length = len(str(dir_path))
    video_files = [str(file) for file in dir_path.iterdir() if file.is_file()]

    # 排序
    video_files.sort(key=lambda x: int(x[dir_path_length+1:].split('.')[0]))

    # 书写 list.txt
    list_txt = parent_path / 'list.txt'
    with open(list_txt, 'w', encoding="utf-8") as f:
        for file in video_files:
            f.write(f"file '{file}'\n")

    cmd = [
        str(FFMPEG_PATH),
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_txt),
        "-c", "copy",  # 直接复制流，不重新编码
        str(output_path),
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        return f"合并视频失败：{e.stderr.decode()}"

    # 删除list.txt
    os.remove(list_txt)


if __name__ == '__main__':
    b_merge_videos(r'E:\byzh_workingplace\byzh-rc-to-pypi\视频\1\Part_0', 'D:/test.mp4')