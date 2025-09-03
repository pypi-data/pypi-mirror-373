__all__ = ["nlp_instance"]

import subprocess


from typing import Optional, Literal, Any


class NlpInstance:
    spc: Any = None
    spc_model: str = None

    nltk_modules = {
        "stopwords": False,
        "wordnet": False,
        "cmudict": False,
        "punkt": False,
        "punkt_tab": False,
        "averaged_perceptron_tagger": False,
        "maxent_ne_chunker": False,
        "words": False,
        "maxent_ne_chunker_tab": False,
    }

    def __init__(self):
        self.is_initialized = False

    def initialize_spacy(
        self,
        model: Optional[
            Literal[
                "en_core_web_md",
                "en_core_web_lg",
            ]
        ] = None,
    ):
        import spacy

        try:
            if model is None:
                model = "en_core_web_md"
                if self.spc is None:
                    self.spc = spacy.load("en_core_web_md", disable=["parser", "ner"])
                    self.spc_model = "en_core_web_md"
                return

            if self.spc_model == model:
                return
            self.spc = spacy.load(model, disable=["parser", "ner"])
            self.spc_model = model
        except OSError:
            print("Model not found, trying to install it!")
            res = subprocess.run(
                f"python -m spacy download {model}",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

            self.spc = spacy.load(model, disable=["parser", "ner"])
            self.spc_model = model

    def initialize_nltk(
        self,
        module_name: Literal[
            "stopwords",
            "wordnet",
            "cmudict",
            "punkt",
            "punkt_tab",
            "averaged_perceptron_tagger",
            "maxent_ne_chunker",
            "words",
            "maxent_ne_chunker_tab",
            "all",
        ] = "all",
    ):
        import nltk

        # TODO: Make this as standard way to handle installation, remove the "all" from the list of options, thus saving space.
        # Removing the self.is_initialized and using 'nltk_modules' modules to check if they are already installled or not.
        if self.is_initialized:
            return
        for _nllib in [
            "stopwords",
            "wordnet",
            "cmudict",
            "punkt",
            "punkt_tab",
            "averaged_perceptron_tagger",
            "maxent_ne_chunker",
            "words",
            "maxent_ne_chunker_tab",
        ]:
            nltk.download(_nllib, quiet=True)
        self.is_initialized = True


nlp_instance = NlpInstance()
