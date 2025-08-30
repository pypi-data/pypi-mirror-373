import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

# 添加NOTICE文件内容读取
with open("NOTICE", "r", encoding='utf-8') as notice_file:
    notice_content = notice_file.read()
    
    
setuptools.setup(
    name="xiaothink",  # 模块名称
    version="1.2.4",  # 当前版本
    author="Shi Jingqi",  # 使用真实姓名而非昵称
    author_email="xiaothink@foxmail.com",  # 作者邮箱
    description="一个AI工具包，帮助用户快速调用小思框架（Xiaothink）相关接口。",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    # 模块相关的元数据
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
    ],
    
    # 关键添加：包含许可证文件和声明
    license="Apache License 2.0",
    license_files=("LICENSE", "NOTICE"),
    
    # 依赖模块
    install_requires=[
        "numpy>=1.21.0",
        "tensorflow>=2.10.0",  # 根据实际依赖调整
    ],
    
    python_requires='>=3',

)


