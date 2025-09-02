from copy import deepcopy
import argparse
import logging
from collections import defaultdict
import translators as ts
from typing import List, Any
from translator.consts import (
    LANGUAGE_EQUIVALENCES,
    LANGUAGE_CODENAMES,
    APP_NAME,
    NO_TS_ENGINES,
    ENGINES
)

from logutils import get_logger


logger = get_logger("translator_cli")


def get_language_code(lang: str, engine: str) -> str:
    """
    Provide the desired language as a 2-letter code and then a tranlation engine.
    If the language is supported by the engine by another identificator (for example
    "spa" or "Spanish" instead of the standard "es"), this function will return the
    equivalent codification for that engine.
    Else, if the engine uses the standard code or maybe it doesn't support the
    language, the 2-letter standard code provided will be returned unchanged.
    Thus, this function should not be used to check if a language is supported by an
    engine or not.
    """
    try:
        return LANGUAGE_EQUIVALENCES[lang][engine]
    except Exception:
        return lang


def language_pair_is_available(engine: str, input_lang: str, output_lang: str) -> bool:
    if engine in NO_TS_ENGINES:
        return True
    input_lang = get_language_code(input_lang, engine)
    output_lang = get_language_code(output_lang, engine)
    d = ts.get_languages(engine)
    if input_lang in d.keys():
        if output_lang in d[input_lang]:
            logger.debug(
                f"Language pair {input_lang} -> {output_lang} available for {engine}"
            )
            return True
    logger.debug(
        f"Language pair {input_lang} -> {output_lang} not available for {engine}"
    )
    return False


def build_chatgpt_translation_prompt(
    text: str, input_lang: str, output_lang: str
) -> str:
    input_lang = LANGUAGE_CODENAMES[input_lang]
    output_lang = LANGUAGE_CODENAMES[output_lang]

    prompt_v1 = (
        f"Translate the following text I am going to provide in the line below from {input_lang} to {output_lang}. "
        "Limit your response to the translated text, without adding anything else, such as additional text or "
        "surrounding quotes."
        f"{text}"
    )

    return prompt_v1


def get_prompt_for_list_of_strings(
    texts: List[str], input_lang: str, output_lang: str
) -> str:
    input_lang = LANGUAGE_CODENAMES[input_lang]
    output_lang = LANGUAGE_CODENAMES[output_lang]

    prompt_v1 = (
        "I am going to provide you with a list of strings in Python format. I want you to translate them all from "
        f"{input_lang} to {output_lang}. They are all part of the same, unique text, and correctly sorted, so you should "
        "make the translation treating the strings as part of a single document, sharing a common context."
        "For the output, I want you to keep the original format and return a Python list of strings that should "
        "be similar to the one provided as input. Both should have the exact same number of elements. "
        "Nested sublists may appear, in which case you must just translate the strings while preserving the original structure. "
        "Output list should be in the regular Python list format: ['a', 'b', 'c'...]. Do not include "
        "any additional text or any other addition other than the mere list of translated strings. "
        "Below this line there are several examples of the kind of input I will be providing and the output I would expect. "
        "Examples are formed by 3 lines: the first one will contain a prompt detailing the pair of languages, like "
        "'Example 2: English to Spanish'. The second line will contain the input list. The third line will contain the output "
        "list. After the examples and two linebreaks, comes the real input you have to translate."
        "\nExample 1: English to Catalan"
        '\n["The spider was weaving", "a dark, intricate web", "to catch a poor old fly."]'
        '\n["L\'aranya estava teixint", "una teranyina fosca i intrincada", "per atrapar a una pobra mosca."]'
        "\nExample 2: English to Spanish"
        '\n["The spider was weaving", "a dark, intricate web", "to catch a poor old fly."]'
        '\n["La araña estaba tejiendo", "una telaraña oscura e intrincada", "para atrapar a una pobre mosca."]'
        "\nExample 3: Spanish to English"
        "\n[['Hola, me llamo', 'José Bonaparte, emperador de las', 'Dos Sicilias y las Islas del', 'Verano, alla donde el sol', 'nunca se pone.'], ['José Bonaparte', 'le gusta', 'Nintendo']]"
        "\n[['Hello, my name is', 'Joseph Bonaparte, emperor of', 'the Two Sicilies and the Summer', 'Isles, where the sun', 'never sets.'], ['Joseph Bonaparte', 'likes', 'Nintendo']]"
        f"\n\n{texts}"
    )
    logger.debug(prompt_v1)
    return prompt_v1


