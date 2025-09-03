"""Modul na načítání dat z IS VaVaI a STARFOSu."""

import pandas as pd
import requests
import string
from tqdm import tqdm
from typing import Union
from bs4 import BeautifulSoup


def isvav_projects() -> pd.DataFrame:
    """ Načte data o příjemcích z otevřených dat IS VaVaI.
    Data jsou aktualizovaná cca jednou za čtvrt roku.

    :return: DataFrame načtených dat ze zdroje
    """

    df = pd.read_csv("https://www.isvavai.cz/dokumenty/opendata/CEP-projekty.csv")
    return df


def isvav_organizations() -> pd.DataFrame:
    """ Načte data o projektech z otevřených dat IS VaVaI.
    Data jsou aktualizovaná cca jednou za čtvrt roku.

    :return: DataFrame načtených dat ze zdroje
    """

    df = pd.read_csv("https://www.isvavai.cz/dokumenty/opendata/CEP-ucastnici.csv")
    return df


def get_providers() -> list:
    """ Stáhne seznam kódu všech poskytovatelů v IS VaVaI.
    Data jsou získána pomocí web scrapingu z webu IS VaVaI.

    :return: seznam kódu poskytovatelů
    """

    base_url = 'https://www.isvavai.cz/cea?s=poskytovatele&n='

    provider_list = []
    for page in range(0, 2):
        url = base_url + str(page)
        html = requests.get(url).content
        parsed_html = BeautifulSoup(html, 'html.parser')

        for i in parsed_html.findAll('b', attrs={'class': 'abbr'}):
            provider_list.append(i.find('a').text)

    # nejsou v seznamu aktivních poskytovatelů, jedná se o historická ministerstva
    # ministerstvo hospodářství a ministesrtvo informatiky
    provider_list.extend(['MH0', 'MI0'])
    return provider_list


def starfos_projects(prog_select: Union[str, list] = None,
                     prov_select: Union[str, list] = None) -> Union[pd.DataFrame, dict[str]]:
    """ Stáhne ze STARFOS projekty buď podle kódů programů nebo kódů poskytovatelů
    
    Volá API endpoint, který slouží pro vytváření exportů. Výstup exportu převede na DataFrame.

    :param prog_select: seznam programů
    :param prov_select: seznam poskytovatelů
    :return: projekty ze STARFOS
    """

    url = 'https://old.starfos.tacr.cz/api/starfos/export'
    headers = {'content-type': 'application/json'}

    common_query_template = {
        "collection": "isvav_project",
        "language_ui": "cs",
        "format": "xlsx",
        "limit": 0,
        "columns": ["code", "name", "anot", "name_en", "anot_en", "x_solve_begin_year", "x_solve_end_year"],
        "filters": {}
    }

    if prog_select:
        programme_filter = {
            "programme__code": {
                "option_codes": prog_select
            }
        }
        common_query_template['filters'].update(programme_filter)

    if prov_select:
        provider_filter = {
            "programme__funder__code": {
                "option_codes": prov_select
            }
        }
        common_query_template['filters'].update(provider_filter)

    try:
        r = requests.post(url, headers=headers, json=common_query_template, stream=True)
        r.raise_for_status()
        df = pd.read_excel(r.content)
        return df
    except requests.exceptions.RequestException as e:
        if not prog_select or prov_select:
            return {'error': str(e),
                    'additional_info': 'You need to enter at least one programme (prog_select) or provider (prov_select).'}
        else:
            return {'error': str(e), 'additional_info': 'Unknown error.'}


def starfos_projects_all() -> pd.DataFrame:
    """ Stáhne ze STARFOS všechny projekty.

    Postupně volá API endpoint, který slouží pro vytváření exportu, za jednotlivé poskytovatele. Výjimku tvoří GA ČR,
    který přesahuje maximální limit 20 000 záznamů, proto se volá po jednotlivých programech (resp. zkouší různé
    kombinace s G na začátku). Výstupy se skládají do jednoho DataFrame.

    :return: projekty ze STARFOS
    """

    url = 'https://old.starfos.tacr.cz/api/starfos/export'
    headers = {'content-type': 'application/json'}

    df_list = []

    provider_list = get_providers()

    common_query_template = {
        "collection": "isvav_project",
        "language_ui": "cs",
        "format": "xlsx",
        "limit": 0,
        "columns": ["code", "name", "anot", "name_en", "anot_en", "x_solve_begin_year", "x_solve_end_year"],
        "filters": {}
    }

    for prov in tqdm(provider_list):
        query_template = common_query_template.copy()

        if prov == 'GA0':
            programme_list = ['G' + i for i in string.ascii_uppercase]
            for prog in programme_list:
                query_template['filters'] = {
                    "programme__code": {
                        "option_codes": [prog]
                    }
                }
                r = requests.post(url, headers=headers, json=query_template, stream=True)
                df = pd.read_excel(r.content)
                df['provider'] = prov
                df_list.append(df)
        else:
            query_template['filters'] = {
                "programme__funder__code": {
                    "option_codes": [prov]
                }
            }

            r = requests.post(url, headers=headers, json=query_template, stream=True)
            df = pd.read_excel(r.content)
            df['provider'] = prov
            df_list.append(df)
    df_concat = pd.concat(df_list).reset_index(drop=True)
    return df_concat
