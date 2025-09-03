from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ztdata",
    version="0.3.15",
    author="ZTQuant团队",
    author_email="liubocheng@ztquant.com",
    description="统一数据库客户端SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.ztquant.com/ztData/ztDataClient",
    license="MIT",
    packages=['ZTData', 'ZTData.generated'],  # 包含ZTData和ZTData.generated
    package_dir={'ZTData': 'ZTData'},  # 使用ZTData目录作为包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "grpcio>=1.44.0",
        "protobuf==5.29.0",
        "websocket-client",
        "pandas>=2.3.1",
        "pyarrow>=14.0.1"
    ],
    include_package_data=True,
    package_data={
        "ZTData.generated": ["*.py"],  # 包含ZTData.generated下的所有py文件
    },
)