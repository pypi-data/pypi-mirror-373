from typing import Any

# import pandas as pd
import openpyxl as op

from ut_dic.dic import Dic
from ut_http.httpx_ import Request
# from ut_xls.wbop import WbOp
# from ut_xls.ioipathnm import IoiPathnmWbOp as IoiWbOp
# from ut_xls.ioowbpe import IooPathnmWbPe as IooWbPe
# from ut_xls.ioowbop import IooPathnmWbOp as IooWbOp

from ut_eviq.cfg import Cfg

TyWbOp = op.Workbook

TyAny = Any
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoD = dict[Any, TyDic]
TyCmd = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnWbOp = None | TyWbOp


class Url:

    @classmethod
    def sh_base(cls, kwargs: TyDic) -> TyStr:
        _cfg = kwargs.get('Cfg', Cfg)
        _url_version: TyStr = kwargs.get('url_version', _cfg.url_version)
        _url_type: TyStr = kwargs.get('url_type', 'sandbox')
        _url: TyStr = _cfg.d_url[_url_type]['url']
        return f"{_url}://{_url_version}"


class EvToken:

    @staticmethod
    def get(kwargs: TyDic) -> TyAny:
        _base_url = Url.sh_base(kwargs)
        _url = f"{_base_url}/EVToken"
        _headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
        }
        _url_user = kwargs.get('url_user')
        _url_password = kwargs.get('url_password')
        _params = {
                'grant_type': 'password',
                'username': _url_user,
                'password': _url_password
        }
        return Request.get(_url, headers=_headers, params=_params)


class IqPartners:
    url_get_partner = "IqPartners/GetPartnerByUniqueId"
    url_upd_partner = "IqPartners/UpdatePartner"
    url_get_status = "IqPartners/GetOperationStatus"

    @staticmethod
    def sh_headers(
            d_response_evtoken: TyDic, dic: TyDic, kwargs: TyDic) -> TyDic:
        _access_token = d_response_evtoken['json']['access_token']
        # _token_type = d_response_evtoken['json']['token_type']
        return {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {_access_token}"
        }

    @staticmethod
    def sh_params_unqid(dic: TyDic, kwargs: TyDic) -> TyDic:
        return {'UniqueId': dic.get('Eindeutige ID')}

    @staticmethod
    def sh_params_opid(dic: TyDic, kwargs: TyDic) -> TyDic:
        return {'operationId': dic.get('operationId')}

    @classmethod
    def export(
            cls, d_response_evtoken: TyDic, dic: TyDic, kwargs: TyDic) -> TyAny:
        return Request.get(
                f"{Url.sh_base(kwargs)}/{cls.url_get_partner}",
                headers=cls.sh_headers(d_response_evtoken, dic, kwargs),
                params={'UniqueId': dic.get('Eindeutige ID')})

    @classmethod
    def upsert(
            cls, d_response_evtoken: TyDic, dic: TyDic, kwargs: TyDic) -> TyAny:
        return Request.get(
                f"{Url.sh_base(kwargs)}/{cls.url_upd_partner}",
                headers=cls.sh_headers(d_response_evtoken, dic, kwargs),
                params={},
                data={})

    @classmethod
    def getoperationstatus(
            cls, d_response_evtoken: TyDic, dic: TyDic, kwargs: TyDic) -> TyAny:
        return Request.get(
                f"{Url.sh_base(kwargs)}/{cls.url_get_status}",
                headers=cls.sh_headers(d_response_evtoken, dic, kwargs),
                params={},
                data={})

    @classmethod
    def upsert_aod_adm(cls, aod_evup_adm: TyAoD,  kwargs: TyDic) -> TyAoD:
        """
        EcoVadus Upload Processing:
        Administration (create, update) of partners using the Rest API
        """
        _aod: TyAoD = []
        _d_resp_evtoken: TyDic = EvToken.get(kwargs)
        for _dic in aod_evup_adm:
            _dod_resp: TyDoD = cls.upsert(_d_resp_evtoken, _dic, kwargs)
            _d_resp_dict: TyDic = _dod_resp.get('dict', {})
            _a_errorlist: TyArr = _d_resp_dict.get('ErrorList', [])
            if not _a_errorlist:
                return _aod
            while True:
                _d_resp_evtoken = IqPartners.getoperationstatus(
                        _d_resp_evtoken, _dic, kwargs)
            if not _d_resp_dict:
                _aod.append(_d_resp_dict)
        return _aod

    @classmethod
    def upsert_aod_del(cls, aod_evup_del: TyAoD,  kwargs: TyDic) -> TyAoD:
        """
        EcoVadus Upload Processing:
        Deletion of partners using the Rest API
        """

        _aod: TyAoD = []
        if aod_evup_del is None:
            return _aod

        _d_resp_evtoken: TyDic = EvToken.get(kwargs)
        for _dic in aod_evup_del:
            _dod_resp: TyDoD = IqPartners.upsert(_d_resp_evtoken, _dic, kwargs)
            _d_resp_dict: TyDic = _dod_resp.get('dict', {})
            if not _d_resp_dict:
                _aod.append(_d_resp_dict)
        return _aod

    @classmethod
    def upsert_aod_reg(
            cls, aod_evup_adm: TyAoD, aod_evup_del: TyAoD,  kwargs: TyDic) -> TyAoD:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using the Rest API
        """
        _aod: TyAoD = []
        _d_resp_evtoken: TyDic = EvToken.get(kwargs)
        for _dic in aod_evup_adm:
            _dod_resp: TyDoD = IqPartners.upsert(_d_resp_evtoken, _dic, kwargs)
            _d_resp_dict: TyDic = _dod_resp.get('dict', {})
            if not _d_resp_dict:
                _aod.append(_d_resp_dict)

        if aod_evup_del is None:
            return _aod

        for _dic in aod_evup_del:
            _dod_resp = IqPartners.upsert(_d_resp_evtoken, _dic, kwargs)
            _d_resp_dict = _dod_resp.get('dict', {})
            if not _d_resp_dict:
                _aod.append(_d_resp_dict)

        return _aod

    @classmethod
    def evdoexp(cls, aod_evup_adm: TyAoD, kwargs: TyDic) -> TyAoD:
        """
        EcoVadus Download Processing:
        Export EcoVadis data with the Rest API
        """
        _aod: TyAoD = []
        _cfg = kwargs.get('Cfg', Cfg)
        _d_resp_evtoken: TyDic = EvToken.get(kwargs)
        for _dic in aod_evup_adm:
            _dod_resp: TyDoD = IqPartners.upsert(_d_resp_evtoken, _dic, kwargs)
            _d_resp_dict_en = _dod_resp.get('dict', {})
            _d_resp_dict_de = Dic.change_keys_by_dic(_d_resp_dict_en, _cfg.d_evup_en2de)
        return _aod
