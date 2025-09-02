# Quadrature rules

[The online encylopedia of quadrature rules](https://quadraturerules.org) is a reference website that lists a number of quadrature rules.

Quadrature rules are sets of points and weights that are used to approximate integrals. If $\{p_0,\dots,p_{n-1}\}\subset\mathbb{R}^d$ and $\{w_0,\dots,w_{n-1}\}\subset\mathbb{R}$
are the points and weights (repectively) of the quadrature rule for a single integral, then:

$$\int f(x)\,\mathrm{d}x \approx \sum_{i=0}^{n-1}f(p_i)w_i$$

## Website

Before building the online encylopedia of quadrature rules, you must first install qrtools
from the [python](python) directory:
```bash
cd python
python3 -m pip install .
```

The online encylopedia of quadrature rules website can then be built by running:

```bash
cd website
python3 build.py
```
## Libraries

All of the quadrature rules included in the online encylopedia of quadrature rules are included in the quadraturerules library, which is available in the following languages:

| Language                                           | Badges |
| -------------------------------------------------- | ------ |
| [C](https://quadraturerules.org/libraries/c.html)                  | [![Test and build C library](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-c.yml/badge.svg)](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-c.yml) |
| [C++](https://quadraturerules.org/libraries/cpp.html)              | [![Test and build C++ library](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-cpp.yml/badge.svg)](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-cpp.yml) |
| [Fortran](https://quadraturerules.org/libraries/fortran90.html)    | [![Test and build Fortran 90 library](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-fortran90.yml/badge.svg)](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-fortran90.yml) |
| [FORTRAN 77](https://quadraturerules.org/libraries/fortran77.html) | [![Test and build Fortran 77 library](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-fortran77.yml/badge.svg)](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-fortran77.yml) |
| [Julia](https://quadraturerules.org/libraries/julia.html)          | [![Test and build Julia library](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-julia.yml/badge.svg)](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-julia.yml) |
| [Python](https://quadraturerules.org/libraries/python.html)        | [![Test and build Python library](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-python.yml/badge.svg)](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-python.yml) [![PyPI](https://img.shields.io/pypi/v/quadraturerules?color=blue&label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/quadraturerules/) |
| [Rust](https://quadraturerules.org/libraries/rust.html)            | [![Test and build Rust library](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-rust.yml/badge.svg)](https://github.com/quadraturerules/quadraturerules/actions/workflows/library-rust.yml) [![crates.io](https://img.shields.io/crates/v/quadraturerules?color=blue&logo=Rust&logoColor=white)](https://crates.io/crates/quadraturerules/) [![docs.rs](https://img.shields.io/docsrs/quadraturerules?logo=Docs.rs&logoColor=white)](https://docs.rs/quadraturerules/) |

Before building any of the libraries, you must first install qrtools
from the [python](python) directory:
```bash
cd python
python3 -m pip install .
```

You can then build the libraries using the [build.py](library/build.py) script in the library directory.
For example, to build the python library, you can run:

```bash
cd library
python build.py python
```

and to build the rust library, you can run:

```bash
cd library
python build.py rust
```

## Python library

The quadraturerules Python library is available on [PyPI](https://pypi.org/project/quadraturerules/).
It can be installed by running:

```bash
python -m pip install quadraturerules
```

## Usage

The library's function `single_integral_quadrature` can be used to get the points and weights
of quadrature rules for a single integral. For example the following snippet will create an
order 3 Xiao--Gimbutas rule on a triangle:

```python
from quadraturerules import Domain, QuadratureRule, single_integral_quadrature

points, weights = single_integral_quadrature(
    QuadratureRule.XiaoGimbutas,
    Domain.Triangle,
    3,
)
```

Note that the points returned by the library are represented using
[barycentric coordinates](/barycentric.md).

## Generating the library
The Python quadraturerules library can be generated from the templates in the online encyclopedia
of quadrature rules GitHub repo. First clone the repo and move into the library directory:

```bash
git clone https://github.com/quadraturerules/quadraturerules.git
cd quadraturerules/library
```

The Python library can then be generated by running:

```bash
python build.py python
```

This will create a directory called python.build containing the Python source code.

Tests can then be run by moving into this folder and using pytest:

```bash
cd python.build
python -m pytest test/
```

