"""Modul na načítání dat, které jsou uložené v BigQuery jakožto 'zdroj pravdy'."""

import pandas as pd
import gspread

#from google.colab import auth
#auth.authenticate_user()


#from google.auth import default
#creds, _ = default()


def _load_df_from_google_sheet(creds, file_id, worksheet_idx): 
    gc = gspread.authorize(creds)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(worksheet_idx)
    rows = worksheet.get_all_values()
    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


class Projects:
    """ Třída, která načítá a reprezentuje tabulku projektů.

    Funguje pouze v rámci Google Colab prostředí.

    :param projects: DataFrame načtených dat ze zdroje nebo z nově vytvořené (vyfiltrované) instance
    :type projects: DataFrame
    :param summary: DataFrame s agregovanými údaji na úrovni veřejných soutěží
    :type summary: DataFrame
    """

    def __init__(self, creds_or_df: object):
        """ Kontstruktor, který načte data do DataFrame, očistí finanční hodnoty a vytvoří agregovanou tabulku.

        :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab nebo přímo DataFrame projektu
        """

        self.projects = None
        if isinstance(creds_or_df, pd.DataFrame):
            self.projects = creds_or_df
        else:
            self.projects = self._get_projects(creds_or_df)
            self._finance_cleaning('Náklady celkem')
            self._finance_cleaning('Podpora celkem')
            self._finance_cleaning('Ostatní celkem')
        self.summary = self.create_summary()


    def _get_projects(self, creds_or_df: object) -> pd.DataFrame:
        """ Načte data o projektech ze "zdroje pravdy" z googlesheets uloženého na Google disku.

        Lze použít pouze v rámci Google Colab prostředí.

        :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab nebo přímo DataFrame projektu
        :return: DataFrame načtených dat ze zdroje
        """

        file_id = "1Ax1OYkdg3IA1YZki0fePizgQR6zOuzq7VGhFgeMorDQ"
        return _load_df_from_google_sheet(creds_or_df, file_id, 0)


    def _finance_cleaning(self, column_name: str):
        """ Interní funkce, která očistí finanční data.

        :param column_name: název sloupce, ve kterém se mají finanční data očistit
        """

        self.projects[column_name].fillna(0, inplace=True)
        self.projects[column_name] = self.projects[column_name].str.replace(',', '.')
        self.projects[column_name] = self.projects[column_name].replace('', '0')
        self.projects[column_name] = self.projects[column_name].astype(float)


    #! HODIT NEKAM, KDE K TOMU BUDU MOCT PRISTUPOVAT ZE VSECH SOUBORU 
    def _check_missing_items(self, provided_items: tuple, existing_items: list, item_name: str): 
        """Ověří, zda se všechny zadané položky nacházejí v existujícím seznamu. 

        Pokud jsou nalezeny chybějící položky, vyvolá ValueError s chybovou zprávou. 

        :param provided_items: Tuple položek zadaných pro filtrování. 
        :param existing_items: Seznam všech unikátních položek nacházejících se v datové sadě. 
        :param item_name: Popisný název položky, který se použije v chabové hlášce. 
        
        :raises ValueError: Pokud alespoň jedna zadaná položka neexistuje v datové sadě. 
        """

        missing_items = [item for item in provided_items if item not in existing_items]
        if missing_items: 
            raise ValueError(f'{item_name} {missing_items} neexistuje/neexistují.')



    def create_summary(self, level: str = 'cfp') -> pd.DataFrame:
        """ Vytvoří agregovaný souhrn buď na úrovni veřejných soutěží (defaultní) nebo na úrovni programů.

        :param level: určuje, na jaké úrovni se provede agregace

                      * 'cfp' (defaultní) - na úrovni veřejných soutěží
                      * 'prog' - na úrovni programů
        :return: agregovaný DataFrame, který obsahuje:

                * Počet podaných projektů
                * Počet podpořených projektů
                * Náklady podpořených projektů
                * Podpora podpořených projektů
        """

        if level not in ['cfp', 'prog']:
            raise ValueError('Neexistující forma agregace.')

        temp_df = self.projects.copy()
        temp_df['Podpořené'] = temp_df.apply(
            lambda x: 'Ano' if x['Fáze projektu'] in ['Realizace', 'Implementace', 'Ukončené'] else 'Ne', axis=1)
        submitted = temp_df.groupby(['Kód programu', 'Kód VS']).agg(
            {'Kód projektu': 'count', 'Náklady celkem': 'sum', 'Podpora celkem': 'sum'}).reset_index()
        funded = temp_df[temp_df['Podpořené'] == 'Ano'].groupby(['Kód programu', 'Kód VS']).agg(
            {'Kód projektu': 'count', 'Náklady celkem': 'sum', 'Podpora celkem': 'sum'}).reset_index()

        summary_df = pd.merge(submitted[['Kód programu', 'Kód VS', 'Kód projektu']], funded, how='inner',
                              on=['Kód programu', 'Kód VS'])
        summary_df.columns = ['Kód programu', 'Kód VS', 'Podané', 'Podpořené', 'Náklady', 'Podpora']

        if level == 'cfp':
            pass
        elif level == 'prog':
            summary_df = summary_df.groupby('Kód programu').agg('sum', numeric_only=True).reset_index()

        return summary_df


    def select_programme(self, *args: str) -> 'Projects':
        """ Vyfiltruje tabulku tak, aby obsahovala pouze projekty vybraných programů.

        :param args: kódy programů, které se mají vyfiltrovat
        :return: nová instance třídy Projects s vyfiltrovanými údaji
        :raise: ValueError
        """

        existing_programmes = self.projects['Kód programu'].unique()
        self._check_missing_items(args, existing_programmes, 'Programy')

        select_df = self.projects[self.projects['Kód programu'].isin(args)].reset_index(drop=True)
        return Projects(select_df)  # todo maybe another class Programms?


    def select_cfp(self, *args: str) -> 'Projects':
        """ Vyfiltruje tabulku tak, aby obsahovala pouze projekty vybraných veřejných soutěží.

        :param args: kódy veřejných soutěží, které se mají vyfiltrovat
        :return: nová instance třídy Projects s vyfiltrovanými údaji
        :raise: ValueError
        """

        existing_cfp = self.projects['Kód VS'].unique()
        self._check_missing_items(args, existing_cfp, 'Veřejné soutěže')

        select_df = self.projects[self.projects['Kód VS'].isin(args)].reset_index(drop=True)
        return Projects(select_df)


    def select_funded(self) -> 'Projects':
        """ Vyfiltruje tabulku tak, aby obsahovala pouze podpořené projekty.

        :return: nová instance třídy Projects s vyfiltrovanými údaji
        """

        funded_states = ['Realizace', 'Implementace', 'Ukončené']
        select_df = self.projects[self.projects['Fáze projektu'].isin(funded_states)].reset_index(drop=True)
        return Projects(select_df)