def get_prompt_for_ppts(texts: List[str], input_lang: str, output_lang: str) -> str:
    input_lang = LANGUAGE_CODENAMES[input_lang]
    output_lang = LANGUAGE_CODENAMES[output_lang]

    prompt_v1 = (
        "I am going to provide you with a data structure of Python nested lists representing the contents of a PowerPoint PPT presentation. "
        "Elements in the outer list represent the different slides in the presentation. The lists in the second level are the different shapes. "
        "Third level corresponds to paragraphs within each shape. Finally, fourth level contains the different text elements that form a paragraph. "
        f"What I want you to do is to translate all the strings contained in this structure from {input_lang} to {output_lang} while maintaining the "
        "exact same structure so I can then rebuild the translated PPT file. You should return the structure of nested lists without adding anything else "
        "to your prompt. Make sure that each of the nested lists is the same length as the original one. Never, under any concept, alter the number of elements "
        f"in any of the nested lists. Strings in languages different that {input_lang} "
        "should not be translated. Of course, all the text in the presentation belongs to the same context and probably shares a common topic. Furthermore, "
        "contents within the same slide will probably be more closely related to each other than "
        "those in different slides; contents sharing a shape will be even more related, and so on. Now I will provide you several examples of what I want you "
        "to do. Each will have 3 lines: first one will be an informative header, indicating the origin and target languages. Second line will be the input I "
        "would be providing. Third line would be the translated content you should be generating. After the examples, and separated by two linebreaks, I "
        f"will present the real task in two lines. First, one header line like 'Input: {input_lang} to {output_lang}'. Second, the real PPT structure you "
        "must translate."
        f"\nExample: English to Spanish"
        "\n[[[['Advances in Live Student Annotations']], [[]]], [[['Opencast']], [['Opencast:'], ['Implemented in Opencast 2.3.0'], ['Also tested in Opencast 2.3.1 ']]], [[['Get events']], [['Added Annotations Endpoint to External API:'], ['Control access to endpoint with roles'], ['Return events that user has permission to read/view'], ['Check event’s roles and user’s roles'], ['Implemented start and end date filters']]], [[['Obtain & store annotations']], [['Used deprecated Opencast Annotations:'], ['Added as private ', 'annotations'], ['System of super annotations for highlighted videos'], []]]]"
        "\n[[[['Avances en Anotaciones en Vivo de Estudiantes']], [[]]], [[['Opencast']], [['Opencast:'], ['Implementado en Opencast 2.3.0'], ['También probado en Opencast 2.3.1 ']]], [[['Obtener eventos']], [['Añadido un endpoint de Anotaciones a la API externa:'], ['Controlar el acceso al endpoint mediante roles'], ['Devolver eventos para los que el usuario tiene permiso de lectura/visualización'], ['Comprobar roles de evento y roles de usuario'], ['Implementados filtros de fecha de inicio y fin']]], [[['Obtener y guardar anotaciones']], [['Anotaciones Opencast obsoletas usadas:'], ['Añadidas como ', 'anotaciones privadas'], ['Sistema de super anotaciones para los vídeos destacados'], []]]]"
        f"\nExample: Spanish to English"
        "\n[[[['Árbol de la manzana', 'crece fuerte', 'en la helada colina'], [], [], [], [], [], [], [], [], [], [], ['Roberto libertad'], []], [[], [], [], ['Quiero caramelos para mi cumple']]]]"
        "\n[[[['Apple tree', 'grows strong', 'in the frozen hill'], [], [], [], [], [], [], [], [], [], [], ['Free Roberto'], []], [[], [], [], ['I want candy for my birthday']]]]"
        f"\n\nInput: {input_lang} to {output_lang}"
        f"\n{texts}"
        ""
    )
    logger.debug(prompt_v1)
    return prompt_v1


