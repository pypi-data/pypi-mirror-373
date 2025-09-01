from setuptools import setup, find_packages  

setup(  
    name="kxy-framework",  # 包名  
    version='1.2.13',  # 版本号  
    packages=find_packages(exclude=['tests']),
    install_requires=[  # 包的依赖项  
        "SQLAlchemy==2.0.38",
        "fastapi==0.115.8",
        "python-jose==3.4.0"
    ],  
    author="Johnliu",  # 作者名字  
    author_email="1242108463@qq.com",  # 作者邮箱  
    description="封装了ORM框架",  # 包的简短描述  
    long_description=open("README.md").read(),  # 包的详细描述，从README.md文件中读取  
    long_description_content_type="text/markdown",  # 描述文件的格式  
    license="MIT",  # 许可证类型  
    url="https://pypi.org/project/kxy-framework/",  # 项目主页或GitHub仓库地址  
    classifiers=[  # 包的分类信息  
        "Development Status :: 3 - Alpha",  
        "Intended Audience :: Developers",  
        "License :: OSI Approved :: MIT License",  
        "Programming Language :: Python",  
        "Programming Language :: Python :: 3.7",  
        # 其他分类信息  
    ],
)