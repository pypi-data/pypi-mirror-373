import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="powerplan",
    version="1.2.0",
    author="Temal",
    author_email="temal@colinm.de",
    description="Simple Windows-only Python package to read your current power plan (name and GUID) and switch to one of the standard Windows power plans.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/temal32/powerplan",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.0',
    entry_points={
        'console_scripts': [
            'powerplan=powerplan:main',
        ],
    }
)