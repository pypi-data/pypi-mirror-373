"""
Modul pro běžné transformace a zpracování dat.
"""

import pandas as pd


def create_mapping_dict(df: pd.DataFrame) -> dict:
    """ Z dataframe, kde se k jedné hodnotě váže více pozorování v samostatných řádcích (např. projekt má N uchazečů)
    vytvoří mapovací dict

    :param df: dataframe s hodnotami one-to-many
    :return: mapovací dict, kde unikátní ID je klíč a hodnotou je seznam hodnot, které patří k danému unikátnímu ID
    """

    if df.shape[1] < 2: 
        raise ValueError("DataFrame mmusí mít aspoň da sloupce pro vytvoření mapovacího slovníku.")
    
    grouped_data = df.groupby(df.columns[0])[df.columns[1]]
    return grouped_data.apply(list).to_dict()


def list_intersection(list1: list, list2: list, percentages: bool = True) -> dict:
    """ Získá průnik hodnot mezi dvěma seznamy (listy) a vypočítá metriky průniku.

    Metriky průniku:

    - *intersect (list)* - seznam stejných hodnot
    - *intersect_count (int)* - počet stejných hodnot
    - *intersect_ratio (float)* - podíl stejných hodnot vůči všem unikátním hodnotám z obou seznamů
    - *intersect_l1_ratio (float)* - podíl stejných hodnot vůči všem hodnotám v prvnímu seznamu
    - *intersect_l2_ratio (float)* - podíl stejných hodnot vůči všem hodnotám v druhému seznamu

    :param list1: seznam hodnot
    :param list2: seznam hodnot
    :param percentages: poměrové metriky zobrazí vrátí v procentech (0-100) s přesností na dvě desetinná místa
    :return: dict metrik průniků
    """

    if not list1: 
        raise ValueError("list1 je prázdný")
    if not list2: 
        raise ValueError("list2 je prázdný")

    set1, set2 = set(list1), set(list2)
    intersect = set1.intersection(set2)
    l1_count = len(set1)
    l2_count = len(set2)
    all_count = len(set1.union(set2))
    
    intersect_count = len(intersect)

    intersect_dict = dict()
    intersect_dict['intersect'] = list(intersect)
    intersect_dict['intersect_count'] = intersect_count

    intersect_ratio = intersect_count / all_count
    intersect_l1_ratio = intersect_count / l1_count
    intersect_l2_ratio = intersect_count / l2_count

    if percentages:
        rounding = lambda x: round(x * 100, 2)  # prevod na procenta 
        intersect_dict['intersect_ratio'] = rounding(intersect_ratio)
        intersect_dict['intersect_ratio_l1'] = rounding(intersect_l1_ratio)
        intersect_dict['intersect_ratio_l2'] = rounding(intersect_l2_ratio)
    else:
        intersect_dict['intersect_ratio'] = intersect_ratio
        intersect_dict['intersect_ratio_l1'] = intersect_l1_ratio
        intersect_dict['intersect_ratio_l2'] = intersect_l2_ratio
    return intersect_dict
