"""
This module provides utilities classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from __future__ import annotations
from typing import Any, TypeAlias

import pandas as pd

from ut_path.pathnm import PathNm
from ut_xls.pd.ioipathwb import IoiPathWb

from ut_eviq.cfg import Cfg

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyPath = str

TnDic = None | TyDic
TnAoD = None | TyAoD
TnPdDf = None | TyPdDf


class Evex:
    """
    EcoVadis Export class
    """
    kwargs_wb = dict(dtype=str, keep_default_na=False, engine='calamine')

    @classmethod
    def read_wb_exp_to_df(cls, kwargs: TyDic) -> TnPdDf:
        _cfg = kwargs.get('Cfg', Cfg)
        _pddf: TnPdDf = IoiPathWb.read_wb_to_df(
                PathNm.sh_path(_cfg.InPath.evex, kwargs),
                kwargs.get('sheet_exp', _cfg.sheet_exp),
                **cls.kwargs_wb)
        return _pddf

    @classmethod
    def read_wb_exp_to_aod(cls, kwargs: TyDic) -> TnAoD:
        _cfg = kwargs.get('Cfg', Cfg)
        _aod: TnAoD = IoiPathWb.read_wb_to_aod(
                PathNm.sh_path(_cfg.InPath.evex, kwargs),
                kwargs.get('sheet_exp', _cfg.sheet_exp),
                **cls.kwargs_wb)
        return _aod
