
import os
from setuptools import setup, find_packages

setup(
    name="x_make_markdown_x",
    version="1.0.0",
    author="Roy GM",
    author_email="eye4357@outlook.com",
    description="Makes markdown.",
    long_description=open(os.path.join(r'C:/x_main_x/x_legatus_tactica_core_x/x_code_x/x_make_markdown_x\docs', "README.md"), encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/x_make_markdown_x/",
    packages=find_packages(),
    install_requires=['markdown', 'pdfkit'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
