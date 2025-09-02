"""
This module provides input verification classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from __future__ import annotations
from typing import Any, TypeAlias

import pandas as pd

from ut_dic.dic import Dic
from ut_dic.doa import DoA
from ut_eviq.cfg import Cfg

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyAoStr = list[str]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoD = dict[Any, TyDic]
TyDoB = dict[Any, bool]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyStr = str
TyTup = tuple[Any]
TyTask = Any
TyDoPdDf = dict[Any, TyPdDf]
TyPdDf_DoPdDf = TyPdDf | TyDoPdDf
TyToAoDDoAoD = tuple[TyAoD, TyDoAoD]

TnDic = None | TyDic
TnAoD = None | TyAoD
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD
TnPdDf = None | TyPdDf
TnStr = None | str


class EvinVfyAdm:
    """
    OmniTracker EcoVadis class
    """
    coco_is_empty = 'adm_wrn_coco_is_empty'
    coco_is_invalid = 'adm_wrn_coco_is_invalid'
    cpydinm_is_empty = 'adm_err_cpydinm_is_empty'
    duns_is_empty = 'adm_err_duns_is_empty'
    duns_isnot_numeric = 'adm_err_duns_is_not_numeric'
    duns_isnot_unique = 'adm_wrn_duns_is_not_unique'
    poco_is_empty = 'adm_wrn_poco_is_empty'
    poco_is_invalid = 'adm_wrn_poco_is_invalid'
    objectid_is_empty = 'adm_err_objectid_is_empty'
    objectid_isnot_unique = 'adm_err_objectid_is_not_unique'
    regno_is_empty = 'adm_wrn_regno_is_empty'
    town_is_empty = 'adm_wrn_town_is_empty'
    town_is_invalid = 'adm_wrn_town_is_invalid'

    @classmethod
    def vfy_duns(
            cls, d_sw: TyDoB, d_evin: TyDic,
            dod: TyDoD, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify DUNS number
        """
        if not kwargs.get('sw_adm_vfy_duns', True):
            return
        _key: TnStr = Cfg.Utils.evin_key_duns
        _val: TnStr = Dic.get(d_evin, _key)
        if not _val:
            DoA.append_unique_by_key(doaod_vfy, cls.duns_is_empty, d_evin)
            d_sw['duns'] = False
            return
        if not _val.isdigit():
            DoA.append_unique_by_key(doaod_vfy, cls.duns_isnot_numeric, d_evin)
            d_sw['duns'] = False
            return
        if kwargs.get('sw_adm_vfy_duns_is_unique', True):
            if dod[_key][_val] > 1:
                DoA.append_unique_by_key(doaod_vfy, cls.duns_isnot_unique, d_evin)
                # d_sw['duns'] = False
                # return
        if len(_val) < 9:
            _val = f"{_val:09}"
        Dic.set_by_key(d_evin, _key, _val)
        d_sw['duns'] = True
        return

    @classmethod
    def vfy_cpydinm(
            cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify Company display name
        """
        if not kwargs.get('sw_adm_vfy_cpydinm', True):
            return
        _key = Cfg.Utils.evin_key_cpydinm
        _val = Dic.get(d_evin, _key)
        if not _val:
            DoA.append_unique_by_key(doaod_vfy, cls.cpydinm_is_empty, d_evin)
            d_sw['cpydinm'] = False
            return
        d_sw['cpydinm'] = True
        return

    @classmethod
    def vfy_regno(
            cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify Registration number
        """
        if not kwargs.get('sw_adm_vfy_regno', True):
            return
        _key = Cfg.Utils.evin_key_regno
        _val = Dic.get(d_evin, _key)
        if not _val:
            DoA.append_unique_by_key(doaod_vfy, cls.regno_is_empty, d_evin)
            d_sw['regno'] = False
            return
        d_sw['regno'] = True
        return

    @classmethod
    def vfy_coco(
            cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify Country Code
        """
        if not kwargs.get('sw_adm_vfy_coco', True):
            return
        _key: TnStr = Dic.get(d_evin, Cfg.Utils.evin_key_coco)
        if not _key:
            DoA.append_unique_by_key(doaod_vfy, cls.coco_is_empty, d_evin)
            d_sw['coco'] = False
            return
        else:
            import pycountry
            try:
                _country = pycountry.countries.get(alpha_2=_key.upper())
            except KeyError:
                DoA.append_unique_by_key(doaod_vfy, cls.coco_is_invalid, d_evin)
                d_sw['coco'] = False
                return
            return
        d_sw['coco'] = True
        return

    @classmethod
    def vfy_objectid(
            cls, d_sw: TyDoB, d_evin: TyDic,
            dod: TyDoD, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify Country Code
        """
        if not kwargs.get('sw_adm_vfy_objectid', True):
            return
        _key: TnStr = Cfg.Utils.evin_key_objectid
        _val = Dic.get(d_evin, _key)
        if not _val:
            DoA.append_unique_by_key(doaod_vfy, cls.objectid_is_empty, d_evin)
            d_sw['objectid'] = False
            return
        if kwargs.get('sw_adm_vfy_objectid_is_unique', True):
            if dod[_key][_val] > 1:
                DoA.append_unique_by_key(
                        doaod_vfy, cls.objectid_isnot_unique, d_evin)
                d_sw['objectid'] = False
                return
        d_sw['objectid'] = True
        return

    @classmethod
    def vfy_town(
            cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify Town by Country Code
        """
        if not kwargs.get('sw_adm_vfy_town', False):
            return
        _key_town: TnStr = Cfg.Utils.evin_key_town
        _town: TnStr = Dic.get(d_evin, _key_town)
        if not _town:
            DoA.append_unique_by_key(doaod_vfy, cls.town_is_empty, d_evin)
            d_sw['town'] = False
            return
        _key_coco: TyStr = Cfg.Utils.evin_key_coco
        if not kwargs.get('sw_adm_vfy_town_with_coco', False):
            return
        _coco: TnStr = Dic.get(d_evin, _key_coco)
        if not _coco:
            d_sw['town'] = True
            return
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut
        _geolocator = Nominatim(user_agent="geo_verifier")
        try:
            _location = _geolocator.geocode(_town)
        except GeocoderTimedOut:
            DoA.append_unique_by_key(doaod_vfy, cls.town_is_invalid, d_evin)
            d_sw['town'] = False
            return
        else:
            if _location is None:
                DoA.append_unique_by_key(doaod_vfy, cls.town_is_invalid, d_evin)
                d_sw['town'] = False
                return
            _address: TyStr = _location.address
            if _coco.lower() not in _address.lower():
                DoA.append_unique_by_key(doaod_vfy, cls.town_is_invalid, d_evin)
                d_sw['town'] = False
                return
            d_sw['town'] = True
            return

    @classmethod
    def vfy_poco(
            cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify Postal Code
        """
        if not kwargs.get('sw_adm_vfy_poco', True):
            return
        _key_poco: TyStr = Cfg.Utils.evin_key_poco
        _key_coco: TyStr = Cfg.Utils.evin_key_coco
        _poco: TnStr = d_evin.get(_key_poco)
        if not _poco:
            DoA.append_unique_by_key(doaod_vfy, cls.poco_is_empty, d_evin)
            d_sw['poco'] = False
            return
        _coco: TnStr = d_evin.get(_key_coco)
        from postal_codes_tools.postal_codes import verify_postal_code_format
        if not verify_postal_code_format(postal_code=_poco, country_iso2=_coco):
            DoA.append_unique_by_key(doaod_vfy, cls.poco_is_invalid, d_evin)
            d_sw['poco'] = False
            return
        d_sw['poco'] = True
        return

    @classmethod
    def vfy_d_evin(
            cls, d_evin: TyDic, dod, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> TyBool:
        if not kwargs.get('sw_adm_vfy', True):
            return True

        # Set verification summary switch
        _d_sw: TyDoB = {}

        # Verify DUNS
        cls.vfy_duns(_d_sw, d_evin, dod, doaod_vfy, kwargs)
        # Verify Company display name
        cls.vfy_cpydinm(_d_sw, d_evin, doaod_vfy, kwargs)
        # Verify Country display name
        cls.vfy_regno(_d_sw, d_evin, doaod_vfy, kwargs)
        # Verify Country Code
        cls.vfy_coco(_d_sw, d_evin, doaod_vfy, kwargs)
        # Verify ObjectID
        cls.vfy_objectid(_d_sw, d_evin, dod, doaod_vfy, kwargs)
        # Verify Town in Country
        cls.vfy_town(_d_sw, d_evin, doaod_vfy, kwargs)
        # Verify Postal Code
        cls.vfy_poco(_d_sw, d_evin, doaod_vfy, kwargs)

        _sw_adm_use_duns = kwargs.get('sw_adm_use_duns', True)
        if _sw_adm_use_duns:
            return _d_sw['duns'] and _d_sw['cpydinm'] and _d_sw['objectid']

        if (_d_sw['duns'] and _d_sw['cpydinm'] and _d_sw['objectid']) or \
           (_d_sw['regno'] and _d_sw['coco'] and _d_sw['cpydinm']) or \
           (_d_sw['cpynm'] and _d_sw['coco'] and _d_sw['cpydinm']):
            return True

        return False

    @staticmethod
    def sh_dod(
            aod_evin: TnAoD, kwargs: TyDic) -> TyDoD:
        _dod: TyDoD = {}
        if not aod_evin:
            return _dod
        _sw_adm_vfy_duns_is_unique = kwargs.get('sw_adm_vfy_duns_is_unique', True)
        _sw_adm_vfy_objectid_is_unique = kwargs.get(
                'sw_adm_vfy_objectid_is_unique', True)
        for _d_evin in aod_evin:
            if _sw_adm_vfy_duns_is_unique:
                _key = Cfg.Utils.evin_key_duns
                _val: TnStr = Dic.get(_d_evin, _key)
                if _key not in _dod:
                    _dod[_key] = {}
                if _val in _dod[_key]:
                    _dod[_key][_val] = _dod[_key][_val] + 1
                else:
                    _dod[_key][_val] = 1
            if _sw_adm_vfy_objectid_is_unique:
                _key = Cfg.Utils.evin_key_objectid
                _val = Dic.get(_d_evin, _key)
                if _key not in _dod:
                    _dod[_key] = {}
                if _val in _dod[_key]:
                    _dod[_key][_val] = _dod[_key][_val] + 1
                else:
                    _dod[_key][_val] = 1
        return _dod

    @classmethod
    def vfy_aod_evin(
            cls, aod_evin: TnAoD, kwargs: TyDic
    ) -> tuple[TyAoD, TyDoAoD]:
        _aod_evin: TyAoD = []
        _doaod_vfy: TyDoAoD = {}
        if not aod_evin:
            return _aod_evin, _doaod_vfy

        _dod = cls.sh_dod(aod_evin, kwargs)

        for _d_evin in aod_evin:
            _sw: bool = cls.vfy_d_evin(_d_evin, _dod, _doaod_vfy, kwargs)
            if _sw:
                _aod_evin.append(_d_evin)

        return _aod_evin, _doaod_vfy


class EvinVfyDel:
    """
    OmniTracker EcoVadis class
    """
    objectid_is_empty = 'del_wrn_objectid_is_empty'
    objectid_isnot_unique = 'del_err_objectid_is_not_unique'
    iq_id_is_empty = 'del_wrn_iq_id_is_empty'
    iq_id_isnot_unique = 'del_err_iq_id_is_not_unique'

    @classmethod
    def vfy_objectid(
            cls, d_sw: TyDoB, d_evin: TyDic,
            dod: TyDoD, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify Country Code
        """
        if not kwargs.get('sw_del_vfy_objectid', True):
            return
        _key: TnStr = Cfg.Utils.evin_key_objectid
        _val = Dic.get(d_evin, _key)
        if not _val:
            DoA.append_unique_by_key(doaod_vfy, cls.objectid_is_empty, d_evin)
            d_sw['objectid'] = False
            return
        if kwargs.get('sw_del_vfy_objectid_is_unique', False):
            if dod[_key][_val] > 1:
                DoA.append_unique_by_key(
                        doaod_vfy, cls.objectid_isnot_unique, d_evin)
                d_sw['objectid'] = False
            return
        d_sw['objectid'] = True
        return

    @classmethod
    def vfy_iq_id(
            cls, d_sw: TyDoB, d_evin: TyDic,
            dod: TyDoD, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> None:
        """
        Verify IQ_ID
        """
        if not kwargs.get('sw_del_vfy_iq_id', True):
            return
        _key = Cfg.Utils.evin_key_iq_id
        _val = Dic.get(d_evin, _key)
        if not _val:
            DoA.append_unique_by_key(doaod_vfy, cls.iq_id_is_empty, d_evin)
            d_sw['iq_id'] = False
            return
        if kwargs.get('sw_del_vfy_iq_id_is_unique', False):
            if dod[_key][_val] > 1:
                DoA.append_unique_by_key(doaod_vfy, cls.iq_id_isnot_unique, d_evin)
                d_sw['iq_id'] = False
            return
        d_sw['iq_id'] = True
        return

    @classmethod
    def vfy_d_evin(
            cls, d_evin: TyDic, dod: TyDoD, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> TyBool:
        if not kwargs.get('sw_del_vfy', True):
            return True

        # Set verification summary switch
        _d_sw: TyDoB = {}

        # Verify ObjectID
        cls.vfy_objectid(_d_sw, d_evin, dod, doaod_vfy, kwargs)
        # Verify EcoVadis IQ Id
        cls.vfy_iq_id(_d_sw, d_evin, dod, doaod_vfy, kwargs)

        if _d_sw['objectid'] or _d_sw['iq_id']:
            return True

        return False

    @staticmethod
    def sh_dod(
            aod_evin: TnAoD, kwargs: TyDic) -> TyDoD:
        _dod: TyDoD = {}
        if not aod_evin:
            return _dod
        _sw_adm_vfy_iq_id_is_unique = kwargs.get('sw_adm_vfy_iq_id_is_unique', True)
        _sw_adm_vfy_objectid_is_unique = kwargs.get(
                'sw_adm_vfy_objectid_is_unique', True)
        for _d_evin in aod_evin:
            if _sw_adm_vfy_iq_id_is_unique:
                _key = Cfg.Utils.evin_key_iq_id
                _val: TnStr = Dic.get(_d_evin, _key)
                if _key not in _dod:
                    _dod[_key] = {}
                if _val in _dod[_key]:
                    _dod[_key][_val] = _dod[_key][_val] + 1
                else:
                    _dod[_key][_val] = 1
            if _sw_adm_vfy_objectid_is_unique:
                _key = Cfg.Utils.evin_key_objectid
                _val = Dic.get(_d_evin, _key)
                if _key not in _dod:
                    _dod[_key] = {}
                if _val in _dod[_key]:
                    _dod[_key][_val] = _dod[_key][_val] + 1
                else:
                    _dod[_key][_val] = 1
        return _dod

    @classmethod
    def vfy_aod_evin(
            cls, aod_evin: TnAoD, kwargs: TyDic
    ) -> tuple[TyAoD, TyDoAoD]:
        _aod_evin: TyAoD = []
        _doaod_vfy: TyDoAoD = {}
        if not aod_evin:
            return _aod_evin, _doaod_vfy

        _dod = cls.sh_dod(aod_evin, kwargs)

        for _d_evin in aod_evin:
            _sw: bool = cls.vfy_d_evin(_d_evin, _dod, _doaod_vfy, kwargs)
            if _sw:
                _aod_evin.append(_d_evin)

        return _aod_evin, _doaod_vfy
