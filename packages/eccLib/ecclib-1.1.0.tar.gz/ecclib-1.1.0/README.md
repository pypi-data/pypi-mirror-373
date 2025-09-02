# eccLib

[![Pipeline](https://gitlab.platinum.edu.pl/eccdna/eccLib/badges/main/pipeline.svg)](https://gitlab.platinum.edu.pl/eccdna/eccLib/-/commits/main)
[![Python Documentation](https://img.shields.io/badge/Documentation-Python-blue)](https://gitlab-pages.platinum.edu.pl/eccdna/eccLib/)
[![C Documentation](https://img.shields.io/badge/Documentation-C-green)](https://gitlab-pages.platinum.edu.pl/eccdna/eccLib/internal/)

eccLib is a python high-performance library designed for parsing genomic files
and analysing genomic context.

## Install

The most reliable way of installing this library is to use pip. You can do this
with the following command:

```Bash
pip install eccLib
```

If you want to install this library from source, you can do this by cloning the
repository and using the makefile.

```Bash
make install
```

If for some reason, makefile doesn't work for you, the following sequence of
steps should work as well:

1. Initialize third party libraries

   ```sh
   git submodule update --init --remote
   ```

2. Ensure you have a compiler installed

   You are going to need to have a C/C++ compiler installed on your system. For
   Linux I recommend `gcc` and for Windows realistically speaking you don't
   have a choice and will have to install `msvc`. In order to compile run the
   following commands

3. Build the library

   ```Bash
   pip install .
   ```

In order to then uninstall this library do this:

```Bash
pip uninstall eccLib
```

## Usage

Currently the library supports parsing and processing of GTF and FASTA formats.
Your IDE should pick up the `.pyi` file associated with the library and provide
documentation for the functions and classes. Additionally the library is
properly typed, so you should be able to use it with type checkers like `mypy`.

For more detailed notes on usage, please refer to the
[documentation](https://gitlab-pages.platinum.edu.pl/eccdna/eccLib/), you can also
build it yourself by running the following command:

```Bash
make python-doc
```

## Development

The source code of the library is stored in the `src` folder. You can learn
about the Python/C API [here](https://docs.python.org/3/c-api/index.html).
The preferred way of building the library for development and debugging is to
use the `debug` target in the makefile. This will build the library with
debugging symbols. Be sure to check out the [test](./test/) folder during
development, as it contains a lot of useful tests. Also consult with the
[internal documentation](https://gitlab-pages.platinum.edu.pl/eccdna/eccLib/internal/)
for more information on the C code. You can build the documentation by running
the following command:

```Bash
make internal-doc
```

If you wish to contribute to the library, please first consult the
[contributing](./CONTRIBUTING.md) file.

## Third party libraries

- [hashmap.h](https://github.com/sheredom/hashmap.h) has been utilized as the
  low level hashmap implementation
- [xxHash](https://github.com/Cyan4973/xxHash)
  ([BSD 2-Clause](./xxHash/LICENSE)) has been used for the hashing function used
  by the hashmap

## Benchmarking

You can find the benchmarking scripts in the `bench` folder. The
[README](./bench/README.md) file in that folder contains more detailed
information on how to run them.

## Wheel building

For building wheels for multiple Python versions, we use
[cibuildwheel](https://github.com/pypa/cibuildwheel). First install it:

```sh
pip install cibuildwheel
```

then run it:

```sh
python -m cibuildwheel --output-dir wheelhouse
```

## License

This library is licensed under
[GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html)
