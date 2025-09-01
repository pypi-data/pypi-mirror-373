from pathlib import Path
from ..Bffmpeg import b_convert_video1

def b_ts2mp4(input_path: Path | str, output_path: Path | str = None):
    '''
    
    :param input_path: 
    :param output_path: 
    :return:
    
    :examples:
    >>> b_ts2mp4('./awaaa/21.ts') 
    '''
    if output_path is None:
        output_path = str(input_path).replace('.ts', '.mp4')
        output_path = Path(output_path)
    if not str(input_path).endswith('.ts'):
        raise ValueError("输入文件必须是 .ts 格式")

    b_convert_video1(input_path, output_path)