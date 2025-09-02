from setuptools import setup, find_packages

setup(
    name="gepeto",
    version="1.1.23",
    packages=find_packages(),
    install_requires=[
        "numpy>=2.2.0",
        "pytest",
        "requests>=2.32.0",
        "tqdm>=4.65.0",
        "pre-commit>=4.0.0",
        "instructor>=1.7.0",
        "litellm>=1.49.1",
    ],
    author="Uzair",
    author_email="uzair@hellogepeto.com",
    description="pip install gepeto",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gepetoai/gepeto",
)