def projects_finance(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o financích projektů ze "zdroje pravdy" z googlesheets uloženého na Google disku.

    Finance jsou v rozdělení po jednotlivých letech.
    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """

    file_id = "1Ax1OYkdg3IA1YZki0fePizgQR6zOuzq7VGhFgeMorDQ"
    return _load_df_from_google_sheet(creds_or_df, file_id, 1)


def organizations(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o uchazečích/příjemcích ze "zdroje pravdy" z googlesheets uloženého na Google disku.

    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """

    file_id = "1h7HpPn-G0_XY2gb_sExAQDkzR1TswGUH_2FuHCWhbRg"
    return _load_df_from_google_sheet(creds_or_df, file_id, 0)


def organizations_finance(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o financích uchazečů/příjemců ze "zdroje pravdy" z googlesheets uloženého na Google disku.

    Finance jsou v rozdělení po jednotlivých letech.
    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """

    file_id = "1h7HpPn-G0_XY2gb_sExAQDkzR1TswGUH_2FuHCWhbRg"
    return _load_df_from_google_sheet(creds_or_df, file_id, 1)


def results(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o výsledcích ze "zdroje pravdy" z googlesheets uloženého na Google disku.

    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """

    file_id = "1eSE6gB8bwuP6OVwVVhQojQLS6aPi_q8t7gK6VhPyiRw"
    return _load_df_from_google_sheet(creds_or_df, file_id, 0)


def cfp(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o veřejných soutěží z googlesheets uloženého na Google disku.

    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """

    file_id = "1FaVienG6ceJGdqSTyD5tpsUsRGxgPii6BWOL73Vk2_s"
    return _load_df_from_google_sheet(creds_or_df, file_id, 1).iloc[:, 0:15]
