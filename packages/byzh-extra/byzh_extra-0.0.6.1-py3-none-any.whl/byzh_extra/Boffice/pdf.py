from PyPDF2 import PdfReader, PdfWriter
from byzh_core import B_os


def b_sort_pdf(file_path, out_path, order: list[int]):
    '''
    :param file_path:
    :param out_path:
    :param order: [1,5,4,3,2]
    :return:
    '''
    # 加载原始 PDF 文件
    reader = PdfReader(file_path)
    writer = PdfWriter()

    order = [i - 1 for i in order]

    # 添加页面到新 PDF 中
    for i in order:
        writer.add_page(reader.pages[i])

    # 保存到新文件
    B_os.makedirs(out_path)
    with open(out_path, "wb") as f:
        writer.write(f)

def b_sort_pdf1(file_path, out_path, order: list[int | tuple[int, int]], remain_unmentioned=False):
    '''
    :param file_path:
    :param out_path:
    :param order: [(1), (98, 118), (2, 97), (119, 168)] 或 [(1), (98, 118)]
    :param remain_unmentioned: 是否保留未提及的页面
    :return:
    '''
    reader = PdfReader(file_path)
    remain_order = [i+1 for i in range(len(reader.pages))]

    new_order = []
    for tu in order:
        if len(tu) == 1:
            num = tu[0]
            new_order.append(num)
            remain_order[num-1] = -1
        else:
            for num in range(tu[0], tu[1]+1):
                new_order.append(num)
                remain_order[num-1] = -1

    remain_order = [x for x in remain_order if x != -1]
    if remain_unmentioned:
        new_order.extend(remain_order)

    b_sort_pdf(file_path, out_path, new_order)

def b_combine_pdf(file_path1, file_path2, out_path, order: list[list[int, int|tuple[int, int]]], remain_unmentioned=False):
    '''
    b_combine_pdf('input1.pdf', 'input2.pdf', out_path='output.pdf', order=[[2, (1, 4)], [1, 1], [2, (6, 103)]])
    :param file_path1: 1
    :param file_path2: 2
    :param out_path:
    :param order: [[1, (start, end)], ..., [2, (start, end)]]
    :return:
    '''
    reader1 = PdfReader(file_path1)
    remain_order1 = [i+1 for i in range(len(reader1.pages))]
    reader2 = PdfReader(file_path2)
    remain_order2 = [i+1 for i in range(len(reader2.pages))]

    new_order = []
    for index, tu in order:
        if isinstance(tu, int):
            new_order.append((index, tu))
        else:
            for num in range(tu[0], tu[1]+1):
                new_order.append((index, num))

    if remain_unmentioned:
        remain_order1 = [(1, x) for x in remain_order1 if x != -1]
        remain_order2 = [(2, x) for x in remain_order2 if x != -1]
        new_order.extend(remain_order1)
        new_order.extend(remain_order2)

    writer = PdfWriter()
    for element in new_order:
        if element[0] == 1:
            writer.add_page(reader1.pages[element[1]-1])
        if element[0] == 2:
            writer.add_page(reader2.pages[element[1]-1])

    # 保存到新文件
    B_os.makedirs(out_path)
    with open(out_path, "wb") as f:
        writer.write(f)


def b_combine_pdf1(file_path1, file_path2, out_path, order: list[list[int, int]], remain_unmentioned=False):
    '''
    从第1张开始，后续默认从上一次结尾的下一张开始
    b_combine_pdf1('input1.pdf', 'input2.pdf', out_path='output.pdf', order=[[2, 4], [1, 1], [2, 16]])
    :param file_path1: 1
    :param file_path2: 2
    :param out_path:
    :param order: [[1, (start, end)], ..., [2, (start, end)]]
    :return:
    '''
    a_start = 1
    b_start = 1
    new_order = []
    for index, num in order:
        if index == 1:
            new_order.append([index, (a_start, num)])
            a_start = num + 1
        elif index == 2:
            new_order.append([index, (b_start, num)])
            b_start = num + 1

    b_combine_pdf(file_path1, file_path2, out_path, new_order, remain_unmentioned)
