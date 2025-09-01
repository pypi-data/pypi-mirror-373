from setuptools import setup, find_packages
import byzh_extra

setup(
    name='byzh_extra',
    version=byzh_extra.__version__,
    author="byzh_rc",
    description="基于byzh_core的扩展包",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'byzh_core==0.0.5.0', # !!!!!
        'python-pptx',
        'pdf2image',
        'chardet',
        'fpdf2'
    ],
    package_data={
        'byzh_extra': ['bin/*']
    },
    entry_points={
        "console_scripts": [
            "b_py2ipynb=byzh_extra.__main__:b_py2ipynb", # b_py2ipynb 路径
            "b_ipynb2py=byzh_extra.__main__:b_ipynb2py", # b_ipynb2py 路径
            "b_str_finder=byzh_extra.__main__:b_str_finder", # b_find_str -p path -s string
        ]
    },
)
