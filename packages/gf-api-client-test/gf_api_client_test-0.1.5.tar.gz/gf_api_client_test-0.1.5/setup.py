from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gf-api-client-test",
    version="0.1.5",
    author="gf_gaoxinzhe",
    author_email="gao89622@163.com",
    description="广发证券开放平台 API 客户端(测试）",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.0.0",
    ],
)
