from setuptools import setup

setup(
    name="muse_lang",  # 包名称，pip install时使用的名字
    package_data={
        "muse": ["data/*", "data/**/*"],  # 包含data目录下的文件
    },
    version="0.5.3",      # 版本号
    description="Mini language for data analysis of asset management.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Brooks Lu",
    author_email="lxc@jixunet.com",
    url="https://e.coding.net/brookslu/muse/muse.git",
    install_requires=[   # 依赖的其他包
        "numpy>=1.24.4",
        "pandas>=2.0.3",
        "polars>=1.8.0",
        "fastexcel>=0.12.0"
    ],
    python_requires=">=3.8",  # Python版本要求
    classifiers=[       # 分类信息，可选
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)