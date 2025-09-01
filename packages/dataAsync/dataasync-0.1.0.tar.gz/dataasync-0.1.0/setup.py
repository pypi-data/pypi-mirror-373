from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dataAsync",  # 包名称，pip install时将使用这个名字
    version="0.1.0",  # 版本号
    author="qiaokuoyuan",
    author_email="457361577@qq.com",
    description="async data to sqlalchemy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/your-package",
    packages=find_packages(),  # 自动发现所有包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python版本要求
    install_requires=[  # 依赖包
        "cx_Oracle>=8.3.0",
        "sqlalchemy",
        "pandas",
        "pymysql",
    ]
)
