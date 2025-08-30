from spacy.language import Language
from spacy.tokens import Doc


class WrapperSerializer:
    """
    Pipe that serves to delete all extension attributes from the Documents and spans and tokens, storing the indices in a joined dictionary so spacy can serialize the Doc object when using multiprocessing. It's to be used as the last pipe.
    """

    def __init__(self, nlp: Language) -> None:
        """
        The pipe only receives the language and nothing more.
        """
        self._nlp = nlp
        Doc.set_extension("coh_metrix_indices", default={})

    def __call__(self, doc: Doc) -> Doc:
        """
        Method that creates a dummy doc.
        """
        # Save all indices into a single dictionary
        doc_new = Doc.from_docs([doc], exclude=["user_data"])
        doc_new._.coh_metrix_indices = {
            **doc._.descriptive_indices,
            **doc._.word_information_indices,
            **doc._.syntactic_pattern_density_indices,
            **doc._.syntactic_complexity_indices,
            **doc._.connective_indices,
            **doc._.lexical_diversity_indices,
            **doc._.readability_indices,
            **doc._.referential_cohesion_indices,
            **doc._.semantic_cohesion_indices,
            **doc._.textual_simplicity_indices,
            **doc._.word_frequency_indices,
        }

        return doc_new
