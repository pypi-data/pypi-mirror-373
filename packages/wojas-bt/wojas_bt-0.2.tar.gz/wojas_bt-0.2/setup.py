from setuptools import setup, find_packages

setup(
    name="wojas_bt",
    version="0.2",
    description="Easily create beautiful gradient and rainbow text in Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="W0jas",
    url="https://github.com/wojase/wojas_bt",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Terminals",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="gradient rainbow text terminal colors ansi",
    license="MIT",
    project_urls={
        "Bug Tracker": "https://github.com/wojase/wojas_bt/issues",
        "Source": "https://github.com/wojase/wojas_bt",
    },
)
