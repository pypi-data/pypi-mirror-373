import ast
import time
import deepl
import requests
from typing import List, Dict

import logging
from logutils import get_logger
from chatgpt_klient.client import LLMClient
import boto3
from botocore.exceptions import ClientError

from deep_translator import GoogleTranslator

from translator.consts import ENGINES, APP_NAME, GPT_ENGINES, FIXER_ENGINE, rgx_text
from translator.utils import (
    language_pair_is_available,
    get_language_code,
    build_chatgpt_translation_prompt,
    get_prompt_by_doctype,
    set_logger_verbosity,
    build_system_directive_batch_translation_no_context,
    structure_equals,
    get_subtree_from_path,
    insert_subtree_in_tree_path,
)
from translator.exceptions import (
    MalformedResponseError,
    NoAvailableEnginesError,
    NoTranslationError,
)

# text_trap = io.StringIO()
# sys.stdout = text_trap
# sys.stderr = text_trap
#
# sys.stdout = sys.__stdout__
# sys.stderr = sys.__stderr__

logger = get_logger(APP_NAME)


class Translator:
    def __init__(
        self,
        engine_list: List | None = None,
        verbosity=1,
        openai_key=None,
        deepl_key=None,
        aws_data: Dict | None = None,
    ):
        set_logger_verbosity(verbosity)
        if engine_list is None:
            self.engine_list = ENGINES
        else:
            self.engine_list = []
            for e in engine_list:
                if e in ENGINES:
                    self.engine_list.append(e)
                else:
                    logger.warning(f"Engine {e} is not supported")
        if "deepl" in self.engine_list:
            try:
                if deepl_key is None:
                    raise Exception("No DeepL key")
                self.deepl_translator = deepl.Translator(deepl_key)
            except Exception:
                logger.exception("Could not configure DeepL engine.")
                self.engine_list.remove("deepl")
        if "gpt3" in self.engine_list:
            try:
                if openai_key is None:
                    raise Exception("Can't use OpenAI services without an API key")
                self.chatgpt3 = LLMClient(
                    api_key=openai_key, model="gpt3.5-default"
                )
            except Exception as e:
                logger.exception(f"Could not configure GPT3 engine: {e}")
                self.engine_list.remove("gpt3")
        if "gpt4" in self.engine_list:
            try:
                if openai_key is None:
                    raise Exception("Can't use OpenAI services without an API key")
                self.chatgpt4 = LLMClient(api_key=openai_key, model="gpt4-default")
            except Exception as e:
                logger.exception(f"Could not configure GPT4 engine: {e}")
                self.engine_list.remove("gpt4")
        if "aws" in self.engine_list:
            if aws_data is None:
                logger.exception("Could not configure AWS engine.")
                self.engine_list.remove("aws")
            else:
                self.awstranslator = boto3.client(
                    service_name="translate",
                    use_ssl=True,
                    region_name=aws_data["region_name"],
                    aws_access_key_id=aws_data["aws_access_key_id"],
                    aws_secret_access_key=aws_data["aws_secret_access_key"],
                )

        if len(self.engine_list) == 0:
            raise NoAvailableEnginesError(
                "There seem to be no available translation engines"
            )

    def translate(
        self,
        text: str,
        input_lang: str,
        output_lang: str,
        retry_next_engine: bool = True,
        engine_index: int = 0,
        if_no_engines_untranslated: bool = True,
    ) -> str:
        """
        Translate text using any of the supported engines in UlionTse's "translators"
        library. The function automatically tries to do its best to normalize the
        language codes so that the user does not have to worry about that.
        """
        if rgx_text.match(text) is None:
            return text
        try:
            engine = self.get_engine(engine_index)
        except NoAvailableEnginesError as e:
            if logger.level == logging.DEBUG:
                logger.exception(
                    "No more available engines to perform the translation. Leaving "
                    "untranslated..."
                )
            else:
                logger.warning(
                    "No more available engines to perform the translation. Leaving "
                    "untranslated..."
                )
            if if_no_engines_untranslated:
                return text
            else:
                raise e
        try:
            if language_pair_is_available(engine, input_lang, output_lang) is False:
                logger.error(f"{input_lang}->{output_lang} unavailable for {engine}")
                raise Exception(f"{input_lang}->{output_lang} unavailable for {engine}")
            logger.debug(f"Translating text: '{text}")
            if engine == "deepl":
                r = self.deepl_translator.translate_text(
                    text, source_lang=input_lang, target_lang=output_lang
                ).text  # type: ignore
            elif engine == "gpt3":
                text = build_chatgpt_translation_prompt(text, input_lang, output_lang)
                r = self.chatgpt3.send_prompt(text, no_history=True)
            elif engine == "gpt4":
                text = build_chatgpt_translation_prompt(text, input_lang, output_lang)
                r = self.chatgpt4.send_prompt(text, no_history=True)
            elif engine == "google":
                r = translate_with_google(text, input_lang, output_lang)
            elif engine == "aws":
                r = self.translate_string_with_aws(text, input_lang, output_lang)
            else:
                import translators as ts

                r = ts.translate_text(
                    text,
                    translator=engine,
                    from_language=get_language_code(input_lang, engine),
                    to_language=get_language_code(output_lang, engine),
                )
            logger.info(f"Translation: '{r}' ({engine})")
            if type(r) is not str:
                logger.exception(
                    f"Here we should have a translated string, but instead we have: {r}"
                )
                raise Exception("Wrong returned type")
        except Exception as e:
            logger.exception(
                f"Error when trying to translate {input_lang}->{output_lang} using "
                f"{engine}"
            )
            if retry_next_engine:
                logger.info("Retrying with the next engine available...")
                engine_index += 1
                r = self.translate(
                    text=text,
                    input_lang=input_lang,
                    output_lang=output_lang,
                    retry_next_engine=retry_next_engine,
                    engine_index=engine_index,
                    if_no_engines_untranslated=if_no_engines_untranslated,
                )
            else:
                raise e
        if not isinstance(r, str):
            raise Exception(f"Returned object should be a string, but it is: {r}")
        return r

    def custom_translation(
        self,
        data: List,
        input_lang: str,
        output_lang: str,
        engine: str | int = 0,
        doctype: str | None = None,
    ):
        """
        Perform a translation of anything using ChatGPT. This function will take pass what is
        received in the "data" parameter and insert it in a ChatGPT prompt. Thus, te real relevant
        information for getting a good translation is in the prompt. The function can select one
        prompt or another depending on the type of document, and complete it with the origin and
        target languages.
        Data should be a Python data structure
        """
        engine = self.get_engine(engine)
        if engine == "gpt3":
            gpt_engine = self.chatgpt3
        elif engine == "gpt4":
            gpt_engine = self.chatgpt4
        else:
            raise Exception(
                f"Custom translation only allowed for LLM-based engines: {GPT_ENGINES}"
            )
        prompt = get_prompt_by_doctype(data, input_lang, output_lang, doctype)
        translation = gpt_engine.send_prompt(prompt)
        try:
            translation = ast.literal_eval(translation)
            translation = self.fix_translation(
                data, translation, src_lang=input_lang, dest_lang=output_lang
            )
        except Exception:
            logger.exception(f"Results are malformed and cannot be used: {translation}")
            raise MalformedResponseError("Malformed results from ChatGPT")
        return translation

    def batch_translate(
        self,
        texts: List[str],
        input_lang: str,
        output_lang: str,
        retry_next_engine: bool = True,
        if_no_engines_untranslated: bool = True,
    ):
        """
        Batch translation of a bunch of texts. This should grant a faster translation,
        reducing the overhead caused by the initialization processes.
        """
        engine = self.get_engine(0)
        translated_texts = []
        logger.debug(f"Starting context-free batch translation with {engine}")

        if engine in GPT_ENGINES:
            chatgpt = self.get_gpt_client(engine)
            sysdir = build_system_directive_batch_translation_no_context(
                input_lang, output_lang
            )
            chatgpt.set_system_directive(sysdir)
            translate_fn = lambda x: chatgpt.send_prompt(x, no_history=False)
        else:
            translate_fn = lambda x: self.translate(
                text=x,
                input_lang=input_lang,
                output_lang=output_lang,
                retry_next_engine=retry_next_engine,
                if_no_engines_untranslated=if_no_engines_untranslated,
            )
        translated_texts = translate_nested_lists(texts, translate_fn)
        logger.debug("Translations completed sucessfully")

        return translated_texts

    def get_engine(self, engine: str | int) -> str:
        if isinstance(engine, str):
            if engine not in self.engine_list:
                raise NoAvailableEnginesError(f"Engine {engine} not available")
        elif isinstance(engine, int):
            if engine >= len(self.engine_list):
                raise NoAvailableEnginesError("There are no more engines to try")
            else:
                engine = self.engine_list[engine]
        return engine

    def get_gpt_client(self, engine):
        if engine == "gpt3":
            return self.chatgpt3
        elif engine == "gpt4":
            return self.chatgpt4
        else:
            raise Exception(f"{engine} is not a valid GPT engine")

    def translate_string_with_aws(self, text: str, src_lang: str, trg_lang: str) -> str:
        delay = 1
        translated = False
        translation = None
        while not translated:
            try:
                translation = self.awstranslator.translate_text(
                    Text=text, SourceLanguageCode=src_lang, TargetLanguageCode=trg_lang
                )
                translated = True
            except ClientError:
                logger.warning(
                    "Too many translation petitions, delaying next one a little bit "
                    f"{delay}s"
                )
                time.sleep(delay)
                delay *= 2
                if delay >= 120:
                    logger.error("Having big problems with the AWS RateLimit")
                    break
        if translation is None:
            raise Exception("Translation failed")
        text = translation.get("TranslatedText")
        return text

    def fix_translation(self, original, translation, src_lang, dest_lang):
        """
        Given two structures of nested lists, where one is supposed to be the translated
        version of the other, check if there are any problems with the structures
        differing at any point. It if were so, fix the subtree by translating it the
        traditional way
        """
        i = 0
        self.engine_list.insert(0, FIXER_ENGINE)
        while True:
            r = structure_equals(original, translation)
            if r is True:
                break
            else:
                logger.info(f"Fixing translation, iteration {i}")
                st = get_subtree_from_path(original, r)
                st = self.batch_translate(
                    st, input_lang=src_lang, output_lang=dest_lang
                )
                insert_subtree_in_tree_path(translation, r, st)
                i += 1
        self.engine_list.pop(0)

        return translation


