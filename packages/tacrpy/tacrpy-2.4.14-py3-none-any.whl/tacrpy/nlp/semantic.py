"""
Modul pro vytváření sémantických embeddingů a dalších funkcí.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

import nltk
nltk.download("punkt")

from nltk import tokenize


def get_embeddings(text: str, model: SentenceTransformer, sent_tokenize: bool = True) -> np.ndarray:
    """Převede text na sémantické embeddingy (vektor).

    Umožňuje převést kratší i delší text na embeddingy. Pokud je sent_tokenize True, tak nejdříve zákoduje jednotlivé \
    věty a pak jednotlivé věty zprůměruje k zákodování celého textu. V případě, že je False, tak zákoduje text jako \
    celek. Druhá varianta lépe zachytí celkový kontext, ale většina SentenceTransformer modelů umí najednou zpracovat \
    pouze určité množství tokenů (např. 128 tokenů, což to odpovídá cca třem průměrným větám), po tomto množství \
    kvalita klesá.

    :param text: text, který chceme zakódvat do embeddingů
    :param model: SentenceTransformer model, podle kterého se text zakóduje do embeddingů
    :param sent_tokenize: pokud je nastavený, tak nejdříve zakóduje jednotlivé věty a až pak celý text.
    :return: embeddingový vektor vstupního textu
    """

    if sent_tokenize:
        sentences = tokenize.sent_tokenize(text)
        sentence_embeddings = [model.encode(sent) for sent in sentences]
        doc_embedding = np.mean(sentence_embeddings, axis=0)
    else:
        doc_embedding = model.encode(text)

    return doc_embedding
