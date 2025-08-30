from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="csv_to_json_format",
    version="0.0.1",
    author="Simone A Diana",
    author_email="si_ap@hotmail.com",
    description="Uma ferramenta simples para converter arquivos CSV para JSON.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SiDianaGit/csv_to_json_format",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas',
    ],
)