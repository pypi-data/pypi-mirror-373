import re
import regex
import json
from collections import defaultdict
from pathlib import Path
import translators as ts


def clean_text(text):
    text = rgx_single_linebreaks.sub(" ", text)
    text = rgx_multi_spaces.sub(" ", text)
    text = rgx_multi_linebreaks.sub("\n", text)
    return text


# Common values
APP_NAME = "translator_cli"


# Regexes
rgx_single_linebreaks = re.compile(r"(?<!\n)\n(?!\n)")
rgx_multi_spaces = re.compile(r" +")
rgx_multi_linebreaks = re.compile(r"\n+")
rgx_text = regex.compile(r".*\p{L}.*")

# Paths
ROOT_DIR = Path(__file__).absolute().parent.parent
ASSETS_DIR = ROOT_DIR.joinpath("assets")
OUTPUT_DIR = ROOT_DIR.joinpath("output")

# URLs
BASE_URL = "http://xiuquan.cc.upv.es"
LIBRETRANSLATE_URL = BASE_URL + "/translate"

# Engines
GPT_ENGINES = ["gpt4", "gpt3"]
PRIORITIZED_TS_ENGINES = ["reverso", "modernMt", "qqFanyi", "baidu"]
TS_ENGINES = [x for x in PRIORITIZED_TS_ENGINES if x in ts.translators_pool] + [
    x for x in ts.translators_pool if x not in PRIORITIZED_TS_ENGINES
]
NO_TS_ENGINES = GPT_ENGINES + ["deepl"] + ["google"] + ["aws"]
ENGINES = NO_TS_ENGINES + TS_ENGINES
FIXER_ENGINE = "google"

# Language dicts
LINGVANEX_CORRESPONDENCE = {
    "af": "af_ZA",
    "am": "am_ET",
    "ar": "ar_SA",
    "az": "az_AZ",
    "be": "be_BY",
    "bg": "bg_BG",
    "bn": "bn_BD",
    "bs": "bs_BA",
    "ca": "ca_ES",
    "ceb": "ceb_PH",
    "co": "co_FR",
    "cs": "cs_CZ",
    "cy": "cy_GB",
    "da": "da_DK",
    "de": "de_DE",
    "el": "el_GR",
    "en": "en_US",
    "eo": "eo_WORLD",
    "es": "es_ES",
    "et": "et_EE",
    "eu": "eu_ES",
    "fa": "fa_IR",
    "fi": "fi_FI",
    "fr": "fr_FR",
    "fy": "fy_NL",
    "ga": "ga_IE",
    "gd": "gd_GB",
    "gl": "gl_ES",
    "gu": "gu_IN",
    "ha": "ha_NE",
    "haw": "haw_US",
    "he": "he_IL",
    "hi": "hi_IN",
    "hmn": "hmn_CN",
    "hr": "hr_HR",
    "ht": "ht_HT",
    "hu": "hu_HU",
    "hy": "hy_AM",
    "id": "id_ID",
    "ig": "ig_NG",
    "is": "is_IS",
    "it": "it_IT",
    "ja": "ja_JP",
    "jv": "jv_ID",
    "ka": "ka_GE",
    "kk": "kk_KZ",
    "km": "km_KH",
    "kn": "kn_IN",
    "ko": "ko _KR",
    "ku": "ku_IR",
    "ky": "ky_KG",
    "la": "la_VAT",
    "lb": "lb_LU",
    "lo": "lo_LA",
    "lt": "lt_LT",
    "lv": "lv_LV",
    "mg": "mg_MG",
    "mi": "mi_NZ",
    "mk": "mk_MK",
    "ml": "ml_IN",
    "mn": "mn_MN",
    "mr": "mr_IN",
    "ms": "ms_MY",
    "mt": "mt_MT",
    "my": "my_MM",
    "ne": "ne_NP",
    "nl": "nl_NL",
    "no": "no_NO",
    "ny": "ny_MW",
    "or": "or_OR",
    "pa": "pa_PK",
    "pl": "pl_PL",
    "ps": "ps_AF",
    "pt": "pt_PT",
    "ro": "ro_RO",
    "ru": "ru_RU",
    "rw": "rw_RW",
    "sd": "sd_PK",
    "si": "si_LK",
    "sk": "sk_SK",
    "sl": "sl_SI",
    "sm": "sm_WS",
    "sn": "sn_ZW",
    "so": "so_SO",
    "sq": "sq_AL",
    "sr": "sr-Cyrl_RS",
    "st": "st_LS",
    "su": "su_ID",
    "sv": "sv_SE",
    "sw": "sw_TZ",
    "ta": "ta_IN",
    "te": "te_IN",
    "tg": "tg_TJ",
    "th": "th_TH",
    "tk": "tk_TK",
    "tl": "tl_PH",
    "tr": "tr_TR",
    "tt": "tt_TT",
    "ug": "ug_UG",
    "uk": "uk_UA",
    "ur": "ur_PK",
    "uz": "uz_UZ",
    "vi": "vi_VN",
    "xh": "xh_ZA",
    "yi": "yi_IL",
    "yo": "yo_NG",
    "zh": "zh-Hans_CN",
    "zu": "zu_ZA",
}


ca = defaultdict(lambda: "ca")
ca["apertium"] = "cat"
ca["lingvanex"] = "ca_ES"
ca["myMemory"] = "ca-ES"
en = defaultdict(lambda: "en")
en["translateMe"] = "English"
en["myMemory"] = "en-US"
en["lingvanex"] = "en_GB"
en["cloudTranslation"] = "en-us"
en["apertium"] = "eng"
es = defaultdict(lambda: "es")
es["translateMe"] = "Spanish"
es["myMemory"] = "es-ES"
es["modernMt"] = "es-ES"
es["lingvanex"] = "es_ES"
es["itranslate"] = "es-ES"
es["baidu"] = "spa"
es["apertium"] = "spa"
LANGUAGE_EQUIVALENCES = {"ca": ca, "en": en, "es": es}

LANGUAGE_CODENAMES = {
    "ca": "Catalan",
    "eu": "Basque",
    "gl": "Galician",
    "oc": "Occitan",
    "ar": "Arabic",
    "bn": "Bengali",
    "de": "German",
    "en": "English",
    "es": "Spanish",
    "fa": "Persian",
    "fr": "French",
    "hi": "Hindi",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "jv": "Javanese",
    "ko": "Korean",
    "mr": "Marathi",
    "ms": "Malay",
    "pa": "Punjabi",
    "pt": "Portuguese",
    "ru": "Russian",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh": "Chinese",
    "zu": "Zulu",
    "el": "Greek",
    "he": "Hebrew",
    "nl": "Dutch",
    "pl": "Polish",
    "ro": "Romanian",
    "sv": "Swedish",
    "hu": "Hungarian",
    "fi": "Finnish",
    "no": "Norwegian",
    "cs": "Czech",
    "da": "Danish",
    "is": "Icelandic",
    "ga": "Irish",
    "mt": "Maltese",
    "af": "Afrikaans",
    "ha": "Hausa",
    "yo": "Yoruba",
    "ig": "Igbo",
    "zu": "Zulu",
    "am": "Amharic",
    "mg": "Malagasy",
    "so": "Somali",
    "ht": "Haitian Creole",
    "fy": "Western Frisian",
    "xh": "Xhosa",
    "gd": "Scottish Gaelic",
    "cy": "Welsh",
}
