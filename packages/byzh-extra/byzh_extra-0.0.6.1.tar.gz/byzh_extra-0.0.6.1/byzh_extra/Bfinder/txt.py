import os
from pathlib import Path
import chardet


def get_encoding(file_path):

    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    return encoding

def b_str_in_file(file_path, string, console_log=True):
    encoding = get_encoding(file_path)

    indexes = []
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            for index, line in enumerate(f):
                if string in line:
                    indexes.append(index + 1)
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding="utf-8") as f:
            for index, line in enumerate(f):
                if string in line:
                    indexes.append(index + 1)
    except Exception as e:
        print(f"Error: {e},\n\tencoding: {encoding},\n\tFilePath: {file_path}")


    if console_log:
        print(file_path, ' <-> ', indexes)

    if len(indexes) == 0:
        return False
    else:
        return indexes

INCLUDE_EXT = [
    '.py', '.html', '.css', '.js',
    '.md', '.txt',
    '.json', '.yaml', '.yml', '.ini',
]
def b_str_in_dir(dir_path, string, console_log=True, include_ext:list[str]=INCLUDE_EXT.copy()):
    '''
    找到文件夹内的指定后缀的文件中是否包含指定字符串，并返回包含该字符串的行号
    :param dir_path:
    :param string:
    :param include_ext:
    :param encoding:
    :return: list[[行号, 文件路径], ...]
    '''
    file_paths = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if Path(file).suffix not in include_ext:
                continue
            file_path = os.path.join(root, file)
            indexes = b_str_in_file(file_path, string, False)
            if indexes:
                file_paths.append([indexes, file_path])

    if console_log:
        for indexes, file_path in file_paths:
            print(file_path, ' <-> ', indexes)

    return file_paths

def b_str_finder(path, string, console_log=True):

    path = Path(path)
    if path.is_file():
        return b_str_in_file(path, string, console_log)
    elif path.is_dir():
        return b_str_in_dir(path, string, console_log)


if __name__ == '__main__':
    # lst = b_str_in_dir(r'E:\byzh_workingplace\byzh-rc-to-pypi\uploadToPypi_extra', 'Bos')
    # for i in lst:
    #     print(i)
    path = r'E:\byzh_study\byzh_code_note'
    b_str_finder(path, 'Trait')