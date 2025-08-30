import math
import statistics
from collections import Counter
from time import time

from more_itertools import chunked
from spacy.language import Language
from spacy.tokens import Doc


class LexicalDiversityIndices:
    """
    This class will handle all operations to obtain the lexical diversity indices of a text according to Coh-Metrix
    """

    name = "lexical_diversity_indices"

    def __init__(self, nlp: Language) -> None:
        """
        The constructor will initialize this object that calculates the lexical diversity indices for a specific language of those that are available.
        It needs the following pipes to be added before it: Content word identifier, alphanumeric word identifier and informative word tagger.

        Parameters:
        nlp: The spacy model that corresponds to a language.

        Returns:
        None.
        """
        required_pipes = [
            "content_word_identifier",
            "alphanumeric_word_identifier",
            "informative_word_tagger",
        ]
        if not all((pipe in nlp.pipe_names for pipe in required_pipes)):
            message = (
                "Lexical diversity indices pipe need the following pipes: "
                + ", ".join(required_pipes)
            )
            raise AttributeError(message)

        self._nlp = nlp
        self._mltd_segment_size = 100
        Doc.set_extension("lexical_diversity_indices", default=dict())  # Dictionary

    def __call__(self, doc: Doc) -> Doc:
        """
        This method will calculate the lexical diversity indices.

        Parameters:
        doc(Doc): A Spacy document.

        Returns:
        Doc: The processed doc.
        """
        if len(doc.text) == 0:
            raise ValueError("The text is empty.")

        print("Analyzing lexical diversity indices")
        start = time()
        doc._.lexical_diversity_indices["LDTTRa"] = (
            self.__get_type_token_ratio_between_all_words(doc)
        )
        doc._.lexical_diversity_indices["LDTTRcw"] = (
            self.__get_type_token_ratio_of_content_words(doc)
        )
        doc._.lexical_diversity_indices["LDTTRno"] = (
            self.__get_type_token_ratio_of_nouns(doc)
        )
        doc._.lexical_diversity_indices["LDTTRvb"] = (
            self.__get_type_token_ratio_of_verbs(doc)
        )
        doc._.lexical_diversity_indices["LDTTRadv"] = (
            self.__get_type_token_ratio_of_adverbs(doc)
        )
        doc._.lexical_diversity_indices["LDTTRadj"] = (
            self.__get_type_token_ratio_of_adjectives(doc)
        )
        doc._.lexical_diversity_indices["LDTTRLa"] = (
            self.__get_type_token_ratio_between_all_lemma_words(doc)
        )
        doc._.lexical_diversity_indices["LDTTRLno"] = (
            self.__get_type_token_ratio_of_lemma_nouns(doc)
        )
        doc._.lexical_diversity_indices["LDTTRLvb"] = (
            self.__get_type_token_ratio_of_lemma_verbs(doc)
        )
        doc._.lexical_diversity_indices["LDTTRLadv"] = (
            self.__get_type_token_ratio_of_lemma_adverbs(doc)
        )
        doc._.lexical_diversity_indices["LDTTRLadj"] = (
            self.__get_type_token_ratio_of_lemma_adjectives(doc)
        )
        doc._.lexical_diversity_indices["LDMLTD"] = self.__calculate_mltd(doc)
        doc._.lexical_diversity_indices["LDVOCd"] = self.__calculate_vocd(doc)
        doc._.lexical_diversity_indices["LDMaas"] = self.__calculate_maas(doc)
        doc._.lexical_diversity_indices["LDDno"] = self.__get_noun_density(doc)
        doc._.lexical_diversity_indices["LDDvb"] = self.__get_verb_density(doc)
        doc._.lexical_diversity_indices["LDDadv"] = self.__get_adverb_density(doc)
        doc._.lexical_diversity_indices["LDDadj"] = self.__get_adjective_density(doc)
        end = time()
        print(f"Lexical diversity indices analyzed in {end - start} seconds.")
        return doc

    def __calculate_maas(self, doc: Doc) -> float:
        """
        This method return the Maas' index of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The Maas' index of a text.
        """
        n = doc._.alpha_words_count
        v = doc._.alpha_words_different_count
        return 0 if v == 1 else (math.log10(n) - math.log10(v)) / math.log10(v) ** 2

    def __calculate_mltd(self, doc: Doc) -> float:
        """
        This method return the Measure of Textual Lexical Diversity (MLTD) of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The Measure of Textual Lexical Diversity (MLTD) of a text.
        """
        segments = [
            words for words in chunked(doc._.alpha_words, self._mltd_segment_size)
        ]
        unique_words = [
            len(set([word.text.lower() for word in words])) for words in segments
        ]
        return doc._.alpha_words_count / statistics.mean(unique_words)

    def __calculate_vocd(self, doc: Doc) -> float:
        """
        This method return the Vocabulary Complexity Diversity (VoCD) of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The Vocabulary Complexity Diversity (VoCD) of a text.
        """
        freq_counter = Counter()
        for unique_word in doc._.alpha_words_different:
            for word in doc._.alpha_words:
                freq_counter[word.text.lower()] += 1

        return doc._.alpha_words_count**2 / sum(
            [count**2 for count in freq_counter.values()]
        )

    def __get_type_token_ratio_between_all_words(self, doc: Doc) -> float:
        """
        This method returns the type token ratio between all words of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between all words of a text.
        """
        return (
            0
            if doc._.alpha_words_count == 0
            else doc._.alpha_words_different_count / doc._.alpha_words_count
        )

    def __get_type_token_ratio_of_content_words(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of content words of a text. Content words are nouns, verbs, adjectives and adverbs.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the content words of a text.
        """
        return (
            0
            if doc._.content_words_count == 0
            else doc._.content_words_different_count / doc._.content_words_count
        )

    def __get_type_token_ratio_of_nouns(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of nouns of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the nouns of a text.
        """
        return (
            0
            if doc._.nouns_count == 0
            else len(set([word.text.lower() for word in doc._.nouns]))
            / doc._.nouns_count
        )

    def __get_type_token_ratio_of_verbs(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of verbs of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the verbs of a text.
        """
        return (
            0
            if doc._.verbs_count == 0
            else len(set([word.text.lower() for word in doc._.verbs]))
            / doc._.verbs_count
        )

    def __get_type_token_ratio_of_adverbs(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of adverbs of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the adverbs of a text.
        """
        return (
            0
            if doc._.adverbs_count == 0
            else len(set([word.text.lower() for word in doc._.adverbs]))
            / doc._.adverbs_count
        )

    def __get_type_token_ratio_of_adjectives(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of adjectives of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the adjectives of a text.
        """
        return (
            0
            if doc._.adjectives_count == 0
            else len(set([word.text.lower() for word in doc._.adjectives]))
            / doc._.adjectives_count
        )

    def __get_type_token_ratio_between_all_lemma_words(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of all lemma words of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between all lemma words of a text.
        """
        return (
            0
            if doc._.alpha_words_count == 0
            else len(set([word.lemma_ for word in doc._.alpha_words]))
            / doc._.alpha_words_count
        )

    def __get_type_token_ratio_of_lemma_nouns(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of lemma nouns of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the lemma nouns of a text.
        """
        return (
            0
            if doc._.nouns_count == 0
            else len(set([word.lemma_ for word in doc._.nouns])) / doc._.nouns_count
        )

    def __get_type_token_ratio_of_lemma_verbs(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of lemma verbs of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the lemma verbs of a text.
        """
        return (
            0
            if doc._.verbs_count == 0
            else len(set([word.lemma_ for word in doc._.verbs])) / doc._.verbs_count
        )

    def __get_type_token_ratio_of_lemma_adverbs(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of lemma adverbs of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the lemma adverbs of a text.
        """
        return (
            0
            if doc._.adverbs_count == 0
            else len(set([word.lemma_ for word in doc._.adverbs])) / doc._.adverbs_count
        )

    def __get_type_token_ratio_of_lemma_adjectives(self, doc: Doc) -> float:
        """
        This method returns the type token ratio of lemma adjectives of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the lemma adjectives of a text.
        """
        return (
            0
            if doc._.adjectives_count == 0
            else len(set([word.lemma_ for word in doc._.adjectives]))
            / doc._.adjectives_count
        )

    def __get_noun_density(self, doc: Doc) -> float:
        """
        This method returns the noun density of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the content words of a text.
        """
        return (
            0 if doc._.nouns_count == 0 else doc._.nouns_count / doc._.alpha_words_count
        )

    def __get_verb_density(self, doc: Doc) -> float:
        """
        This method returns the verb density of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the content words of a text.
        """
        return (
            0
            if doc._.verbs_count == 0
            else doc._.verbs_count / doc._.content_words_count
        )

    def __get_adverb_density(self, doc: Doc) -> float:
        """
        This method returns the adverb density of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the content words of a text.
        """
        return (
            0
            if doc._.adverbs_count == 0
            else doc._.adverbs_count / doc._.content_words_count
        )

    def __get_adjective_density(self, doc: Doc) -> float:
        """
        This method returns the adjective density of a text.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        float: The type token ratio between the content words of a text.
        """
        return (
            0
            if doc._.adjectives_count == 0
            else doc._.adjectives_count / doc._.content_words_count
        )
