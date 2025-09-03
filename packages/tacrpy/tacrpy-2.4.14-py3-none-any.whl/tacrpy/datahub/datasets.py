"""Soubor funkcí, které slouží k vytváření podkladů pro DataHub a k nahrávání dat přes API \
včetně checků vyplněných údajů.
"""

import pandas as pd
import os
import copy
import datetime

from enum import Enum
import typing

# template pro přidání fieldů
FIELD_TEMPLATE = {
    'fieldPath': str(),  # název pole, odpovídá názvu sloupce v DB, pro etalon anglický název
    'nullable': None,  # hodnoty nemusí být ve slouci vyplněny - True/False
    'description': None,  # popis pole, co daný sloupec reprezentuje, pro etalon může být český ekvivalent názvu
    'type': {
        # specifický datový typ DataHub - za tečkou Nulltype, pokud chceme pouze klasické datové typy
        # com.linkedin.pegasus2avro.schema.NullType
        # BooleanType, FixedType, StringType, BytesType, NumberType, DateType, TimeType,
        # EnumType, MapType, ArrayType, UnionType, RecordType
        'type': {
            "com.linkedin.pegasus2avro.schema.NullType": {}
        }
    },
    # klasický datový typ - string, date, integer atd.
    'nativeDataType': None,
}

# template pro jeden dataset
DATASET_TEMPLATE = {
    "auditHeader": None,
    "proposedSnapshot": {
        "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot": {
            # vloží (vytvoří) strukturu, kde se má dataset nacházet
            # dataPlatform - PostgreSQL, MySQL, Hive ... i "vlastní" platformy - Etalon
            # struktura v rámci platformy DB.schema.dataset
            # např. promo--rejstrik.public.rejstrik_entity
            # prostředí PROD, PROMO, TEST atd.
            # pro etalony vkládat rovnou do platformy bez struktury
            # urn:li:dataPlatform:etalon,odhad,PROD
            "urn": str(),
            # základní informace o data setu, struktura datasetu, vlastníci, dokumentace atd.
            "aspects": [
                {
                    "com.linkedin.pegasus2avro.dataset.DatasetProperties": {
                        "description": None,
                        "uri": None,
                        "tags": [],
                        "customProperties": {},
                        "name": str()  # nastaví název, který se jinak generuje ze schemaName
                    }
                },
                {
                    "com.linkedin.pegasus2avro.schema.SchemaMetadata": {
                        # v GUI se rálně nezobrazuje, v GUI název odpovídá struktuře v rámci platformy
                        "schemaName": str(),
                        "platform": "urn:li:dataPlatform:etalon",
                        "version": 0,
                        "hash": "",  # nevím k čemu, ale bez toho to nefunguje
                        "platformSchema": {  # nevím k čemu, ale bez toho to nefunguje
                            "com.linkedin.pegasus2avro.schema.OtherSchema": {
                                "rawSchema": ""
                            }
                        },
                        "fields": None,  # sloupce v tabulce (datasetu)
                        "foreignKeys": None  # cizí klíče a odkaz na tabulky (datasety) cizích klíčů
                    }
                }
            ]
        }
    }
}

# template pro přidání cizích klíčů
FOREIGN_KEYS_TEMPLATE = {
    "name": None,
    "foreignFields": [],  # list fieldů v cizím datasetu, na které se má vytvořit vazba
    "sourceFields": [],  # list fieldů ve zdrojovém datasetu, pro které se má vytvořit vazba
    "foreignDataset": str()  # URN cizího datasetu, na který se odkazujeme
}


class OwnerType(Enum):
    DATA_STEWARD = 'Data Steward'
    TECHNICAL_OWNER = 'Technical Owner'
    BUSINESS_OWNER = 'Business Owner'


