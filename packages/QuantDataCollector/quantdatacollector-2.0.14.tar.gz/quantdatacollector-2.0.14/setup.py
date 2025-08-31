from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
        name="QuantDataCollector",
        version="2.0.14",
        author="TX",
        author_email="hanerzamora@gmail.com",
        description="为量化项目提供稳定且统一的数据接口",
        url="https://github.com/QuantitativeInvestment/QuantDataCollector",
        long_description=long_description,
        long_description_content_type='text/markdown',
        license='MIT',
        packages=find_packages(),
        install_requires=[
            "datetime",
            "baostock",
            "pandas",
            "pymysql",
            "psycopg2",
            "dbutils"
            ],
        zip_safe=False
        )

