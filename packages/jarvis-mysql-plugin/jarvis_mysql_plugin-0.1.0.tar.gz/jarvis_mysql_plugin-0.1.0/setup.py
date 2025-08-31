from setuptools import setup, find_packages

setup(
    name="jarvis_mysql_plugin",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.3",
        "jarvis-api-library>=1.0.0",
    ],
    author="Samuel Lewis",
    description="A Plugin that assists The J.A.R.V.I.S. Project with MySQL database management and operations.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)
