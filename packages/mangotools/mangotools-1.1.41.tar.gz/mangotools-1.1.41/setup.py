from setuptools import setup, find_packages

__version__ = '1.1.41'

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='mangotools',
    version=__version__,
    description='测试工具',
    long_description=long_description,
    package_data={
        'mangotools': [
            'mangos/*',
            'mangos/**/*',
        ]
    },
    include_package_data=True,
    author='毛鹏',
    author_email='729164035@qq.com',
    url='https://gitee.com/mao-peng/testkit',
    packages=find_packages(),
    install_requires=[
        'aiomysql>=0.2.0',
        'PyMySQL>=1.1.1',
        'jsonpath>=0.82.2',
        'cachetools>=5.3.1',
        'Faker>=24.1.0',
        'diskcache>=5.6.3',
        'pydantic>=2.9.2',
        'colorlog>=6.7.0',
        'assertpy>=1.1',
        'deepdiff>=8.0.1',
        'requests>=2.32.3',
        'openpyxl>=3.1.5',
        'concurrent-log-handler==0.9.28',
        'dulwich==0.21.7'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ]
)

"""


python -m pip install --upgrade setuptools wheel
python -m pip install --upgrade twine

python setup.py check
python setup.py sdist bdist_wheel
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

"""
