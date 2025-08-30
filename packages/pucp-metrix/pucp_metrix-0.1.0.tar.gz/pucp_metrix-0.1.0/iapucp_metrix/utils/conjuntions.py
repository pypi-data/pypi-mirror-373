from itertools import islice

import numpy as np
import spacy
from datasets import load_dataset


def calculate_sentence_ranges(nlp, texts: list[str]):
    nlp.add_pipe("sentencizer")
    docs = nlp.pipe(texts)

    sentence_lengths = []
    for doc in docs:
        for sent in doc.sents:
            words = [token for token in sent if not token.is_punct]
            sentence_lengths.append(len(words))

    mean_length = np.mean(sentence_lengths)
    std_dev = np.std(sentence_lengths)
    median_length = np.median(sentence_lengths)
    percentiles = np.percentile(sentence_lengths, [25, 50, 75])

    print(f"Longitud media de las sentencias: {mean_length:.2f} palabras")
    print(f"Desviación estándar: {std_dev:.2f}")
    print(f"Mediana de la longitud de las sentencias: {median_length}")
    print(f"Percentiles 25, 50, 75: {percentiles}")

    short_threshold = percentiles[0]  # Percentil 25
    medium_threshold = percentiles[1]  # Percentil 50 (mediana)
    long_threshold = percentiles[2]  # Percentil 75

    return {
        "short_threshold": short_threshold,
        "medium_threshold": medium_threshold,
        "long_threshold": long_threshold,
    }


# Cargar el modelo (puedes cambiar por 'en_core_web_sm' para inglés)
nlp = spacy.load("es_core_news_lg")

# Cargar una fracción del dataset (puedes ajustar el tamaño)
dataset = load_dataset("crscardellino/spanish_billion_words")

# Combinar textos (puedes tomar más si quieres más precisión)
texts = [entry["text"] for entry in islice(dataset["train"], 10000)]

print("Textos cargados:")
print(texts[:5])

calculate_sentence_ranges(nlp, texts)
