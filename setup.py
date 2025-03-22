from setuptools import setup, find_packages

setup(
    name="pdf_edit",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "reportlab",
        "PyMuPDF", 
    ]
)