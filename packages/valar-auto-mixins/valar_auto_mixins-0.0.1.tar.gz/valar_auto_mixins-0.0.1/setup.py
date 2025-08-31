from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

requires = [
    'Django~=4.2.20',
]

setup(
    name="valar_auto_mixins",  # 包名
    version="0.0.1",  # 版本号
    author="LYP",  # 作者
    author_email="liuyinpeng@buaa.edu.cn",  # 邮箱
    description="valar auto mixins",  # 简短描述
    long_description=long_description,  # 详细说明
    long_description_content_type="text/markdown",  # 详细说明使用标记类型
    url="https://gitee.com/GRIFFIN120",  # 项目主页
    packages=find_packages(where="src"),  # 需要打包的部分
    package_dir={"": "src"},  # 设置src目录为根目录
    python_requires=">=3.9",  # 项目支持的Python版本
    install_requires=requires,  # 项目必须的依赖
    include_package_data=False  # 是否包含非Python文件（如资源文件）
)
