from setuptools import setup, find_packages

setup(
    name="agtegra-tractors-hours",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "plotly>=5.15.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "numpy>=1.24.0",
        "openpyxl>=3.1.0",
        "xlrd>=2.0.0"
    ],
)