def _create_fields(entity_dict: list[dict], nested_fields: bool) -> list[dict]:
    """Vytvoří záznamy pro jednotlivé fieldy v datasetu na základě šablony.

    V případě, že dataset (datová entita) obsahuje nested fields, pak volá funkci (_create_nested_fields),
    která vytvoří jejich technický název. (do formátu nested_field.field, nested_field.other_nested_field.field).

    :param entity_dict: dict datové entity, který obsahuje jednotlivé fieldy a další informace fieldů
    :param nested_fields: informace, jestli dataset obsahuje vnořené fieldy (nested fields)
    :return: list dictů jednotlivých fieldů
    """

    all_fields = []

    for field in entity_dict:
        field_dict = FIELD_TEMPLATE.copy()

        if nested_fields:
            if pd.isnull(field['upstream_lineage']):
                field_dict['fieldPath'] = field['field_name']
            else:
                field_dict['fieldPath'] = _create_nested_field(field['field_name']
                                                               , field['upstream_lineage'])
        else:
            field_dict['fieldPath'] = field['field_name']

        field_dict['description'] = field['field_description']
        field_dict['nativeDataType'] = field['field_data_type']

        all_fields.append(field_dict)

    return all_fields


def _create_nested_field(field_name: str, upstream_lineage: str) -> str:
    """Vytvoří složený název pro nested fields.

    Obecně slouží pro funkcionalitu rozbalování a zobrazení vnořených polí (nested fields) v DataHub.
    Nejvyšší nested field -> nižší nested field -> technický název fieldů.
    Formát - nested_field.field, nested_field.other_nested_field.field

    :param field_name: technický název fieldů
    :param upstream_lineage: seznam nested fieldů, ve kterých se field zobrazí. Odělené středníkem
    :return: složený název fieldů (Formát - nested_field.field, nested_field.other_nested_field.field)
    """

    upstream_lineage_list = upstream_lineage.split(';')
    upstream_lineage = '.'.join(upstream_lineage_list)
    if field_name in upstream_lineage_list:
        field_name = upstream_lineage

    else:
        field_name = f'{upstream_lineage}.{field_name}'
    return field_name


def _create_foreign_keys(entity_dict: list[dict], urn: str, platform: str) -> list[dict]:
    """Vytvoří odkaz na jiné datasety skrze cizí klíče (foreign keys) na základě šablony.

    Funkce vytvoří potřebné URN datasetů a fieldů. V současné chvíli je možné přiřadit pouze
    jeden foreign key k jednomu fieldu.

    :param entity_dict: dict datové entity, který obsahuje jednotlivé fieldy a další informace fieldů
    :param urn: URN zdrojového datasetu
    :param platform: název platformy, která je zdrojem datasetu
                     (např. etalon, googlesheets, ISTA, Postgres, OpenAPI...)
    :return: list dictů jednotlivých cizích klíčů (foreign keys)
    """

    foreign_keys = []

    for field in entity_dict:
        if pd.isnull(field['foreign_key']):
            pass
        else:
            fk_dict = FOREIGN_KEYS_TEMPLATE.copy()
            fk_dict['name'] = field['field_name']

            if pd.isnull(field['upstream_lineage']):
                fieldPath = field['field_name']
            else:
                fieldPath = _create_nested_field(field['field_name'], field['upstream_lineage'])

            foreign_dataset_name = '_'.join(field['foreign_key'].lower().split(' '))
            foreign_dataset_urn = f'urn:li:dataset:(urn:li:dataPlatform:{platform},{foreign_dataset_name},PROD)'
            foreign_field_urn = f'urn:li:schemaField:({foreign_dataset_urn},Entity Id)'
            source_urn = f'urn:li:schemaField:({urn},{fieldPath})'

            fk_dict['foreignFields'] = [foreign_field_urn]
            fk_dict['sourceFields'] = [source_urn]
            fk_dict['foreignDataset'] = foreign_dataset_urn

            foreign_keys.append(fk_dict)

    return foreign_keys


