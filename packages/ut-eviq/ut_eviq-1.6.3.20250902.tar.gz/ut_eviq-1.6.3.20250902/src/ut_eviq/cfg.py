"""
This module provides configuration classes for the management of Sustainability Ris Rating processing.
"""
from typing import Any

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]


class Cfg:

    class Utils:

        d_ecv_iq2umh_iq = {
            'Sehr niedrig': '1',
            'Niedrig': '2',
            'Mittelniedrig': '3',
            'Mittelhoch': '4',
            'Hoch': '4',
            'Sehr hoch': '4',
            'Undefiniert': '4',
        }

        evin_key_coco = 'Landesvorwahl'
        evin_key_cpydinm = 'Anzeigename des Unternehmens (Ihr Name)'
        evin_key_cpynm = 'Anzeigename des Unternehmens (Ihr Name)'
        evin_key_duns = 'DUNS-Nummer'
        evin_key_iq_id = 'IQ-ID'
        evin_key_objectid = 'Eindeutige ID'
        evin_key_poco = 'Postleitzahl'
        evin_key_town = 'Stadt'
        evin_key_regno = 'Steuer-ID oder andere Identifikationsnummer'

        evex_key_coco = 'Land'

        a_evin_key: TyArr = [
            'DUNS-Nummer',
            'Steuer-ID',
            'Umsatzsteuer-ID',
            'Handelsregister-Nr',
            'Offizieller Name des Unternehmens',
            'LEI'
        ]

        d_evin2evex_keys: TyDic = {
            'DUNS-Nummer': 'DUNS-Nummer',
            'Steuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
            'Umsatzsteuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
            'Handelsregister-Nr': 'Steuer-ID oder andere Identifikationsnummer',
            'Offizieller Name des Unternehmens': 'Name des Unternehmens',
            'LEI': 'Steuer-ID oder andere Identifikationsnummer',
            'Eindeutige ID': 'Eindeutige ID'
        }

        d_evex2evin_keys: TyDic = {
            'Eindeutige ID': 'Eindeutige ID',
            'IQ-ID': 'IQ-ID'
        }

        d_evup_en2de: TyDic = {
            "UniqueId": "Eindeutige ID",
            "CompanyDisplayName": "Anzeigename des Unternehmens (Ihr Name)",
            "CompanyName": "Offizieller Name des Unternehmens",
            "CriticalityScale": "ScaleAbc",
            "CriticalityLevel": "Kritikalitätsstufe",
            "SpendScale": "ScaleAbc",
            "SpendLevel": "Spend Level",
            "DunsNumber": "DUNS-Nummer",
            "RegistrationNumber": "Steuer-ID oder andere Identifikationsnummer",
            "CountryCode": "Landesvorwahl",
            "Tags": "Tags",
            "contactFirstName": "Vorname des Ansprechpartners beim Unternehmen",
            "contactLastName": "Nachname des Ansprechpartners beim Unternehmen",
            "contactEmail": "Kontakt-Telefonnummer für das Unternehmen",
        }

        d_evup2const: TyDic = {

            'Anzeigename des Unternehmens (Ihr Name)': None,
            'DUNS-Nummer': '',
            'Steuer-ID oder andere Identifikationsnummer': '',
            'Offizieller Name des Unternehmens': '',

            'Landesvorwahl': '',
            'Postleitzahl': '',
            'Stadt': '',
            'Adresse': '',
            'Eindeutige ID': '',
            'IQ-ID': '',
            'Kritikalitätsstufe': '',
            'Spend Level': '',

            'Vorname des Ansprechpartners beim Unternehmen': '',
            'Nachname des Ansprechpartners beim Unternehmen': '',
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen': '',
            'Kontakt-Telefonnummer für das Unternehmen': '',
            'E-Mail der anfordernden Kontaktperson': '',

            'Tags': 'Union Investment 2024; KRG'
        }

        doaod_evup2evin_keys: TyDoAoD = {
            'id1': [
                {
                    'DUNS-Nummer': 'DUNS-Nummer'
                }
            ],
            'id2': [
                {
                    'Steuer-ID oder andere Identifikationsnummer': 'Steuer-ID',
                    'Landesvorwahl': 'Landesvorwahl'
                },
                {
                    'Steuer-ID oder andere Identifikationsnummer': 'Umsatzsteuer-ID',
                    'Landesvorwahl': 'Landesvorwahl',
                    'Postleitzahl': 'Postleitzahl',
                    'Stadt': 'Stadt',
                    'Adresse': 'Adresse',
                },
                {
                    'Steuer-ID oder andere Identifikationsnummer': 'Handelsregister-Nr',
                    'Landesvorwahl': 'Landesvorwahl',
                    'Postleitzahl': 'Postleitzahl',
                    'Stadt': 'Stadt',
                    'Adresse': 'Adresse',
                },
                {
                    'Steuer-ID oder andere Identifikationsnummer': 'LEI',
                    'Landesvorwahl': 'Landesvorwahl',
                    'Postleitzahl': 'Postleitzahl',
                    'Stadt': 'Stadt',
                    'Adresse': 'Adresse',
                }
            ],
            'id3': [
                {
                    'Offizieller Name des Unternehmens': 'Offizieller Name des Unternehmens',
                    'Landesvorwahl': 'Land',
                    'Postleitzahl': 'Postleitzahl',
                    'Stadt': 'Stadt',
                    'Adresse': 'Adresse',
                }
            ]
        }

        d_evup2evin_nonkeys: TyDic = {
            'Landesvorwahl': 'Landesvorwahl',
            'Postleitzahl': 'Postleitzahl',
            'Stadt': 'Stadt',
            'Adresse': 'Adresse',
            'Eindeutige ID': 'Eindeutige ID',
            'Anzeigename des Unternehmens': 'Anzeigename des Unternehmens',
            'Offizieller Name des Unternehmens': 'Offizieller Name des Unternehmens'
        }

        d_evup2evin_plz_ort_strasse: TyDic = {
            'Postleitzahl': 'Postleitzahl',
            'Stadt': 'Stadt',
            'Adresse': 'Adresse',
        }

        a_evup_key: TyArr = [
            'DUNS-Nummer',
            'Steuer-ID oder andere Identifikationsnummer',
            'Offizieller Name des Unternehmens'
        ]

        d_del_evup2evex: TyDic = {
            'Eindeutige ID': 'Eindeutige ID',
            'IQ-ID': 'IQ-ID',
        }

        d_evup2evex: TyDic = {
            'Anzeigename des Unternehmens (Ihr Name)': 'Name des Unternehmens',
            'Spend Level': 'Spend Level',
            'Kritikalitätsstufe': 'Kritikalitätsstufe',
            'DUNS-Nummer': 'DUNS-Nummer',
            'Steuer-ID oder andere Identifikationsnummer': 'Steuer-ID oder andere Identifikationsnummer',
            'Landesvorwahl': 'Land',
            'Tags': 'Tags',
            'Vorname des Ansprechpartners beim Unternehmen': 'Vorname des Ansprechpartners beim Unternehmen',
            'Nachname des Ansprechpartners beim Unternehmen': 'Nachname des Ansprechpartners beim Unternehmen',
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen': 'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
            'Kontakt-Telefonnummer für das Unternehmen': 'Kontakt-Telefonnummer für das Unternehmen',
            'E-Mail der anfordernden Kontaktperson': 'E-Mail der anfordernden Kontaktperson',
            'IQ-ID': 'IQ-ID',
            'Eindeutige ID': 'Eindeutige ID'
        }

        d_evup2evin: TyDic = {
            'Anzeigename des Unternehmens (Ihr Name)': 'Anzeigename des Unternehmens (Ihr Name)',
            'DUNS-Nummer': 'DUNS-Nummer',
            'Offizieller Name des Unternehmens': 'Offizieller Name des Unternehmens',

            'Landesvorwahl': 'Landesvorwahl',
            'Postleitzahl': 'Postleitzahl',
            'Stadt': 'Stadt',
            'Adresse': 'Adresse',
            'Eindeutige ID': 'Eindeutige ID',
        }

        d_evin2evex: TyDic = {
            'IQ-ID': 'IQ-ID',
            'Kritikalitätsstufe': 'Kritikalitätsstufe',
            'Spend Level': 'Spend Level',

            'Vorname des Ansprechpartners beim Unternehmen': 'Vorname des Ansprechpartners beim Unternehmen',
            'Nachname des Ansprechpartners beim Unternehmen': 'Nachname des Ansprechpartners beim Unternehmen',
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen': 'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
            'Kontakt-Telefonnummer für das Unternehmen': 'Kontakt-Telefonnummer für das Unternehmen',
            'E-Mail der anfordernden Kontaktperson': 'E-Mail der anfordernden Kontaktperson',
            'Tags': 'Tags'
        }

        d_evin2evup: TyDic = {
            'Offizieller Name des Unternehmens': 'Offizieller Name des Unternehmens',
            'DUNS-Nummer': 'DUNS-Nummer',
            'Steuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
            'Landesvorwahl': 'Landesvorwahl',
            'Eindeutige ID': 'Eindeutige ID'
        }

        d_evex2evin: TyDic = {
            'IQ-ID': 'IQ-ID',
            'Kritikalitätsstufe': 'Kritikalitätsstufe',
            'Spend Level': 'Spend Level',

            'Vorname des Ansprechpartners beim Unternehmen': 'Vorname des Ansprechpartners beim Unternehmen',
            'Nachname des Ansprechpartners beim Unternehmen': 'Nachname des Ansprechpartners beim Unternehmen',
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen': 'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
            'Kontakt-Telefonnummer für das Unternehmen': 'Kontakt-Telefonnummer für das Unternehmen',
            'E-Mail der anfordernden Kontaktperson': 'E-Mail der anfordernden Kontaktperson',
            'Tags': 'Tags'
        }
