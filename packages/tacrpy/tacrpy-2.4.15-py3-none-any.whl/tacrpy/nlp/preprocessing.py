"""
Tento modul slouží k předzpracování textových dat pro další využití v textových analýzích (NLP).
"""

import re
import string

import pandas as pd

from corpy.udpipe import Model

from tqdm import tqdm
tqdm.pandas()


def create_corpus(df: pd.DataFrame) -> pd.DataFrame:
    """ Vytvoří corpus (soubor textů) k dalšímu zpracování v textových analýzách.

    :param df: vstupní dataframe, kde první sloupec je ID a další sloupce obsahují textové informace
    :return: dataframe s ID a corpus textů
    """
    id_col = df.columns[0]
    corpus_cols = df.columns[1:]
    df = df.fillna('')
    df['corpus'] = df[corpus_cols].agg('. '.join, axis=1)
    corpus_df = df[[id_col, 'corpus']]
    corpus_df.columns = ['id', 'corpus']

    return corpus_df


def text_cleaning(text: str) -> str:
    """ Odstraní všechny netextové znaky.

    :param text: text k vyčištění
    :return: vyčištěný text
    """
    text = text.lower()
    text = re.sub('\d', '', text)  # odstraní čísla
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)  # odstranění interpukci a speciální znaky
    text = re.sub(' +', ' ', text)  # odstraní whitespace
    return text


def text_lemmatization(text: str, model: Model) -> str:
    """ Pro český text vytvoří lemmatizované tvary.

    :param text: text k lemmatizaci
    :param model: UDPipe model, který slouží k lemmatizovaní českých slov
    :return: lemmatizovaný text
    """
    sentence = []

    for s in model.process(text):
        for w in s.words:
            if '<root>' not in w.lemma:
                sentence.append(w.lemma)

    lemma = ' '.join(sentence)

    return lemma


def text_preprocessing(text: str, model: Model) -> str:
    """ Předzpracování (vyčištění a lemmatizace) českého textu pro další využití v textových analýzách.

    :param text: text k předzpracování
    :param model: UDPipe model, který slouží k lemmatizovaní českých slov
    :return: předzpracovaný text
    """
    text = text_cleaning(text)
    text = text_lemmatization(text, model)
    return text


def text_preprocessing_bulk(df: pd.DataFrame, model: Model) -> pd.DataFrame:
    """ Hromadné předzpracování __českého__ textu pro další využití v textových analýzách.

    :param df: vstupní dataframe, kde první sloupec je ID a další sloupce obsahují textové informace
    :param model: UDPipe model, který slouží k lemmatizovaní českých slov
    :return: dataframe s předzpracovanými texty
    """
    df_preprocessed = create_corpus(df)
    df_preprocessed['lemma'] = df_preprocessed['corpus'].progress_apply(lambda x: text_preprocessing(x, model))
    df_preprocessed = df_preprocessed[['id', 'lemma']]
    return df_preprocessed
