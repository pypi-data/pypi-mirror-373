"""
setup.py - 这个B班值不值得上 包配置文件
"""

from setuptools import setup, find_packages
import os

# 读取requirements.txt文件获取依赖项
def get_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

# 读取README.md文件作为长描述
def get_long_description():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "一个帮助你评估工作真实价值的工具，综合考虑薪资、工时、通勤、工作环境等多个因素"

setup(
    name="b-class-worth",  # 英文包名，用于PyPI上传
    description="这个B班值不值得上 - 一个帮助你评估工作真实价值的工具，综合考虑薪资、工时、通勤、工作环境等多个因素",
    version="0.1.0",
    author="Alvin",
    author_email="alvin@example.com",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zippland/worth-calculator",
    packages=find_packages(),
    install_requires=get_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            '这个B班值不值得上=b_class_worth.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False
)