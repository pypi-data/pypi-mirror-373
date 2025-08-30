from setuptools import setup, find_packages

setup(
    name="outlier_library",  # name on PyPI
    version="0.1.0",
    author="Irene Betsy D",
    author_email="betsydnicholraja@gmail.com",
    description="A Python library for identifying and handling outliers",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/outlier_library",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # or Apache
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
