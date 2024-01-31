from setuptools import setup

setup(
    name='scrapy_work',
    version='1.0',
    author='ConstasJ',
    author_email='constasJ@qq.com',
    description='a example for pack python',
    keywords='spider',  # 关键词
    url='https://github.com/CJGroup/scrapy-work',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml',
    ],
    license='MIT License',
    packages=['scrapy_work'],
    scripts=['spider']
)
