from setuptools import setup

# 这个setup.py与pyproject.toml配合使用
# 元数据主要在pyproject.toml中定义，这里保持兼容性并可添加自定义构建逻辑
setup(
    # 基础元数据（与pyproject.toml中的[project]部分对应）
    name="qrpa",
    version="1.0.5",
    description="qsir's rpa library",
    author="QSir",
    author_email="1171725650@qq.com",
    license="GPL-3.0-or-later",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",

    # 以下部分可根据需要添加
    # packages=["qrpa"],  # 如果需要显式指定包
    # py_modules=["module_name"],  # 如果是单文件模块
    # install_requires=[],  # 依赖项（也可在pyproject.toml中定义）

    # 可添加自定义构建逻辑，例如：
    # cmdclass={
    #     'custom_command': CustomCommand,
    # },
)
