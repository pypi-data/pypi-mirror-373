#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time : 2023/11/08 18:38 
# @Author : JY
"""
目前可以稳定的版本，后面不行了如果改不了的话就用这个版本
'pymysql==1.1.0',
'requests==2.26.0'
"""

from setuptools import setup

setup(
    name='jyhelper',
    version='1.7.9',
    packages=['jyhelper'],
    install_requires=[
        'pymysql',
        'requests'
    ],
    description='各种实用、常用的小函数、类',
    long_description=open('README.md',encoding='utf-8').read(),  # 详细描述，通常从 README.md 中读取
    long_description_content_type='text/markdown',  # README.md 的内容类型
    author='JY',
    author_email='your-email@example.com',
    url='https://pypi.org/project/jyhelper/',  # 项目主页
    python_requires='>=3.0',  # Python 的版本要求
)
