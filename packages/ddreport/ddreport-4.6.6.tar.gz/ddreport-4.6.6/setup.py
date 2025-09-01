#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: duanliangcong
# Mail: 137562703@qq.com
# Created Time:  2022-11-02 15:00:00
#############################################

# pip install twine
# python setup.py sdist
# twine upload dist/*

#############################################
#################使用方法#####################
#############################################
"""
目录结构
UPSDIST
    ddreport        库文件夹
    MANIFEST.in     配置
    setup.py        当前文件

1.cmd进入UPSDIST目录
2.执行命令：python setup.py sdist
3.执行命令：twine upload dist/*
"""

# 每次更新需要修改 version 字段
from setuptools import setup, find_packages, find_namespace_packages
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="ddreport",
    version="4.6.6",
    description="pytest测试报告 1.解决api详情没有展示的问题, 2.解决fixture是function时只调用一次的问题",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://blog.csdn.net/weixin_43975720/article/details/137867720",
    author="duanliangcong",
    author_email="137562703@qq.com",
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing'
    ],
    license="MIT Licence",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "pytest11": [
            "ddreport = ddreport"
        ]
    },
    install_requires=["requests", "sshtunnel", "pymysql", "psycopg2", "jsonpath", 'openpyxl', 'deepdiff', 'python-dateutil'],
)