def build_system_directive_batch_translation_no_context(
    input_lang: str, output_lang: str
) -> str:
    logger.debug("Building system directive for GPT context-free batch translation")
    input_lang = LANGUAGE_CODENAMES[input_lang]
    output_lang = LANGUAGE_CODENAMES[output_lang]
    prompt_v1 = (
        "In the next several prompts I am going to provide you with several texts that I need you to translate. "
        "Please, make sure that the following requirements are fulfilled:"
        f"\n- Output will be the input text translated from {input_lang} to {output_lang}."
        "\n- Output should consist in just the translated text, without any further addition of text alien to the input prompt, quotes, etc."
        "\n- Do NOT take the previous prompts in account when translating the current prompt."
        "\nBelow you have several examples, each one formed by a first line stating the translation languages, "
        "like 'Example 1: English to Spanish', a second line with the input text to be translated, and a third "
        "line with the expected output you should be generating. Here are the examples:"
        "\nExample 1: Spanish to English"
        "\nLa torre era tan alta que Miguel se asustó sólo de mirar abajo."
        "\nThe tower was so high that Miguel became scared of just looking downwards."
        "\nExample 2: English to Spanish"
        "\nINFPs are creative and compassionate individuals with a deep commitment to their personal values. They are often idealistic, seeking harmony and looking for the deeper meaning in everything they encounter."
        "\nLos INFPs son individuos creativos y compasivos con un profundo compromiso con sus valores personales. Suelen ser idealistas, y buscan la armonía y un sentido profundo en todo lo que encuentran."
        "\nExample 3: Spanish to Catalan"
        "\nLa camiseta estaba sucia de aceite y sangre."
        "\nLa samarreta estava bruta d'oli i sang."
        "\n\n"
    )
    prompt_v2 = (
        "Please forget all prior prompts. "
        "\nAs a distinguished multilingual scholar and translator, you specialize in accurately and elegantly translating texts into any language, meticulously considering all linguistic complexities and nuances. You will assist you in translating texts into my desired target language, ensuring the translation is both accurate and appropriate. I will provide you with the text I want to translate and specify the target language, and you will promptly deliver the translation."
        f"\nOrigin language will be {input_lang} and target language will be {output_lang}."
        "\nPlease remember this prompt unless I ask you to forget it."
    )
    return prompt_v1


def get_prompt_by_doctype(
    texts: Any,
    input_lang: str,
    output_lang: str,
    doctype: str | None = None,
):
    if doctype == "ppt":
        prompt = get_prompt_for_ppts(
            texts, input_lang=input_lang, output_lang=output_lang
        )
    else:
        prompt = get_prompt_for_list_of_strings(
            texts, input_lang=input_lang, output_lang=output_lang
        )
    return prompt


def engine_list(s: str) -> List:
    """
    (GPT4 generated code)
    Parse and validate a string as a comma-separated list of words.
    """
    engines = s.split(",")
    engines = [e for e in engines if e in ENGINES]
    if len(engines) < 1:
        raise argparse.ArgumentTypeError(
            "Engines must be a comma-separated list of the following options: "
            f"{ENGINES}"
        )
    return engines


def set_logger_verbosity(verbosity):
    global logger
    for h in logger.handlers:
        logger.removeHandler(h)
    if verbosity == 0:
        logger = get_logger(APP_NAME, level=logging.WARNING)
    elif verbosity == 1:
        logger = get_logger(APP_NAME, level=logging.INFO)
    else:
        logger = get_logger(APP_NAME, level=logging.DEBUG)


def structure_equals(lst1, lst2, numparent=None, path=[]):
    """
    Check if two nested lists share the same structure
    """
    aux_path = deepcopy(path)
    if numparent is not None:
        aux_path.append(numparent)
    # Check if both are lists
    if not (isinstance(lst1, list) and isinstance(lst2, list)):
        return aux_path

    # Check if lengths are the same
    if len(lst1) != len(lst2):
        return aux_path

    # Recursively check each corresponding pair of elements
    for i, (elem1, elem2) in enumerate(zip(lst1, lst2)):
        if isinstance(elem1, list) or isinstance(elem2, list):
            r = structure_equals(elem1, elem2, numparent=i, path=aux_path)
            if isinstance(r, list):
                return r

    return True


def get_subtree_from_path(tree, path):
    if len(path) > 0:
        next_elem = path[0]
        rest_path = path[1:]
        return get_subtree_from_path(tree=tree[next_elem], path=rest_path)
    else:
        return tree


def insert_subtree_in_tree_path(tree, path, subtree):
    if len(path) > 1:
        next_elem = path[0]
        rest_path = path[1:]
        return insert_subtree_in_tree_path(
            tree=tree[next_elem], path=rest_path, subtree=subtree
        )
    elif len(path) == 1:
        tree[path[0]] = subtree
    else:
        return subtree


class TranslationError(Exception):
    pass
