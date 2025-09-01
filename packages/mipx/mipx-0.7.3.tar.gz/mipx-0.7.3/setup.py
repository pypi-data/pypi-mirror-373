# -*- coding: utf-8 -*-
# @Time    : 2023/4/9 18:21
# @Author  : luyi
from setuptools import setup

# with open("README.md", "r", encoding="utf-8") as f:
#     long_description = f.read()
setup(
    name="mipx",
    version="0.7.3",
    author="ly",
    author_email="2662017230@qq.com",
    # description="Python (Mixed-Integer Linear Programming Constraint Programming) Optimization Tools",
    description="",
    url="",
    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    # packages=find_packages(exclude=['core', '__pycache__']),
    packages=["mipx"],
    # long_description=long_description,
    # long_description_content_type="text/markdown",  # 详细描述的内容类型
    # include_package_data=True,
    install_requires=[
        "ortools>=9.9.3963,<=9.14.6206",
    ],
    extras_require={
        "docplex": ["docplex>=2.25.0,<3.0.0"],  # 限制 docplex 的版本范围
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    zip_safe=False,
)
