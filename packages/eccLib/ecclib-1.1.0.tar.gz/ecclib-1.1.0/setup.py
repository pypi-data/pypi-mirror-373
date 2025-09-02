from setuptools import Extension, setup
from os import getenv
from pathlib import Path

args = []

env_var_value = getenv("ECCLIB_DEBUG")
if env_var_value == "1":
    args.extend(
        ["-O0", "-g3", "-Wall", "-Wextra", "-fvar-tracking", "-Wno-cast-function-type"]
    )


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

module1 = Extension(
    "eccLib",
    sources=[
        "src/eccLib.c",
        "src/common.c",
        "src/reader.c",
        "src/functions.c",
        "src/formats/fasta.c",
        "src/formats/gtf.c",
        "src/classes/GtfDict.c",
        "src/classes/GtfReader.c",
        "src/classes/GtfList.c",
        "src/classes/FastaBuff.c",
        "src/classes/FastaReader.c",
        "src/hashmap_ext.c",
        "xxHash/xxhash.c",
    ],
    include_dirs=["src", "xxHash"],  # this doesnt work for sdist, thats why MANIFEST.in
    extra_compile_args=args,
)

setup(
    name="eccLib",
    version="1.1.0",
    description="High-performance library designed for parsing genomic files and analysing genomic context",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.platinum.edu.pl/eccdna/eccLib",
    author="Tomasz Chady",
    author_email="tomek.chady@gmail.com",
    python_requires=">=3.10",
    ext_modules=[module1],
    packages=["eccLib"],
    package_dir={"eccLib": "./stub"},
    package_data={"eccLib": ["__init__.pyi"]},
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: C",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
)

# to compile and install this library run the following commands:
# pip install .
# Python will do it's thing just fine :)
