import sys
from setuptools import find_packages, setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="logs-py-solutions",
    version="0.2.3",
    packages=find_packages(),
    author="Bruker BioSpin GmbH & Co KG",
    author_email="support@sciy.com",
    description="Prebuild solution library for the logs-py package",
    long_description=(this_directory / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://solutions.logs-python.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
    ],
    python_requires='>=3.8',
    install_requires=[
        "logs-py>=3.0.14",
        "ipykernel",
        "jinja2",
        "jupyter",
        "matplotlib",
        "pandas",
        "pdf2image",
        "pdfkit",
        "plotly",
        "PyPDF2",
        "python-dateutil",
        "qrcode[pil]",
        "tqdm",
        "wkhtmltopdf",
        "openpyxl",
        "colorama",
    ],
)
