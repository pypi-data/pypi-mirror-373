from setuptools import setup, find_packages

setup(
    name="maisaedu_poormans_dms",
    version="1.2.58",
    description="A library for making database migration tasks, for +A Education",
    license="MIT License",
    author="A+ Educação",
    author_email="dataeng@maisaedu.com.br",
    packages=find_packages(),
    scripts=[],
    install_requires=[
        "pandas",
        "scipy",
        "numpy",
        "wheel",
        "psycopg2-binary",
        "aiopg",
        "aiochannel",
        "pymssql",
        "datetime",
        "sqlalchemy",
        "pyarrow",
        "boto3",
    ],  # external packages as dependencies
)
