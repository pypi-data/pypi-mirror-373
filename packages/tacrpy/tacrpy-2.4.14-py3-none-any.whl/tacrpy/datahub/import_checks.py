""" Modul obsahuje předdefinované funkce, které slouží jako kontrola
úplnosti dat importovaných skrze API do datahubu.
Primárním využitím je testování skrze tyto předdefinované funkce nad cílovým souborem.
 """

import pandas as pd
import ast

# kontrola vyplnění všech hodnot ve sloupci
def is_column_filled(df: pd.DataFrame, column_name: object) -> bool:
    """ Ověřovací funkce určená primárně jako vstup do testu, indikuje, zda je sloupec kompletně vyplněný,
    tj. zda v daném sloupci nejsou obsaženy prázdné hodnoty.

    :param df: dataframe, v rámci kterého chci danou podmínku ověřovat
    :param column_name: sloupec v rámci dataframu, na který chci danou podmínku aplikovat
    :return: bool hodnota podle toho, jestli je nebo není podmínka pro vybraný sloupec splněna
    """
    return df[column_name].notnull().all()

# kontrola, jestli jsou ve sloupci předepsané hodnoty
def has_specific_values(df: pd.DataFrame, column_name: object, predefined_values: list[any]) -> bool:
    """ Ověřovací funkce určená primárně jako vstup do testu, indikuje, zda se ve sloupci vyskytují pouze předdefinované hodnoty.

    :param df: dataframe, v rámci kterého chci danou podmínku ověřovat
    :param column_name: sloupec v rámci dataframu, na který chci danou podmínku aplikovat
    :param predefined_values: list předdefinovaných hodnot
    :return: bool hodnota podle toho, jestli je nebo není podmínka pro vybraný sloupec splněna
    """
    return df[column_name].isin(predefined_values).all()

# kontrola, zda sloupec obsahuje pouze bool hodnoty (True nebo False)
def contains_boolean_values(df: pd.DataFrame, column_name: object) -> bool:
    """ Ověřovací funkce určená primárně jako vstup do testu, indikuje, zda se ve sloupci vyskytují pouze bool hodnoty.

    :param df: dataframe, v rámci kterého chci danou podmínku ověřovat
    :param column_name: sloupec v rámci dataframu, na který chci danou podmínku aplikovat
    :return: bool hodnota podle toho, jestli je nebo není podmínka pro vybraný sloupec splněna
    """
    return df[column_name].apply(lambda x: isinstance(x, bool)).all()

# kontrola, zda sloupec obsahuje pouze object values
def are_all_values_objects_in_column(df: pd.DataFrame, column_name: object) -> bool:
    """ Ověřovací funkce určená primárně jako vstup do testu, indikuje, zda se ve sloupci vyskytují pouze object hodnoty.

    :param df: dataframe, v rámci kterého chci danou podmínku ověřovat
    :param column_name: sloupec v rámci dataframu, na který chci danou podmínku aplikovat
    :return: bool hodnota podle toho, jestli je nebo není podmínka pro vybraný sloupec splněna
    """
    column = df[column_name]
    return all(isinstance(value, object) for value in column)

# kontrola duplicit
def no_duplicates_in_column(df: pd.DataFrame, column_name: object) -> bool:
    """ Ověřovací funkce určená primárně jako vstup do testu, indikuje, zda se ve sloupci vyskytují duplicitní hodnoty.

    :param df: dataframe, v rámci kterého chci danou podmínku ověřovat
    :param column_name: sloupec v rámci dataframu, na který chci danou podmínku aplikovat
    :return: bool hodnota podle toho, jestli je nebo není podmínka pro vybraný sloupec splněna
    """
    return not df[column_name].duplicated().any()

# kontrola, zda se ve sloupci nachází hodnoty strukturované do list[dict].
def is_column_list_of_dicts(df: pd.DataFrame, column_name: object) -> bool:
    """ Ověřovací funkce určená primárně jako vstup do testu, ověřuje, zda buňky ve sloupci obsahují pouze obsah strukturovaný do listu slovníků (v případě, že nejsou prázdné).

    :param df: dataframe, v rámci kterého chci danou podmínku ověřovat
    :param column_name: sloupec v rámci dataframu, na který chci danou podmínku aplikovat
    :return: bool hodnota podle toho, jestli je nebo není podmínka pro vybraný sloupec splněna
    """
    filtered_df = df[df[column_name].notna() & (df[column_name] != '')]
    column = filtered_df[column_name]
    for i, cell_value in enumerate(column):
        if isinstance(cell_value, list):
            for item in cell_value:
                if not isinstance(item, dict):
                    print(f"Row {i} contains a non-dict element: {item}")
                    return False
        elif isinstance(cell_value, str):
            try:
                parsed_value = ast.literal_eval(cell_value)
                if not isinstance(parsed_value, list):
                    print(f"Row {i} is not a list: {parsed_value}")
                    return False
                for item in parsed_value:
                    if not isinstance(item, dict):
                        print(f"Row {i} contains a non-dict element: {item}")
                        return False
            except (ValueError, SyntaxError):
                print(f"Row {i} is not a valid list/dictionary: {cell_value}")
                return False
        else:
            print(f"Row {i} is not a list or string: {cell_value}")
            return False

    return True

# kontrola zda se ve sloupci v rámci list[dict] nenachází nespárované komponenty (např. prázdné values)
def notnan_in_columns_with_list_of_dicts(df: pd.DataFrame, column_name: object) -> bool:
    """ Ověřovací funkce určená primárně jako vstup do testu, ověřuje, zda buňky s obsahem strukturovaným do listu slovníků neobsahují Nan values uvnitř slovníků.

    :param df: dataframe, v rámci kterého chci danou podmínku ověřovat
    :param column_name: sloupec v rámci dataframu, na který chci danou podmínku aplikovat
    :return: bool hodnota podle toho, jestli je nebo není podmínka pro vybraný sloupec splněna
    """
    notnan_values = [': nan',': NaN']
    for value in notnan_values:
        if df[column_name].str.contains(value).any():
            return False
        else:
            return True