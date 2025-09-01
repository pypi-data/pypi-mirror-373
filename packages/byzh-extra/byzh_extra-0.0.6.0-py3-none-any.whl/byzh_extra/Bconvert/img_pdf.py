from pdf2image import convert_from_path
from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fpdf import FPDF


def b_img2pdf(img_path, pdf_path):

    # 打开图片
    image = Image.open(img_path)

    # 转换为 RGB 模式（有些图片是 PNG 的 RGBA 格式）
    image = image.convert("RGB")

    # 保存为 PDF
    image.save(pdf_path)


def b_imgs2pdf(
    image_folder,
    output_pdf="output.pdf",
    sorted_key=lambda x: int(Path(x).stem),
):
    """
    :param image_folder:
    :param output_pdf:
    :param sorted_key:
    :return:

    >>> b_img2pdf(r'./文件夹1')

    """
    # 获取所有图片并排序
    images = [
        file for file in os.listdir(image_folder)
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
    ]
    images = sorted(images, key=sorted_key)
    images = [os.path.join(image_folder, file) for file in images]


    if not images:
        print("没有找到图片文件！")
        return

    # 创建PDF对象
    pdf = FPDF()

    for image_file in images:
        # 打开图片文件
        img = Image.open(image_file)

        # 获取图片尺寸（转换为毫米）
        width, height = img.size
        width_mm = width * 0.264583
        height_mm = height * 0.264583

        # 添加PDF页面（使用图片原始尺寸）
        pdf.add_page(format=(width_mm, height_mm))

        # 将图片添加到PDF中
        pdf.image(image_file, 0, 0, width_mm, height_mm)

    # 保存PDF文件
    pdf.output(output_pdf)
    print(f"PDF已保存到: {output_pdf}")


def b_pdf2img(pdf_path, output_dir, format='png', dpi=200, cpu_use:int = None):
    '''
    :param pdf_path:
    :param output_dir:
    :param format: png, jpg, ...
    :param dpi: 越高越清晰, 125够用
    :param cpu_use: 采用核心数(不指定则采用总核心的四分之一)
    :return:
    '''
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    pdf_name = pdf_path.stem
    if not pdf_path.is_file():
        print(f"路径 {pdf_path} 无法访问")
    os.makedirs(output_dir, exist_ok=True)

    cpu_count = os.cpu_count()
    if cpu_use is None:
        cpu_use = int(cpu_count / 4)
    print(f"[PDF to IMG] 当前CPU核心数{cpu_count}, 采用{cpu_use}个核心")
    print("[PDF to IMG] 正在处理数据中: ")
    images = convert_from_path(pdf_path, dpi=dpi, thread_count=cpu_use)

    def save_image(index, image):
        image.save(output_dir / f"{pdf_name}_{index + 1}.{format}", format.upper())

    with ThreadPoolExecutor() as executor:
        executor.map(save_image, range(len(images)), images)

    print(f"[PDF to IMG] {len(images)} 张 {format.upper()} 图片已保存至路径 {output_dir}")