def _create_dataset(entity: str, platform: str, entity_dict: list[dict]
                    , nested_fields: bool, foreign_keys: bool, subfolder: str = None) -> dict:
    """ Doplní template dictu datasetu o potřebné atributy a objekty.

    Vytvoří urn (ID) datasetu na základě jmenné konvence.
    Volá interní funkce pro vytvoření záznamů jednoltivých fieldů (_create_fields) \
    a přiřazení cizích klíčů (_create_foreign_keys).

    :param entity: název datové entity (datasetu)
    :param platform: název platformy, která je zdrojem datasetu
                     (např. etalon, googlesheets, ISTA, Postgres, OpenAPI...)
    :param entity_dict: dict datové entity, který obsahuje jednotlivé fieldy a další informace fieldů
    :param nested_fields: informace, jestli dataset obsahuje vnořené fieldy (nested fields)
    :param foreign_keys: informace, jestli dataset obsahuje cizí klíče (foreign keys)
    :param subfolder: podsložka, v rámci které má být dataset uložený
    :return: dict reprezentace datové entity (datasetu), včetně fieldů a cizích klíčů
    """

    dataset = DATASET_TEMPLATE.copy()

    if subfolder is None:
        entity_name = entity
    else:
        entity_name = f'{subfolder}.{entity}'

    urn = f"urn:li:dataset:(urn:li:dataPlatform:{platform},{entity_name},PROD)"

    fields = _create_fields(entity_dict, nested_fields)

    if foreign_keys:
        foreign_keys_list = _create_foreign_keys(entity_dict, urn, platform)
    else:
        foreign_keys_list = None

    level1 = 'proposedSnapshot'
    level2 = 'com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot'

    level4a = 'com.linkedin.pegasus2avro.dataset.DatasetProperties'
    level4b = 'com.linkedin.pegasus2avro.schema.SchemaMetadata'

    dataset[level1][level2]['aspects'][0][level4a]['name'] = entity

    dataset[level1][level2]['urn'] = urn
    dataset[level1][level2]['aspects'][1][level4b]['schemaName'] = entity_name
    dataset[level1][level2]['aspects'][1][level4b]['platform'] = f'urn:li:dataPlatform:{platform}'
    dataset[level1][level2]['aspects'][1][level4b]['fields'] = fields
    dataset[level1][level2]['aspects'][1][level4b]['foreignKeys'] = foreign_keys_list

    return dataset


def create_etalon(etalon_df: pd.DataFrame, etalon_name: str, platform: str
                  , nested_fields: bool, foreign_keys: bool, subfolder: str = None) -> dict[str, any]:
    """
    Vytvoří dict datasetu k importu do DataHub pro jednu datovou entitu.

    Z načteného souboru získá, případně vytvoří potřebné informace k vytvoření informací o datasetu.
    Název entity získává z názvu souboru => v názvu souboru musí být název entity.

    Povinné sloupce v načteném souboru:

     * field_name
     * field_description
     * field_data_type

     Volitelné sloupce:

     * upstream_lineage
     * foreign_key

    :param etalon_df: zdrojový dataframe s informacemi o etalonu
    :param etalon_name: název etalonu
    :param platform: název platformy, která je zdrojem datasetu
                     (např. etalon, googlesheets, ISTA, Postgres, OpenAPI...)
    :param nested_fields: informace, jestli dataset obsahuje vnořené fieldy (nested fields)
    :param foreign_keys: informace, jestli dataset obsahuje cizí klíče (foreign keys)
    :param subfolder: podsložka, v rámci které má být dataset uložený
    :return: etalon ve formě dict, které je možné převést do JSON a importovat do DataHub
    """
    entity_dict = etalon_df.to_dict('records')

    etalon = _create_dataset(etalon_name, platform, entity_dict, nested_fields, foreign_keys, subfolder)

    return etalon 


def create_etalon_bulk(etalon_df: pd.DataFrame, platform: str
                       , nested_fields: bool, foreign_keys: bool, subfolder: str = None) -> list[dict[str, any]]:
    """
    Vytvoří dict datasetu k importu do DataHub pro více datových entit.

    Z načteného souboru získá, případně vytvoří potřebné informace k vytvoření informací o datasetu.
    Název entity získává ze sloupce entity_name, ten slouží i k filtrování jednotlivých entit
    a jejich následné zpracování.

    Povinné sloupce v načteném souboru:

     * entity_name
     * field_name
     * field_description
     * field_data_type

     Volitelné sloupce:

     * upstream_lineage
     * foreign_key

    :param etalon_df: zdrojový dataframe s informacemi o etalonu
    :param platform: název platformy, která je zdrojem datasetu
                     (např. etalon, googlesheets, ISTA, Postgres, OpenAPI...)
    :param nested_fields: informace, jestli dataset obsahuje vnořené fieldy (nested fields)
    :param foreign_keys: informace, jestli dataset obsahuje cizí klíče (foreign keys)
    :param subfolder: podsložka, v rámci které má být dataset uložený
    :return: etalon ve formě dict, které je možné převést do JSON a importovat do DataHub
    """
    etalon_list = []

    for entity in etalon_df['entity_name'].unique():
        entity_df = etalon_df[etalon_df['entity_name'] == entity]
        entity_df = entity_df.drop(columns=['entity_name'])

        entity_dict = entity_df.to_dict('records')

        entity_name = '_'.join(entity.lower().split(' '))
        etalon = _create_dataset(entity_name, platform, entity_dict, nested_fields, foreign_keys, subfolder)
        etalon_list.append(copy.deepcopy(etalon))

    return etalon_list


