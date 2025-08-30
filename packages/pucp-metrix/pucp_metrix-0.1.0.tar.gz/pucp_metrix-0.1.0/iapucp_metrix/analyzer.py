from typing import List

import spacy
from spacy.tokens import Doc

import iapucp_metrix.pipes.factory


class Analyzer:
    def __init__(self, paragraph_delimiter: str = "\n\n"):
        self._nlp = spacy.load("es_core_news_lg")

        self._nlp.add_pipe("sentencizer")
        self._nlp.add_pipe(
            "paragraphizer", config={"paragraph_delimiter": paragraph_delimiter}
        )
        self._nlp.add_pipe("alphanumeric_word_identifier")
        self._nlp.add_pipe("syllablelizer", config={"language": "es"})
        self._nlp.add_pipe("informative_word_tagger")
        self._nlp.add_pipe("descriptive_indices")
        self._nlp.add_pipe("content_word_identifier")
        self._nlp.add_pipe("readability_indices")
        self._nlp.add_pipe("noun_phrase_tagger")
        self._nlp.add_pipe("words_before_main_verb_counter")
        self._nlp.add_pipe("syntactic_complexity_indices")
        self._nlp.add_pipe("verb_phrase_tagger")
        self._nlp.add_pipe("negative_expression_tagger")
        self._nlp.add_pipe("syntactic_pattern_density_indices")
        self._nlp.add_pipe("causal_connectives_tagger")
        self._nlp.add_pipe("logical_connectives_tagger")
        self._nlp.add_pipe("adversative_connectives_tagger")
        self._nlp.add_pipe("temporal_connectives_tagger")
        self._nlp.add_pipe("additive_connectives_tagger")
        self._nlp.add_pipe("connective_indices")
        self._nlp.add_pipe("cohesion_words_tokenizer")
        self._nlp.add_pipe("referential_cohesion_indices")
        self._nlp.add_pipe("semantic_cohesion_indices")
        self._nlp.add_pipe("lexical_diversity_indices")
        self._nlp.add_pipe("word_information_indices")
        self._nlp.add_pipe("textual_simplicity_indices")
        self._nlp.add_pipe("word_frequency_indices")
        self._nlp.add_pipe("wrapper_serializer", last=True)

    def analyze(self, texts: List[str]) -> list[Doc]:
        """Analyze a text.

        text(str): The text to analyze.
        RETURNS (Doc): The analyzed text.
        """
        doc = self._nlp.pipe(texts)
        return doc
