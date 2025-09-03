import setuptools  # 导入setuptools打包工具

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="noteparse",  # 用自己的名替换其中的YOUR_USERNAME_
    version="1.1.22",  # 包版本号，便于维护版本,保证每次发布都是版本都是唯一的
    author="maoyuyan",  # 作者，可以写自己的姓名
    author_email="294567571@qq.com",  # 作者联系方式，可写自己的邮箱地址
    description="a package for parse html to noteinfo",  # 包的简述
    long_description=open("README.md", "r", encoding="utf-8").read(),  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    platforms=["all"],
    # url="https://github.com/m294567571/noteparse.git",  # 自己项目地址，比如github的项目地址
    # http://gitlab.uniview.com/mkt_uic/uic-spider.git
    packages=setuptools.find_packages(),
    # entry_points={
    #     "console_scripts" : ['noteparse = noteparse.__init__:init']
    # }, #安装成功后，在命令行输入mwjApiTest 就相当于执行了mwjApiTest.manage.py中的run了
    install_requires=[
        'requests>=2.32.3',
        'bs4>=0.0.2',
        'fastapi>=0.115.4',
        'pydantic>=2.7.3',
        'loguru>=0.7.2',
        'zhipuai>=2.1.5.20230904',
        'selenium>=4.21.0',
        'fake-useragent>=1.5.1'
    ],
    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        # 开发的目标用户
        'Intended Audience :: Developers',
        # 许可证信息
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Natural Language :: Chinese (Simplified)',
        # 目标 Python 版本
        'Programming Language :: Python :: 3',
        # 属于什么类型
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    license='MIT'
)
