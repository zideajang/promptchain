from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here,"README.md"),encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='promptchain',
    version='1.0.0',
    author='zidea',
    author_email='zidea2015@163.com',
    description='tiny agent frame work',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="agentframework muliti-agents llm prompt chain",
    url="https://github.com/zideajang/prompt_chain",
    # install_requires=requirements,
    packages=find_packages(exclude=["examples","chain","function_programming"]),
    python_requires=">=3.9"
)