def dataset_description(urn: str, description: str) -> list[dict[str, any]]:
    """ Vytvoří JSON pro přiřazení popisu datové sady k existující datové sadě.

    :param urn: URN existujícího datasetu, ve kterém se mají vytvořit/upravit údaje
    :param description: popis datasetu
    :return: list dictů s potřebnými informace k nahrání do DataHub
    """
    json_data = [{
        'entityType': 'dataset',
        'entityUrn': urn,
        'aspect': {
            '__type': 'EditableDatasetProperties',
            'description': description
        }
    }]
    return json_data


def dataset_link(urn: str, link_name: str, link_url: str, corpuser: str) -> list[dict[str, any]]:
    """ Vytvoří JSON pro přiřazení odkazů k existujícímu datasetu.

    V současné chvíli funguje pouze pro jeden odkaz.

    :param urn: URN existujícího datasetu, ve kterém se mají vytvořit/upravit údaje
    :param link_name: zobrazený název odkazu
    :param link_url: odkaz ve formátu url
    :param corpuser: uživatel, který odkaz vytvořil (ve formátu jmeno.prijmeni, bez diakritiky)
    :return: list dictů s potřebnými informace k nahrání do DataHub
    """
    dt = datetime.datetime.now()
    ts = int(datetime.datetime.timestamp(dt) * 1000)

    corpuser_urn = f'urn:li:corpuser:{corpuser}'
    json_data = [{
        'entityType': 'dataset',
        'entityUrn': urn,
        'aspect': {
            '__type': 'InstitutionalMemory',
            'elements': [
                {
                    'url': link_url,
                    'description': link_name,
                    'createStamp': {
                        'time': ts,
                        'actor': corpuser_urn
                    }
                }
            ]
        }
    }]
    return json_data


def dataset_ownership(urn: str, corpuser: str, owner_type: OwnerType) -> list[dict[str, any]]:
    """ Vytvoří JSON pro přiřazení vlastníka k existujícímu datasetu.

    V současné chvíli funguje pouze pro jednoho vlastníka.

    :param urn: URN existujícího datasetu, ve kterém se mají vytvořit/upravit údaje
    :param corpuser: uživatel, který se má přiřadit jako vlastník datasetu (ve formátu jmeno.prijmeni, bez diakritiky)
    :param owner_type: typ vlastníka (DATA_STEWARD, TECHNICAL_OWNER, BUSINESS_OWNER)
    :return: list dictů s potřebnými informace k nahrání do DataHub
    """

    corpuser_urn = f'urn:li:corpuser:{corpuser}'
    json_data = [{
        'entityType': 'dataset',
        'entityUrn': urn,
        'aspect': {
            '__type': 'Ownership',
            'owners': [
                {
                    'owner': corpuser_urn,
                    'type': owner_type,
                }
            ]
        }
    }]
    return json_data


def dataset_tag(urn: str, tags: list[str]) -> list[dict[str, any]]:
    """ Vytvoří JSON pro přiřazení tagu/tagů k existujícímu datasetu.

    :param urn: URN existujícího datasetu, ve kterém se mají vytvořit/upravit údaje
    :param tags: list tagů, které se mají přiřadit k datasetu
    :return: list dictů s potřebnými informace k nahrání do DataHub
    """

    tag_urns = [f'urn:li:tag:{tag}' for tag in tags]
    json_data = [{
        'entityType': 'dataset',
        'entityUrn': urn,
        'aspect': {
            '__type': 'GlobalTags',
            'tags': [
                {'tag': tag_urn} for tag_urn in tag_urns
            ]
        }
    }]
    return json_data