def translate_nested_lists(lst: List, translate_fn):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.append(translate_nested_lists(item, translate_fn))
        elif isinstance(item, str):
            if rgx_text.match(item) is None:
                r = item
            else:
                try:
                    r = translate_fn(item)
                except Exception:
                    logger.exception(
                        f"Something failed when translating this string: '{item}'"
                    )
                    r = item
            result.append(r)
        else:
            raise Exception(
                "Can only translate data structures formed by strings as terminal nodes"
            )
    return result


def translate_with_google(text: str, src_lang: str, trg_lang: str) -> str:
    """
    Peculiarity of Google includes that requests per second are limited to 5. Abusing
    this limit will imply a exception in the request. Thus, adding a little sleep timer
    is recommended
    """
    delay = 0.2
    translation = None
    while translation is None:
        try:
            translation = GoogleTranslator(source=src_lang, target=trg_lang).translate(
                text
            )
            if translation is None:
                raise NoTranslationError(
                    "Google returned a None instead of a translation"
                )
        except (AttributeError, requests.exceptions.SSLError):
            logger.warning(f"Retrying petition with a little delay: {delay}s")
            time.sleep(delay)
            delay *= 2
            if delay >= 10:
                logger.error("Having big problems with the Google rate limit")
                raise Exception("Translation failed")
    return translation
