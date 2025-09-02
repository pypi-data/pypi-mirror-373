from setuptools import setup, find_packages
setup(
    name='DE_Lib',
    version='0.0.56',
    author='Almir J Gomes',
    author_email='almir.jg@hotmail.com',
    packages=find_packages(),
    install_requires=[
        "fbd",
        "cx_Oracle",
        "oracledb>=3.2.0",
        "pymssql>=1.1.1",
        "JayDeBeApi",
        "mysql.connector",
        "psycopg2",
        "pywinauto==0.6.9",
        "cryptography==45.0.5",
        "redshift-connector",
        "SQLAlchemy==2.0.38",
        "bcrypt==4.3.0",
        "argon2-cffi==23.1.0",
        "pyautogui"
    ],
    python_requeries='==3.9',
    description="Biblioteca de funcionalidades",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/DE-DataEng/DE_Lib.git',
)