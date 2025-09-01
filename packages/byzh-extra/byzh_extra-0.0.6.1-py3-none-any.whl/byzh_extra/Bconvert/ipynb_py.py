import json
from pathlib import Path

def b_ipynb2py(ipynb_path, py_path=None):
    '''

    :param ipynb_path:
    :param py_path:
    :return: None

    :examples:
    >>> b_ipynb2py('./test.ipynb')
    '''
    if py_path is None:
        py_path = Path(ipynb_path).parent / (Path(ipynb_path).stem + '.py')

    # 存在则询问是否覆盖
    if py_path.exists():
        ans = input(f"{py_path} 已存在. 是否覆盖? (y/n): ").strip().lower()
        if ans != 'y':
            print("Operation cancelled.")
            return

    with open(ipynb_path, mode='r', encoding='utf-8') as f:
        data = json.load(f)

    with open(py_path, mode='w', encoding='utf-8') as f:

        for i, x in enumerate(data['cells']):
            source = x['source']
            if source == '':
                continue

            prefix = ''
            if source[0].strip() == '# test':
                prefix = '# '

            # 前缀
            f.write('#' * 24 + f'# cell {i + 1} ' + '#' * 25)
            f.write('\n\n')

            # 正文
            for sentence in source:
                f.write(prefix + sentence)

            # 后缀
            f.write('\n\n')

def b_py2ipynb(py_path, ipynb_path=None):
    '''
    如果遇到含`# cell`的注释，则分为一个块

    :param py_path:
    :param ipynb_path:
    :return: None

    :example:
    >>> b_py2ipynb('./example.py')
    '''
    if ipynb_path is None:
        ipynb_path = Path(py_path).parent / (Path(py_path).stem + '.ipynb')

    # 存在则询问是否覆盖
    if ipynb_path.exists():
        ans = input(f"{ipynb_path} 已存在. 是否覆盖? (y/n): ").strip().lower()
        if ans != 'y':
            print("Operation cancelled.")
            return

    with open(py_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cells = []
    current_cell = []
    start = True

    for line in lines:
        if ('# cell' in line) or ('#cell' in line):
            # 如果当前 cell 有内容，则保存为代码单元
            if current_cell:
                cells.append({
                    "cell_type": "code",
                    "metadata": {},
                    "outputs": [],
                    "execution_count": None,
                    "source": current_cell # 关键
                })
                current_cell = []
                start = True
            continue  # 注释行为 cell 分割标志，不写入 cell 中

        if start:
            if line.strip() == '':
                continue
            else:
                start = False
        current_cell.append(line)

    # 添加最后一个 cell（如果存在）
    if current_cell:
        cells.append({
            "cell_type": "code",
            "metadata": {},
            "outputs": [],
            "execution_count": None,
            "source": current_cell
        })

    notebook = {
        "cells": cells,
        "metadata": { # 元数据
            "kernelspec": { # 内核规范
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": { # 关于编程语言的信息
                "name": "python",
                "version": "3.x"
            }
        },
        "nbformat": 4, # 格式版本号（版本 4 是当前的稳定版本）
        "nbformat_minor": 5
    }

    with open(ipynb_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=4)



if __name__ == '__main__':
    b_ipynb2py(r'E:\byzh_workingplace\byzh-rc-to-pypi\train.ipynb')
    # b_py2ipynb(r'E:\byzh_workingplace\byzh-rc-to-pypi\train.py')