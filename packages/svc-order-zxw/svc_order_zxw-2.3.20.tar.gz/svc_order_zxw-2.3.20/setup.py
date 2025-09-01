from setuptools import setup, find_packages

setup(
    name="svc_order_zxw",
    version="2.3.20",
    packages=find_packages(),
    package_data={
        '': ['**/*.vue', '**/*.ts', '**/*.js'],  # 包含所有子文件夹中的.vue和.ts文件
    },
    install_requires=[
        'fastapi>=0.112.0,<0.113',
        'sqlalchemy==2.0.32',
        'greenlet==3.0.3',
        'asyncpg==0.29.0',
        'psycopg2-binary>=2.9.10',
        'uvicorn>=0.30.0,<0.31.0',
        'app-tools-zxw>=2.2.4'
    ],
    author="薛伟的小工具",
    author_email="jingmu_app@foxmail.com",
    description="订单与支付服务: 支持苹果内购订阅",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunshineinwater/",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
