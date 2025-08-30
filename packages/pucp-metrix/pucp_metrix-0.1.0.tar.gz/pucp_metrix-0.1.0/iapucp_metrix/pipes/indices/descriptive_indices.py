import statistics
from time import time
from typing import Callable

from spacy.language import Language
from spacy.tokens import Doc

from iapucp_metrix.utils.statistics_results import StatisticsResults


class DescriptiveIndices:
    """
    This class will handle all operations to obtain the descriptive indices of a text according to Coh-Metrix
    """

    def __init__(self, nlp: Language) -> None:
        """
        The constructor will initialize the extensions where to hold the descriptive indices of a doc. It needs the following pipes to be added before it: 'alphanumeric_word_identifier', 'paragraphizer', 'syllablelizer'

        Parameters:
        nlp(Lanuage): The spacy model that corresponds to a language.
        language(str): The language that the texts to process will have.

        Returns:
        None.
        """
        required_pipes = [
            "alphanumeric_word_identifier",
            "paragraphizer",
            "syllablelizer",
        ]
        if not all((pipe in nlp.pipe_names for pipe in required_pipes)):
            message = "Descriptive indices pipe need the following pipes: " + ", ".join(
                required_pipes
            )
            raise AttributeError(message)

        self._nlp = nlp
        Doc.set_extension("descriptive_indices", default=dict())  # Dictionary

    def __call__(self, doc: Doc) -> Doc:
        """
        This method will calculate the descriptive indices.

        Parameters:
        doc(Doc): A Spacy document.

        Returns:
        Doc: The processed doc.
        """
        if len(doc.text) == 0:
            raise ValueError("The text is empty.")

        print("Analyzing descriptive indices")
        start = time()
        doc._.descriptive_indices["DESPC"] = doc._.paragraph_count
        doc._.descriptive_indices["DESSC"] = doc._.sentence_count
        doc._.descriptive_indices["DESWC"] = doc._.alpha_words_count
        self.__get_length_of_paragraphs(doc)
        self.__get_length_of_sentences(doc)
        self.__get_syllables_per_word(doc)
        self.__get_length_of_words(doc)
        end = time()
        print(f"Descriptive indices analyzed in {end - start} seconds.")
        return doc

    def _get_mean_std_of_metric(
        self, doc: Doc, counter_function: Callable, statistic_type: str = "all"
    ) -> StatisticsResults:
        """
        This method returns the mean and/or standard deviation of a descriptive metric.

        Parameters:
        doc(Doc): The text to be anaylized.
        counter_function(Callable): This callable will calculate the values to add to the counter array in order to calculate the standard deviation. It receives a Spacy Doc and it should return a list or number.
        statistic_type(str): Whether to calculate the mean and/or the standard deviation. It accepts 'mean', 'std' or 'all'.

        Returns:
        StatisticsResults: The mean and/or standard deviation of the current metric.
        """
        if len(doc.text) == 0:
            raise ValueError("The text is empty.")
        elif statistic_type not in ["mean", "std", "all"]:
            raise ValueError("'statistic_type' can only take 'mean', 'std' or 'all'.")
        else:
            counter = counter_function(doc)  # Find the values to add to the counter
            stat_results = StatisticsResults()
            # Calculate the statistics
            if statistic_type in ["std", "all"]:
                stat_results.std = statistics.pstdev(counter)

            if statistic_type in ["mean", "all"]:
                stat_results.mean = statistics.mean(counter)

            return stat_results

    def __get_length_of_paragraphs(self, doc: Doc) -> None:
        """
        This method calculates the average amount and standard deviation of sentences in each paragraph.

        Parameters:
        doc(doc): The text to be anaylized.
        """

        count_length_of_paragraphs = lambda complete_text: [
            para._.sentence_count for para in complete_text._.paragraphs
        ]
        metrics = self._get_mean_std_of_metric(
            doc, counter_function=count_length_of_paragraphs, statistic_type="all"
        )
        doc._.descriptive_indices["DESPL"] = metrics.mean
        doc._.descriptive_indices["DESPLd"] = metrics.std

    def __get_length_of_sentences(self, doc: Doc) -> None:
        """
        This method calculate the average amount and standard deviation of words in each sentence.

        Parameters:
        doc(Doc): The text to be anaylized.
        """
        count_length_of_sentences = lambda complete_text: [
            sentence._.alpha_words_count
            for sentence in complete_text._.non_empty_sentences
        ]

        metrics = self._get_mean_std_of_metric(
            doc, counter_function=count_length_of_sentences, statistic_type="all"
        )
        doc._.descriptive_indices["DESSL"] = metrics.mean
        doc._.descriptive_indices["DESSLd"] = metrics.std

    def __get_length_of_words(self, doc: Doc) -> None:
        """
        This method calculates the average amount and standard deviation of letters in each word.

        Parameters:
        doc(Doc): The text to be anaylized.
        """
        count_letters_per_word = lambda complete_text: [
            len(token) for token in complete_text._.alpha_words
        ]

        metrics = self._get_mean_std_of_metric(
            doc, counter_function=count_letters_per_word, statistic_type="all"
        )
        doc._.descriptive_indices["DESWLlt"] = metrics.mean
        doc._.descriptive_indices["DESWLltd"] = metrics.std

    def __get_syllables_per_word(self, doc: Doc) -> StatisticsResults:
        """
        This method calculates the average amount and standard deviation of syllables in each word.

        Parameters:
        doc(Doc): The text to be anaylized.

        Returns:
        None
        """
        count_syllables_per_word = lambda doc: [
            token._.syllable_count
            for token in doc._.alpha_words
            if token._.syllables is not None
        ]

        metrics = self._get_mean_std_of_metric(
            doc, counter_function=count_syllables_per_word, statistic_type="all"
        )
        doc._.descriptive_indices["DESWLsy"] = metrics.mean
        doc._.descriptive_indices["DESWLsyd"] = metrics.std

