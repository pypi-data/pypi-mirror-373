from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

requires = [
    'channels==3.0.3',
    'pymongo~=4.11.2',
    'asgiref~=3.8.1',
    'django-cors-headers==4.2.0',
    'pandas==2.2.3',
    'openpyxl==3.1.5',
    'deepmerge~=2.0',
    'minio==7.2.2',
]

setup(
    name="valar",  # 包名
    version="1.2.5",  # 版本号
    author="LYP",  # 作者
    author_email="liuyinpeng@buaa.edu.cn",  # 邮箱
    description="valar for morghulis",  # 简短描述
    long_description=long_description,  # 详细说明
    long_description_content_type="text/markdown",  # 详细说明使用标记类型
    url="https://gitee.com/GRIFFIN120/valar_dev",  # 项目主页
    packages=find_packages(where="src"),  # 需要打包的部分
    package_dir={"": "src"},  # 设置src目录为根目录
    python_requires=">=3.9",  # 项目支持的Python版本
    install_requires=requires,  # 项目必须的依赖
    include_package_data=False  # 是否包含非Python文件（如资源文件）
)
