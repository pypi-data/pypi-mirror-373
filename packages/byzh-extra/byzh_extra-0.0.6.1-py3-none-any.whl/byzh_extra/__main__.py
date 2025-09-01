import argparse
from pathlib import Path

def b_py2ipynb():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="py文件")
    args = parser.parse_args()

    path = Path(args.path)
    if path.suffix != '.py':
        print("Error: 请输入.py文件路径")
        return

    from .Bconvert import b_py2ipynb
    b_py2ipynb(args.path)

def b_ipynb2py():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="ipynb文件")
    args = parser.parse_args()

    path = Path(args.path)
    if path.suffix != '.ipynb':
        print("Error: 请输入.ipynb文件路径")
        return

    from .Bconvert import b_ipynb2py
    b_ipynb2py(args.path)

def b_str_finder():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", '-p')
    parser.add_argument("--string", '-s')
    args = parser.parse_args()

    from .Bfinder import b_str_finder
    b_str_finder(args.path, args.string)