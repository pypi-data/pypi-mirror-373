"""Soubor dílčích a agregujících funkcí sloužících k vytváření nových pojmů v DataHubu skrze API post."""

import uuid
from unidecode import unidecode
import numpy as np
import datetime
import pandas as pd
from tacrpy.datahub.openapi import post_data
from tacrpy.datahub.import_checks import (is_column_filled, has_specific_values, contains_boolean_values,
                                          no_duplicates_in_column, is_column_list_of_dicts)


def _preprocess_regs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Specifická pomocná dílčí funkce k preprocessingu tabulky se souhrnem vnitřních předpisů.

    :param df: pd.DataFrame se souhrnem vnitřních předpisů
    :return: pd.DataFrame k využití v dalších krocích modulu
    """

    df.columns = df.iloc[0]
    df = df.iloc[1:]
    df['Verze'] = df['Verze'].astype(str)
    df1 = df.dropna(subset=['Odkaz'])
    df1['verze_s'] = ('v' + df1['Verze'])
    df1['předpis_full'] = df1['ID předpisu'] + ' ' + df1['Název vnitřního předpisu'] + ' ' + df1['verze_s']
    links = df1[['ID předpisu', 'předpis_full', 'Odkaz']]
    return links


def records_into_rows(df: pd.DataFrame, key_column: object, parse_column: object, separator: any) -> pd.DataFrame:
    """
    Dílčí funkce, která rozparsuje buňky v cílovém sloupci s více záznamy do jednotlivých řádků (na základě separátoru),
    přičemž je zachována příslušnost k hlavnímu klíči.

    :param df: název pd.DataFrame, v rámci kterého chci danou funkci použít
    :param key_column: název sloupce s klíčem/ID, ke kterému chci rozparsované záznamy vztáhnout
    :param parse_column: název sloupce, v rámci kterého chci záznamy rozparsovat do řádků
    :param separator: volba separátoru, kterým jsou jednotlivé záznamy v buňce odděleny
    :return: pd.DataFrame obsahující sloupec s rozparsovanými záznamy a klíč, ke kterému se dané záznamy vztahují
    """

    df[parse_column] = df[parse_column].astype(str)
    new_rows = []
    for index, row in df.iterrows():
        records = row[parse_column].split(separator)
        for record in records:
            new_rows.append({key_column: row[key_column], parse_column: record})

    split_df = pd.DataFrame(new_rows)
    split_df[parse_column] = split_df[parse_column].str.lstrip()
    split_df = split_df[split_df[parse_column] != '']
    return split_df


def _add_owners_urn(df: pd.DataFrame, dh_users: pd. DataFrame, name_column: object,
                    separator: any, owner_type: str) -> pd.DataFrame:
    """
    Pomocná dílčí funkce zpracující formát, ve kterém jsou vlastníci pojmů vedeni ve zdrojovém souboru,
    a vytvoří klíč na základě kterého jsou vlastníkům následně přiřazeny jejich urns v souladu s účty v datahubu.

    :param df: pd.DataFrame obsahující sloupec s rozparsovanými vlastníky pojmů
    :param dh_users: pd.DataFrame obsahující seznam urn existujících uživatelů v datahubu
    :param name_column: název sloupce obsahující jméno a příjmení vlastníka pojmu ve formátu "příjmení, jméno"
    :param separator: nastavení separátoru, kterým jsou části jména oddělené (v případě zdroj. souboru se jedná o ","
    :param owner_type: nastavení druhu vlastnictví (defaultně se pro pojmy používá "BUSINESS OWNER")
    :return: pd.DataFrame, který primárně obsahuje sloupce z df doplněné o urn jednotlivých vlastníků
    """

    parsed_df = records_into_rows(df, 'Název pojmu', 'Garanti pojmů', ';')
    owner_preprocess = parsed_df[name_column].str.split(separator, expand=True)
    for col in owner_preprocess:
        owner_preprocess[col + 10] = (owner_preprocess[col].apply(lambda text: unidecode(text).lower()
                                      if text else '').str.lstrip())

    owner_preprocess_v2 = pd.merge(parsed_df, owner_preprocess[[10, 11]],
                                   left_index=True,
                                   right_index=True)
    owner_preprocess_v3 = owner_preprocess_v2[10].str.split(' ', expand=True)
    owner_preprocess_v4 = pd.merge(owner_preprocess_v2, owner_preprocess_v3,
                                   left_index=True,
                                   right_index=True)

    desired_column = 1
    if desired_column in owner_preprocess_v4.columns:
        owner_preprocess_v4['base_urn_long'] = (owner_preprocess_v4.apply
                                                (lambda row: row[11] + '.' + row[0] + ('.' + row[1] if not pd.isna(row[1]) else ''), axis=1))
    else:
        owner_preprocess_v4['base_urn_long'] = (owner_preprocess_v4.apply(lambda row: row[11] + '.' + row[0], axis=1))

    owner_preprocess_v4['urn_long'] = (owner_preprocess_v4.apply
                                       (lambda row: 'urn:li:corpuser:' + row['base_urn_long'], axis=1))
    owner_preprocess_v4['base_urn_short'] = owner_preprocess_v4.apply(lambda row: row[0], axis=1)
    owner_preprocess_v4['urn_short'] = (owner_preprocess_v4.apply
                                        (lambda row: 'urn:li:corpuser:' + row['base_urn_short'], axis=1))

    users_datahub = dh_users[["urn"]]
    users_datahub['dh'] = True
    intersect = pd.merge(owner_preprocess_v4,  users_datahub,
                         left_on='urn_long',
                         right_on='urn',
                         how='left')
    intersect['urn'] = intersect['urn'].fillna(intersect['urn_short'])
    final_owners = intersect[['Název pojmu', 'urn']].rename(columns={'urn': 'owner'})
    final_owners['type'] = owner_type
    return final_owners


def row_transform(df: pd.DataFrame, new_column: object, key_column: object,
                  base_column_1: object, base_column_2: object) -> pd.DataFrame:
    """
    Dílčí funkce agregující řádky vstupního df na základě klíče a ze záznámů z vybraných sloupců vytvoří list slovníků.

    :param df: název pd.DataFrame, v rámci kterého chci danou funkci použít
    :param new_column: název nového sloupce, jehož obsahem bude agregace záznamů do struktury listu slovníků
    :param key_column: název sloupce, který představuje klíč pro agregaci řádků
    :param base_column_1: název prvního sloupce, jehož hodnoty jsou agregovány do struktury listu slovníků
    :param base_column_2: název druhého sloupce, jehož hodnoty jsou agregovány do struktury listu slovníků
    :return: pd.DataFrame obsahující dva sloupce - klíč a hodnoty ve struktuře listu slovníků
    """

    df[new_column] = df.apply(lambda row: {base_column_1: row[base_column_1], base_column_2: row[base_column_2]}
                              if not (pd.isna(row[base_column_1]) or pd.isna(row[base_column_2])) else None, axis=1)
    df = df[df[new_column].notna()]
    dictionary = df.groupby(key_column)[new_column].apply(list).to_dict()
    df_list_of_dicts = pd.DataFrame(dictionary.items(), columns=[key_column, new_column])
    return df_list_of_dicts


def _create_lovs(row):
    """
    Pomocná dílčí funkce odkazující se na hodnotu stejného řádku v jiném sloupci.
    Slouží jako interní funkce pro vstup do funkce _expand_data.

    :param row: vstupní hodnota, na základě které funkce vrací výsledek
    :return: podle podnímky bool hodnota (False) nebo np.nan
    """

    if row:
        return False
    else:
        return np.nan


def _expand_data(df: pd.DataFrame, base_column: object, new_column: object,
                 unidecode_column: object = None, parentnode: str = None) -> pd.DataFrame:
    """
    Pomocná dílčí funkce připravující strukturu dat do podoby, která je nutná pro import dat skrze API do datahubu
    (předtím než se dataframe překlopí do JSON struktury).

    :param df: pd.DataFrame, který obsahuje již všechna klíčová data potřebná pro import skrze API do datahubu,
    která jsou ovšem ještě potřeba doupravit a doplnit o určité položky
    :param base_column: název sloupce s bool typem, na základě kterého bude vytvořen sloupec nový (kompletní)
    :param new_column: název nového sloupce s bool hodnotami, na základě kterého budou skrze interní funkci
    vytvořeny další nové sloupce dat nutné pro vstup do importu
    :param unidecode_column (optional): název sloupce, který je potřeba upravti skrze unidecode script
    :param parentnode (optional): název sloupce pro případné upřesnění parentnodu
    :return: pd.DataFrame s kompletními daty pro import do datahubu skrze API
    """

    df[new_column] = df[base_column]
    for i in range(1, 4):  # tvorba tří nových lov sloupců
        new_column_name_a = f'lov_column_{i}'
        df[new_column_name_a] = df[new_column].apply(_create_lovs)
    df.fillna('', inplace=True)
    if unidecode_column:
        df[unidecode_column] = df[unidecode_column].apply(lambda text: unidecode(text).upper() if text else '')
    if parentnode:
        df['parentNode'] = parentnode
    return df


def _df_to_dict(df: pd.DataFrame, expanded_column: str, urn_actor: str) -> dict:
    """
    Pomocná dílčí funkce konvertující vstupní data ve formátu pd.DataFrame do JSON struktury (dict)
    a rozšiřuje položku u daného klíče o další vnořený dict.

    :param df: pd.DataFrame, který obsahuje kompletní data potřebná pro import
    :param expanded_column: název klíče, u kterého je nutné rozšířit strukturu o další vnořený dict
    :param urn_actor: urn uživatele, který data nahrává (ve struktuře 'urn:li:corpuser:jmeno.prijmeni'
    nebo 'urn:li:corpuser:prijmeni' - dle struktury gmailu)
    :return: data v JSON struktuře připravená pro import skrze API post do datahubu
    """

    data_dict = df.to_dict('index')
    new_keys = ['createStamp']
    counter = 0
    for key, inner_dict in data_dict.items():
        list_of_dict = inner_dict[expanded_column]
        for d in list_of_dict:
            dt = datetime.datetime.now()
            ts = int(datetime.datetime.timestamp(dt) * 1000) + counter
            counter += 1
            d.update({new_key: {"time": ts, "actor": urn_actor} for new_key in new_keys})
        inner_dict[expanded_column] = list_of_dict
    return data_dict


def preprocess_data(df_entities: pd.DataFrame, df_regs: pd.DataFrame, df_owners: pd.DataFrame,
                    parentnode: str = None) -> pd.DataFrame:
    """
    Finální agregující funkce (1/2), která vstupní data (z dataframů) transformuje
    a doplní do potřebné struktury tak, aby mohla posloužit jako vstup do importovací funkce.

    :param df_entities: pd.DataFrame obsahující vstupní data s informacemi o nahrávaných položkách
        (musí obsahovat následující povinné sloupce:'Název pojmu', 'Definice pojmu', 'Kód výskyt pojmu', 'Garanti pojmů',
        'Zkratka pojmu', 'Název pojmu (EN)', 'Zkratka (EN)', 'Kategorie', 'Datová entita')
    :param df_regs: pd.DataFrame obsahující přehled přespisů (dostupný na intranetu)
    :param df_owners: pd.DataFrame obsahující seznam existujících uživatelských účtú v datahubu
    :param parentnode: v případě hromadného zařazení všech nahrávaných položek do jedné nadřazené složky
    :return: pd.DataFrame obsahující všechny položky nutné k importu do datahubu
    """

    df_regs_ = _preprocess_regs(df_regs)
    df_parse_regs = records_into_rows(df_entities, 'Název pojmu', 'Kód výskyt pojmu', ';')
    df_parse_owners = _add_owners_urn(df_entities, df_owners, 'Garanti pojmů', ',', 'BUSINESS_OWNER')
    df_parse_regs_url = (pd.merge(df_parse_regs, df_regs_,
                                  left_on='Kód výskyt pojmu',
                                  right_on='ID předpisu',
                                  how='left').rename(columns={'předpis_full': 'description', 'Odkaz': 'url'}))
    df_regs_url = row_transform(df_parse_regs_url, 'elements', 'Název pojmu', 'url', 'description')
    df_ownership = row_transform(df_parse_owners, 'owners', 'Název pojmu', 'owner', 'type')
    df_merged2 = pd.merge(df_entities, df_regs_url,
                          left_on='Název pojmu',
                          right_on='Název pojmu',
                          how='left')
    df_merged = (pd.merge(df_merged2, df_ownership,
                          left_on='Název pojmu',
                          right_on='Název pojmu',
                          how='left').rename(columns={'Název pojmu': 'name', 'Definice pojmu': 'definition',
                                                      'Zkratka pojmu': 'abbrev', 'Název pojmu (EN)': 'nameEn',
                                                      'Zkratka (EN)': 'abbrevEn', 'Kategorie': 'termCategory'}))
    df_prepared = _expand_data(df_merged, 'Datová entita', 'isEntity', 'termCategory', parentnode)
    return df_prepared


def import_data(df: pd.DataFrame, urn_actor: str, test: bool = True):
    """
    Finální agregující funkce (2/2), která otestuje úplnost a správnost vstupních dat
    a skrze kterou se přes API importují jednotlivé prvky glossary terms do datahubu.

    :param df: předpřipravený a otestovaný df, v kterém jsou obsažena veškerá data
        tvořící jednotlivé glossary terms potřebná pro import do datahubu
    :param urn_actor: urn osoby, která glossary terms nahrává (urn:li:corpuser:jmeno.prijmeni
        nebo urn:li:corpuser:prijmeni - dle struktury gmailu)
    :param test: určení, jestli se jedná o test (True) nebo produkci (False)
    :return: nahrání glossary terms na zvolený server datahubu (s informací o průběhu uploadu
        na úrovni jednotlivých terms a nově vytvořeném urn pro daný term)
    """

    columns_for_is_column_filled = ['name', 'termCategory', 'isEntity']
    for column_filled in columns_for_is_column_filled:
        if not is_column_filled(df, column_filled):
            raise ValueError(f"Not all values are filled in column '{column_filled}' .")

    predefined_values = ['ROLE', 'ICT', 'DOKUMENT', 'OSTATNI', 'INSTITUCE']
    if not has_specific_values(df, 'termCategory', predefined_values):
        raise ValueError("The 'termCategory' column contains an invalid value.")

    if not contains_boolean_values(df, 'isEntity'):
        raise ValueError("The 'isEntity' column contains an invalid value (only bool accepted).")

    if not no_duplicates_in_column(df, 'name'):
        raise ValueError("The 'name' column contains duplicate values.")

    columns_for_is_list_of_dicts = ['elements', 'owners']
    for column_with_list in columns_for_is_list_of_dicts:
        if not is_column_list_of_dicts(df, column_with_list):
            raise ValueError(f"Not all values are proper list_of_dicts in column '{column_with_list}' .")

    json_data = _df_to_dict(df, 'elements', urn_actor)
    for key, value in json_data.items():
        term_id = uuid.uuid1().hex
        if value['parentNode'] == '':
            glossary_term_info = [
                {
                    'entityType': 'glossaryTerm',
                    'entityKeyAspect': {
                        '__type': 'GlossaryTermKey',
                        'name': term_id
                    },
                    'aspect': {
                        '__type': 'GlossaryTermInfo',
                        'name': value['name'],
                        'definition': value['definition'],
                        'termSource': 'INTERNAL'
                    }
                }
            ]
        else:
            glossary_term_info = [
                {
                    'entityType': 'glossaryTerm',
                    'entityKeyAspect': {
                        '__type': 'GlossaryTermKey',
                        'name': term_id
                    },
                    'aspect': {
                        '__type': 'GlossaryTermInfo',
                        'name': value['name'],
                        'definition': value['definition'],
                        'parentNode': value['parentNode'],
                        'termSource': 'INTERNAL'
                    }
                }
            ]
        r = post_data(glossary_term_info, test)

        urn = r.json()[0]

        glossary_term_tacr_gen = {
                'entityType': 'glossaryTerm',
                'entityUrn': urn,
                'aspect': {
                    '__type': 'GlossaryTermTacrGen',
                    'abbrev': value['abbrev'],
                    'nameEn': value['nameEn'],
                    'abbrevEn': value['abbrevEn'],
                    'termCategory': value['termCategory']
                }
            }

        glossary_term_tacr = {
                'entityType': 'glossaryTerm',
                'entityUrn': urn,
                'aspect': {
                    '__type': 'GlossaryTermTacr',
                    'isEntity': value['isEntity']
                }
            }

        glossary_term_tacr_entity = {
                'entityType': 'glossaryTerm',
                'entityUrn': urn,
                'aspect': {
                    '__type': 'GlossaryTermTacrEntity',
                    'lov': value['lov_column_1'],
                    'externalLov': value['lov_column_2'],
                    'lovSource': value['lov_column_3']
                }
            }

        if value['elements'] != '':
            institutional_memory = {
                'entityType': 'glossaryTerm',
                'entityUrn': urn,
                'aspect': {
                    '__type': 'InstitutionalMemory',
                    'elements': value['elements']

                }
            }
        else:
            pass

        if value['owners'] != '':
            ownership = {
                'entityType': 'glossaryTerm',
                'entityUrn': urn,
                'aspect': {
                    '__type': 'Ownership',
                    'owners': value['owners']

                }
            }
        else:
            pass

        api_structure = [glossary_term_tacr_gen, glossary_term_tacr,
                         glossary_term_tacr_entity, institutional_memory, ownership]

        r = post_data(api_structure, test)

        if 200 <= r.status_code <= 250:
            print("Post successful:", value['name'], urn)
        else:
            print(f"Post failed. Status code: {r.status_code}")
            print(value['name'], urn)
