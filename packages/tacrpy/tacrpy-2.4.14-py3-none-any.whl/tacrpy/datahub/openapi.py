"""Soubor funkcí k práci s OpenAPI DataHubu."""

import requests


def post_data(json_data: list[dict], test: bool = True) -> requests.Response:
    """ Nahraje přes OpenAPI data do DataHubu.

    Než se data nahrají je vhodné provést kontroly správnosti dat.

    :param json_data: data ve formátu JSON, které se mají nahrát do DataHubu
    :param test: nahraje data buď na testovací nebo produkční prostředí
    :return: objekt třídy Response, který reprezentuje odezvu serveru
    """

    if test:
        server = 'http://datahub-test.tacr.cz:8080/'
    else:
        server = 'http://datahub.tacr.cz:8080/'

    query = 'openapi/entities/v1/'
    url = server + query

    r = requests.post(url, json=json_data)

    return r


def get_data(urn: str, test: bool = True) -> dict:
    """ Získá data k vybrané entitě přes OpenAPI.

    :param urn: URN entity, pro kterou chceme získat data
    :param test: získá data buď z testovacího nebo produkčního prostředí
    :return: data ve formátu JSON
    """

    if test:
        server = 'http://datahub-test.tacr.cz:8080/'
    else:
        server = 'http://datahub.tacr.cz:8080/'

    query = f'openapi/entities/v1/latest?urns={urn}'

    url = server + query

    r = requests.get(url)

    json_data = r.json()['responses']

    return json_data


def delete_data(urn: str, test: bool = True, soft: bool = False) -> requests.Response:
    """ Vymaže data vybrané entity přes OpenAPI

    :param urn: URN entity, kterou chceme vymazat
    :param test: vymaže data z testovacího nebo produkčního prostředí
    :param soft: můžeme entitu vymazat pouze z vyhledávání (soft = True) nebo kompletně (soft = False)
    :return: objekt třídy Response, který reprezentuje odezvu serveru
    """

    if test:
        server = 'http://datahub-test.tacr.cz:8080/'
    else:
        server = 'http://datahub.tacr.cz:8080/'

    if soft:
        soft_delete = '&soft=true'
    else:
        soft_delete = '&soft=false'

    query = f'openapi/entities/v1/?urns={urn}'

    url = server + query + soft_delete

    r = requests.delete(url)

    return r
