import os
from byzh_core import B_os


def get_file_size(file_path):
    return os.path.getsize(file_path)
def get_dir_size(dir_path):
    size = 0
    result = b_largefile_in_dir(dir_path, want=None, console_log=False, exclude_dir=[])
    for file_path, file_size, file_size_str in result:
        size += file_size
    return size

def process_size(size):
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size/1024:.2f}KB"
    else:
        return f"{size/1024/1024:.2f}MB"

def b_largefile_in_dir(dir_path, want:None|int=5, console_log=True, exclude_dir=['.git']):
    '''
    不管文件夹大小
    :param dir_path:
    :param want: 要返回多少个大文件, 默认5个, None表示全部
    :return:
    '''



    file_paths = B_os.get_filepaths_in_dir(dir_path, exclude_dir=exclude_dir)
    results = []
    for file_path in file_paths:
        file_size = get_file_size(file_path) # B
        file_size_str = process_size(file_size)
        results.append((file_path, file_size, file_size_str))

    # 按文件大小排序
    results.sort(key=lambda x:x[1], reverse=True)

    if want is None:
        want = len(results)
    result = results[:want]

    if console_log:
        for file_path, file_size, file_size_str in result:
            print(f"{file_size_str}: {file_path}")

    return result

def b_largedir_in_dir(dir_path, want:None|int=5, console_log=True):
    '''
    只管文件夹大小
    :param dir_path:
    :param want:
    :param console_log:
    :return:
    '''
    results = []
    for root, dirs, files in os.walk(dir_path):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            dir_size = get_dir_size(dir_path)
            dir_size_str = process_size(dir_size)
            results.append((dir_path, dir_size, dir_size_str))

    # 按文件夹大小排序
    results.sort(key=lambda x:x[1], reverse=True)

    if want is None:
        want = len(results)
    result = results[:want]

    if console_log:
        for dir_path, dir_size, dir_size_str in result:
            print(f"{dir_size_str}: {dir_path}")

if __name__ == '__main__':
    b_largefile_in_dir(r'E:\byzh_workingplace\byzh-rc-to-pypi', console_log=True)
    b_largedir_in_dir(r'E:\byzh_workingplace\byzh-rc-to-pypi', want=10, console_log=True)