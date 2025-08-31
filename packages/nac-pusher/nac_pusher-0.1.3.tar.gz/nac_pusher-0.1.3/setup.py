import toml
from setuptools import setup, find_packages

# 读取pyproject.toml文件中的信息
with open("pyproject.toml", "r", encoding="utf-8") as f:
    pyproject_data = toml.load(f)
    name = pyproject_data["project"]["name"]
    version = pyproject_data["project"]["version"]
    description = pyproject_data["project"]["description"]
    authors = pyproject_data["project"]["authors"]
    python_requires = pyproject_data["project"]["requires-python"]
    install_requires = pyproject_data["project"]["dependencies"]
    classifiers = pyproject_data["project"]["classifiers"]
    urls = pyproject_data["project"]["urls"]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 提取作者信息
author = authors[0]["name"] if authors else ""
author_email = authors[0]["email"] if authors else ""

# 提取URL
url = urls.get("Homepage", "") if urls else ""

setup(
    name=name,
    version=version,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    packages=find_packages(),
    classifiers=classifiers,
    python_requires=python_requires,
    install_requires=install_requires,
)