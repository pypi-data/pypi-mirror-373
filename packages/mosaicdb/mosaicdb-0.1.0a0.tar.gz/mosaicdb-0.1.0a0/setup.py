from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mosaicdb",
    version="0.1.0-alpha",
    description="Universal, framework-independent ORM for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Akash Nath",
    author_email="anath5440@gmail.com",
    url="https://github.com/Akash-nath29/mosaic",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "mysql-connector-python",
        "psycopg2",
        "pymongo"
    ],
    entry_points={
        "console_scripts": [
            "mosaicdb=mosaic.cli:main"
        ]
    },
    python_requires='>=3.7',
    keywords="orm database sql nosql sqlite mysql postgres mongodb",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
