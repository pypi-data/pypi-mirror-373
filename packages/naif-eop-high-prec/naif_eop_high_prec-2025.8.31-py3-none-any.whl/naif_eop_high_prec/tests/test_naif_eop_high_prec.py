import os
import spiceypy as spice

from ..compare import calculate_md5


def test_eop_high_prec():
    from naif_eop_high_prec import eop_high_prec

    assert os.path.isfile(eop_high_prec)

def test_eop_high_prec_load():
    from naif_eop_high_prec import eop_high_prec

    spice.furnsh(eop_high_prec)
    spice.unload(eop_high_prec)

def test__eop_high_prec_md5():
    from naif_eop_high_prec import _eop_high_prec_md5

    assert os.path.isfile(_eop_high_prec_md5)


def test__eop_high_prec_md5_matches():
    from naif_eop_high_prec import _eop_high_prec_md5, eop_high_prec

    # Read the MD5 hash from the file that comes with the
    # package
    with open(_eop_high_prec_md5, "r") as f:
        md5_hash = f.read().split()[0]

    # Compare to the MD5 calculated from the naif_eop_high_prec file
    assert calculate_md5(eop_high_prec) == md5_hash
