from importlib.resources import files

eop_high_prec = files("naif_eop_high_prec").joinpath("earth_latest_high_prec.bpc").as_posix()
_eop_high_prec_md5 = files("naif_eop_high_prec").joinpath("earth_latest_high_prec.md5").as_posix()
