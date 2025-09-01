"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
from ut_path.pathnm import PathNm

# from ut_xls.op.ioipathwb import IoiPathWb as OpIoiPathWb
from ut_xls.op.ioopathwb import IooPathWb as OpIooPathWb
from ut_xls.pe.ioopathwb import IooPathWb as PeIooPathWb

from ut_eviq.cfg import Cfg
from ut_eviq.taskin import TaskTmpIn

# import pandas as pd
import openpyxl as op

from typing import Any, TypeAlias
TyOpWb: TypeAlias = op.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyCmd = str
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnOpWb = None | TyOpWb


class TaskOut:

    @classmethod
    def evupadm(cls, tup_adm: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Administration processsing for evup xlsx workbooks
        """
        _aod_evup_adm, _doaod_evin_adm_vfy = tup_adm

        _cfg = kwargs.get('Cfg', Cfg)

        OpIooPathWb.write(
                TaskTmpIn.evupadm(_aod_evup_adm, kwargs),
                PathNm.sh_path(_cfg.OutPath.evup_adm, kwargs))

        _out_path_evin_adm_vfy = PathNm.sh_path(_cfg.OutPath.evin_adm_vfy, kwargs)
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_adm_vfy, _out_path_evin_adm_vfy)

    @classmethod
    def evupdel(cls, tup_del: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Delete processsing for evup xlsx workbooks
        """
        _aod_evup_del, _doaod_evin_del_vfy = tup_del

        _cfg = kwargs.get('Cfg', Cfg)

        OpIooPathWb.write(
                TaskTmpIn.evupdel(_aod_evup_del, kwargs),
                PathNm.sh_path(_cfg.OutPath.evup_del, kwargs))

        PeIooPathWb.write_wb_from_doaod(
                _doaod_evin_del_vfy,
                PathNm.sh_path(_cfg.OutPath.evin_del_vfy, kwargs))

    @classmethod
    def evupreg_reg_wb(
            cls,
            tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD],
            kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del

        _cfg = kwargs.get('Cfg', Cfg)

        OpIooPathWb.write(
                TaskTmpIn.evupreg(_aod_evup_adm, _aod_evup_del, kwargs),
                PathNm.sh_path(_cfg.OutPath.evup_reg, kwargs))

        PeIooPathWb.write_wb_from_doaod(
                _doaod_evin_adm_vfy | _doaod_evin_del_vfy,
                PathNm.sh_path(_cfg.OutPath.evin_reg_vfy, kwargs))

    @classmethod
    def evupreg_adm_del_wb(
            cls,
            tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD],
            kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        two xlsx Workbooks:
          the first one contains a populated admin-sheet
          the second one contains a populated delete-sheet
        """
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del

        _cfg = kwargs.get('Cfg', Cfg)

        OpIooPathWb.write(
                TaskTmpIn.evupadm(_aod_evup_adm, kwargs),
                PathNm.sh_path(_cfg.OutPath.evup_adm, kwargs))

        OpIooPathWb.write(
                TaskTmpIn.evupdel(_aod_evup_del, kwargs),
                PathNm.sh_path(_cfg.OutPath.evup_del, kwargs))

        PeIooPathWb.write_wb_from_doaod(
                _doaod_evin_adm_vfy | _doaod_evin_del_vfy,
                PathNm.sh_path(_cfg.OutPath.evin_reg_vfy, kwargs))

    @classmethod
    def evdomap(cls, aod_evex: TyAoD, kwargs: TyDic) -> None:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        _cfg = kwargs.get('Cfg', Cfg)

        PeIooPathWb.write_wb_from_aod(
                aod_evex,
                PathNm.sh_path(_cfg.OutPath.evex, kwargs),
                kwargs.get('sheet_exp', _cfg.sheet_exp))
