########################################################################################################################
# IMPORTS

import logging
import warnings
from typing import List, Optional


class PiiDependenciesMissingError(ImportError):
    pass


class SpacyModelNotFoundError(ImportError):
    pass


try:
    import phonenumbers
    import spacy
    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_analyzer.predefined_recognizers import PhoneRecognizer
    from presidio_anonymizer import AnonymizerEngine
    from spacy.language import Language
    from spacy_langdetect import LanguageDetector
except ImportError as e:
    raise PiiDependenciesMissingError(
        "One or more PII anonymization dependencies are missing. "
        "Please install them by running: pip install datamarket[pii]\n"
        f"Original error: {e}"
    ) from e


########################################################################################################################
# SETTINGS

logger = logging.getLogger()
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

warnings.filterwarnings(
    "ignore",
    message=r"\[W108\]",
    category=UserWarning,
    module="spacy.pipeline.lemmatizer",
)


@Language.factory("language_detector")
def get_lang_detector(nlp, name):
    return LanguageDetector()


########################################################################################################################
# CLASSES


class PiiAnonymizer:
    SUPPORTED_LANG = ["es", "en"]

    def __init__(self):
        # Check for required spaCy models
        required_models = {
            "en_core_web_md": "python -m spacy download en_core_web_md",
            "es_core_news_md": "python -m spacy download es_core_news_md",
        }
        missing_models_instructions = []
        for model_name, install_command in required_models.items():
            if not spacy.util.is_package(model_name):
                missing_models_instructions.append(
                    f"Model '{model_name}' not found. Please install it by running: {install_command}"
                )

        if missing_models_instructions:
            raise SpacyModelNotFoundError("\n".join(missing_models_instructions))

        self.anonymizer = AnonymizerEngine()
        self.analyzer = self._load_analyzer_engine()

        self.nlp = self._nlp()

    def _nlp(self) -> Language:
        analyzer_en_model = self.analyzer.nlp_engine.nlp.get("en")
        shared_vocab = analyzer_en_model.vocab
        nlp = spacy.blank("en", vocab=shared_vocab)

        if nlp.has_factory("sentencizer"):
            nlp.add_pipe("sentencizer")

        if nlp.has_factory("language_detector"):
            nlp.add_pipe("language_detector", last=True)

        return nlp

    @staticmethod
    def _nlp_config():
        return {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "es", "model_name": "es_core_news_md"},
                {"lang_code": "en", "model_name": "en_core_web_md"},
            ],
        }

    def _load_analyzer_engine(self) -> AnalyzerEngine:
        provider = NlpEngineProvider(nlp_configuration=PiiAnonymizer._nlp_config())
        nlp_engine = provider.create_engine()
        phone_recognizer_es = PhoneRecognizer(
            supported_language="es",
            supported_regions=phonenumbers.SUPPORTED_REGIONS,
            context=["teléfono", "móvil", "número"],
        )
        registry = RecognizerRegistry(supported_languages=self.SUPPORTED_LANG)
        registry.load_predefined_recognizers(nlp_engine=nlp_engine, languages=self.SUPPORTED_LANG)
        registry.add_recognizer(phone_recognizer_es)

        analyzer = AnalyzerEngine(
            registry=registry,
            nlp_engine=nlp_engine,
            supported_languages=self.SUPPORTED_LANG,
        )
        return analyzer

    def detect_lang(self, text: str) -> str:
        if hasattr(self, "nlp") and self.nlp:
            with self.nlp.select_pipes(enable=["tokenizer", "sentencizer", "language_detector"]):
                doc = self.nlp(text)
            return doc._.language["language"]
        else:
            logger.error("Language detection NLP model not initialized. Cannot detect language.")
            return "unknown"

    def anonymize_text(
        self,
        text: str,
        entities: Optional[List[str]] = None,
        lang: str = "unknown",
    ) -> str:
        if lang == "unknown":
            lang = self.detect_lang(text)
            if lang not in self.SUPPORTED_LANG:
                logger.warning(f"Support for language {lang} is not implemented yet! Fail safe to empty string.")
                return ""
        elif lang not in self.SUPPORTED_LANG:
            logger.warning(f"Support for language {lang} is not implemented yet! Fail safe to empty string.")
            return ""

        analyzer_result = self.analyzer.analyze(
            text=text,
            entities=entities,
            language=lang,
        )
        anonymizer_result = self.anonymizer.anonymize(text=text, analyzer_results=analyzer_result)
        return anonymizer_result.text
