"""
This module provides task input classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from ut_dfr.pddf import PdDf
from ut_path.pathnm import PathNm
from ut_xls.op.ioipathwb import IoiPathWb as OpIoiPathWb

from ut_eviq.utils import Evin
from ut_eviq.utils import Evex
from ut_eviq.utils import Evup
from ut_eviq.cfg import Cfg

import pandas as pd
import openpyxl as op

from typing import Any, TypeAlias
TyPdDf: TypeAlias = pd.DataFrame
TyOpWb: TypeAlias = op.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]

TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnPdDf = None | TyPdDf
TnOpWb = None | TyOpWb


class TaskTmpIn:

    @classmethod
    def evupadm(cls, aod_evup_adm: TnAoD, kwargs: TyDic) -> TnOpWb:
        """
        Administration processsing for evup xlsx workbooks
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _wb_evup_adm: TnOpWb = OpIoiPathWb.sh_wb_adm(
                _in_path_evup_tmp, aod_evup_adm, _sheet_adm)
        return _wb_evup_adm

    @classmethod
    def evupdel(cls, aod_evup_del: TnAoD, kwargs: TyDic) -> TnOpWb:
        """
        Delete processsing for evup xlsx workbooks
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _wb_evup_del: TnOpWb = OpIoiPathWb.sh_wb_del(
                _in_path_evup_tmp, aod_evup_del, _sheet_del)
        return _wb_evup_del

    @classmethod
    def evupreg(
            cls, aod_evup_adm: TnAoD, aod_evup_del: TnAoD, kwargs: TyDic) -> TnOpWb:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _wb_evup_reg: TnOpWb = OpIoiPathWb.sh_wb_reg(
           _in_path_evup_tmp, aod_evup_adm, aod_evup_del, _sheet_adm, _sheet_del)
        return _wb_evup_reg


class TaskIn:

    @staticmethod
    def evupadm(EvexRead, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Administration processsing for evup
        """
        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(
                Evin.read_wb_adm_to_aod(kwargs),
                EvexRead.read_wb_exp_to_df(kwargs),
                kwargs)
        return _tup_adm

    @staticmethod
    def evupdel(EvexRead, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Delete processsing for evup
        """
        _aod_evin_del: TnAoD = Evin.read_wb_del_to_aod(kwargs)
        _pddf_evin_adm: TnPdDf = Evin.read_wb_adm_to_df(kwargs)

        _sw_del_use_evex: TyBool = kwargs.get('sw_del_use_evex', True)
        if _sw_del_use_evex:
            _pddf_evex: TnPdDf = EvexRead.read_wb_exp_to_df(kwargs)
            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
            _tup_del: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_del_use_evex(
                    _aod_evin_del, _pddf_evin_adm, _aod_evex, _pddf_evex, kwargs)
        else:
            _tup_del = Evup.sh_aod_evup_del(
                    _aod_evin_del, _pddf_evin_adm, kwargs)

        return _tup_del

    @staticmethod
    def evupreg(
           EvexRead, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD]:
        """
        Regular processsing for evup
        """
        _pddf_evin_adm: TnPdDf = Evin.read_wb_adm_to_df(kwargs)
        _aod_evin_adm: TnAoD = PdDf.to_aod(_pddf_evin_adm)
        _pddf_evex: TnPdDf = EvexRead.read_wb_exp_to_df(kwargs)
        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(
                _aod_evin_adm, _pddf_evex, kwargs)

        _aod_evin_del: TnAoD = Evin.read_wb_del_to_aod(kwargs)

        _sw_del_use_evex: TyBool = kwargs.get('sw_del_use_evex', True)
        if _sw_del_use_evex:
            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
            _tup_del: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_del_use_evex(
                _aod_evin_del, _pddf_evin_adm, _aod_evex, _pddf_evex, kwargs)
        else:
            _tup_del = Evup.sh_aod_evup_del(
                _aod_evin_del, _pddf_evin_adm, kwargs)

        return _tup_adm + _tup_del

    @staticmethod
    def evdomap(EvexRead, kwargs: TyDic) -> TyAoD:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _aod_evex_new: TyAoD = Evex.map(
                EvexRead.read_wb_exp_to_aod(kwargs),
                _cfg.Utils.d_ecv_iq2umh_iq)
        return _aod_evex_new
