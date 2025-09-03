"""
Modul pro fulltextovou práci s texty např. extrahování informací, podobnost dokumentů.
"""

import re

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class FulltextSimilarity:
    """
    Vytvoří podobnost mezi porovnávanými (kontrolovanými) a referenčními dokumenty.

    :param corpus_comparison: soubor dokumentů k porovnání (včetně ID)
    :type corpus_comparison: DataFrame
    :param corpus_reference: soubor dokumentů, vůči kterým porovnáváme (včetně ID)
    :type corpus_reference: DataFrame
    :param lemma_comparison: lemmatizované dokumenty k porovnání
    :type lemma_comparison: list
    :param lemma_reference: lemmatizované dokumenty, vůči kterým porovnáváme
    :type lemma_reference: list

    :param document_ids: unikatní ID všech nahraných dokumentů
    :type document_ids: list
    :param features: seznam slov a slovních spojení v modelu TF-IDF
    :type features: ndarray
    :param tfidf_matrix: matice dokumentů a slov/slovních spojení (features)
    :type tfidf_matrix: ndarray
    :param cos_sim: matice podobných dokumentů
    :type cos_sim: ndarray
    :param similar_documents: dvojice podobných dokumentů včetně skóre podobnosti
    :type similar_documents: DataFrame

    :param include_comparison: zahrne porovnávané (kontrolované) dokumenty k referenčním
    :type include_comparison: bool
    :param threshold: hranice podobnosti (hodnoty 0-1), nad kterou chceme vyextrahovat podobné dokumenty
    :type threshold: float
    """

    def __init__(self, lemma_corpus_comparison: pd.DataFrame, lemma_corpus_reference: pd.DataFrame = None):
        self.corpus_comparison = lemma_corpus_comparison
        self.corpus_reference = lemma_corpus_reference
        lemma_col = self.corpus_comparison.columns[1]
        self.lemma_comparison = self.corpus_comparison[lemma_col].tolist()
        if self.corpus_reference is not None:
            lemma_col = self.corpus_reference.columns[1]
            self.lemma_reference = self.corpus_reference[lemma_col].tolist()

        self.document_ids = None
        self.features = None
        self.tfidf_matrix = None
        self.cos_sim = None
        self.similar_documents = None

        self.include_comparison = None
        self.threshold = None

    def create_tfidf(self, **kwargs) -> 'FulltextSimilarity':
        """ Vytvoří TF-IDF reprezentaci dokumentů.

        Více o využití [TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
        """

        if self.corpus_reference is not None:
            lemma = self.lemma_comparison + self.lemma_reference

            comparison_ids_col = self.corpus_comparison.columns[0]
            reference_ids_col = self.corpus_reference.columns[0]

            comparison_ids = self.corpus_comparison[comparison_ids_col].tolist()
            reference_ids = self.corpus_reference[reference_ids_col].tolist()

            document_ids = comparison_ids + reference_ids
        else:
            comparison_ids_col = self.corpus_comparison.columns[0]
            comparison_ids = self.corpus_comparison[comparison_ids_col].tolist()

            lemma = self.lemma_comparison
            document_ids = comparison_ids

        tfidf = TfidfVectorizer(**kwargs)
        tfidf_matrix = tfidf.fit_transform(lemma)
        self.tfidf_matrix = tfidf_matrix
        self.features = tfidf.get_feature_names_out()
        self.document_ids = document_ids
        return self

    def create_similarity(self, include_comparison: bool = False, **kwargs) -> 'FulltextSimilarity':
        """ Vytvoří matici podobností na základě cosine similarity.

        Pokud neexistují referenční dokumenty, tak porovnává kontrolované dokumenty mezi sebou.
        V případě parametru _include_comparison_ se porovnávají kontrolované dokumenty vůči referenčním i kontrolovaným.

        :param include_comparison: zahrne porovnávané (kontrolované) dokumenty k referenčním
        """

        self.create_tfidf(**kwargs)
        tfidf_matrix = self.tfidf_matrix

        if self.corpus_reference is not None:
            comparison_len = len(self.lemma_comparison)
            tfidf_matrix_comparison = tfidf_matrix[:comparison_len]

            if include_comparison:
                tfidf_matrix_reference = tfidf_matrix

            else:
                tfidf_matrix_reference = tfidf_matrix[comparison_len:]

            cos_sim = cosine_similarity(tfidf_matrix_comparison, tfidf_matrix_reference)
        else:
            cos_sim = cosine_similarity(tfidf_matrix)
        self.cos_sim = cos_sim
        self.include_comparison = include_comparison
        return self

    def get_similar_documents(self, threshold: float = 0.5, include_comparison: bool = False
                          , remove_duplicates: bool = True, **kwargs) -> pd.DataFrame:
        """ Vyextrahuje dvojice podobných dokumentů na základě hranice podobnosti.

        Umožňuje odstranit duplicitní dvojice např. dvojice dokument1 a dokument2 je stejná jako dokument2 a dokument1.

        :param threshold: hranice podobnosti (hodnoty 0-1), nad kterou chceme vyextrahovat podobné dokumenty
        :param include_comparison: zahrne porovnávané (kontrolované) dokumenty k referenčním
        :param remove_duplicates: odstraní duplicitní dvojice
        :return: dvojice podobných dokumentů (repreznetované jako ID) a skóre podobnosti
        """

        self.create_similarity(include_comparison, **kwargs)
        cos_sim_sorted = self.cos_sim.argsort()[::-1]

        comparison_ids_col = self.corpus_comparison.columns[0]
        comparison_ids = self.corpus_comparison[comparison_ids_col].tolist()

        if self.corpus_reference is not None:

            reference_ids_col = self.corpus_reference.columns[0]

            if self.include_comparison:
                reference_ids = self.corpus_reference[reference_ids_col].tolist()
                reference_ids = comparison_ids + reference_ids
            else:
                reference_ids = self.corpus_reference[reference_ids_col].tolist()
        else:
            reference_ids = comparison_ids

        dokument_id1 = []
        dokument_id2 = []
        score = []

        for index, array in enumerate(cos_sim_sorted):
            for item in array:
                sim_score = self.cos_sim[index, item]
                if sim_score >= threshold:
                    id1 = comparison_ids[index]
                    id2 = reference_ids[item]
                    if id1 != id2:
                        dokument_id1.append(id1)
                        dokument_id2.append(id2)
                        score.append(sim_score)

        similar_documents = pd.DataFrame({
            'id1': dokument_id1,
            'id2': dokument_id2,
            'score': score
        })

        similar_documents = similar_documents.sort_values('score', ascending=False).reset_index(drop=True)

        if remove_duplicates:
            similar_documents = self._remove_duplicate_pairs(similar_documents)

        self.threshold = threshold
        self.similar_documents = similar_documents
        return self.similar_documents

    def _remove_duplicate_pairs(self, similar_documents):
        """ Odstraní duplicitní dvojice, kde např. dokument1 a dokument2 je stejné jako dokument2 a dokument1.

        :param similar_documents: dvojice podobných dokumenty
        :return: vyčištěné dvojice podobných dokumentů
        """

        sorted_similar_documents = similar_documents[['id1', 'id2']].apply(lambda x: sorted(x), axis=1)
        sorted_similar_documents = sorted_similar_documents.drop_duplicates().index
        similar_documents = similar_documents[similar_documents.index.isin(sorted_similar_documents)].reset_index(drop=True)
        return similar_documents

    def add_info(self, comparison_info: pd.DataFrame, reference_info: pd.DataFrame = None) -> pd.DataFrame:
        """ Přidá k dvojicím podobných dokumentů další informace (např. název a cíle projektu, stavy projektů atd.).

        :param comparison_info: informace o kontrolovaných dokumentech
        :param reference_info: informace o referenčních dokumentech
        :return: dvojice podobných projektů včetně dalších informací
        """

        similar_documents = self.similar_documents

        if reference_info is None:
            reference_info = comparison_info

        comparison_info_col = comparison_info.columns[0]
        reference_info_col = reference_info.columns[0]

        reference_info = reference_info.rename(columns={reference_info_col: comparison_info_col})

        if self.include_comparison:
            reference_info = pd.concat([comparison_info, reference_info])
            reference_info = reference_info.drop_duplicates(subset=[comparison_info_col])

        merged_info = pd.merge(similar_documents, comparison_info, how='left', left_on='id1'
                               , right_on=comparison_info_col, suffixes=('_1', '_2'))
        merged_info = merged_info.drop(columns=[comparison_info_col])
        merged_info = pd.merge(merged_info, reference_info, how='left', left_on='id2'
                               , right_on=comparison_info_col, suffixes=('_1', '_2'))
        merged_info = merged_info.drop(columns=[comparison_info_col])

        return merged_info


def find_project_code(text: str, prog_select: str | list = None) -> list:
    """ Vyhledá v textu kódy projektů.

    :param text: vstupní text
    :param prog_select: kód programu nebo list kódů programů, jejichž projekty nás specificky zajímají
    :return: list kódů projektů v textu
    """

    projects = re.findall('\w{2}\d{6,8}', text)

    if prog_select is not None:
        if isinstance(prog_select, list):
            projects = [proj for proj in projects if proj[:2] in prog_select]
        elif isinstance(prog_select, str):
            prog_select = [prog_select]
            projects = [proj for proj in projects if proj[:2] in prog_select]

    return projects
