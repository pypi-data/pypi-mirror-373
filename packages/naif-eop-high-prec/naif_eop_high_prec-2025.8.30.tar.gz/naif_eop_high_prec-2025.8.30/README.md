# naif_eop_high_prec: NAIF High Precision Earth Orientation Parameters Kernel for SPICE
#### A Python package by the Asteroid Institute, a program of the B612 Foundation

[![Python 3.7+](https://img.shields.io/badge/Python-3.7%2B-blue)](https://img.shields.io/badge/Python-3.7%2B-blue)
[![PyPI version](https://img.shields.io/pypi/v/naif-eop-high-prec)](https://img.shields.io/pypi/v/naif-eop-high-prec)
[![PyPi downloads](https://img.shields.io/pypi/dm/naif-eop-high-prec)](https://img.shields.io/pypi/dm/naif-eop-high-prec)  
[![Build and Test](https://github.com/B612-Asteroid-Institute/naif_eop_high_prec/actions/workflows/build_test.yml/badge.svg)](https://github.com/B612-Asteroid-Institute/naif_eop_high_prec/actions/workflows/build_test.yml)
[![Build, Test, & Publish](https://github.com/B612-Asteroid-Institute/naif_eop_high_prec/actions/workflows/build_test_publish.yml/badge.svg)](https://github.com/B612-Asteroid-Institute/naif_eop_high_prec/actions/workflows/build_test_publish.yml)
[![Compare Upstream](https://github.com/B612-Asteroid-Institute/naif_eop_high_prec/actions/workflows/compare_upstream.yml/badge.svg)](https://github.com/B612-Asteroid-Institute/naif_eop_high_prec/actions/workflows/compare_upstream.yml)  

This package ships the Navigation and Ancillary Information Facility's high precision Earth orientation parameters (EOP) [kernel](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/earth_latest_high_prec.bpc).

**This is not an official NAIF package**. It is an automatically generated mirror of the file so that it is
installable via `pip`.

Every night at around 2:15 AM UTC, the NAIF high precision Earth orientation parameters (EOP) kernel is downloaded and compared (via md5 checksum) to the current version of this package. If the checksums are different, a new package will be published.

## Installation

The latest version of the file can be installed via pip:  
`pip install naif-eop-high-prec`

## Usage
```python
import spiceypy as sp
from naif_eop_high_prec import eop_high_prec

sp.furnsh(eop_high_prec)
```

## Acknowledgment

This project makes use of data provided and maintained by the Navigation and Ancillary Information Facility (NAIF). 

### References
[1] Acton, C.H.; "Ancillary Data Services of NASA's Navigation and Ancillary Information Facility;" Planetary and Space Science, Vol. 44, No. 1, pp. 65-70, 1996.
DOI 10.1016/0032-0633(95)00107-7  
[2] Charles Acton, Nathaniel Bachman, Boris Semenov, Edward Wright; A look toward the future in the handling of space science mission geometry; Planetary and Space Science (2017);
DOI 10.1016/j.pss.2017.02.013
