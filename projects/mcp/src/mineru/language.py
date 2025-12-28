"""List of languages supported by MinerU."""

from typing import Dict, List

# List of supported languages
LANGUAGES: List[Dict[str, str]] = [
    {"name": "Chinese", "description": "Chinese & English", "code": "ch"},
    {"name": "English", "description": "English", "code": "en"},
    {"name": "French", "description": "French", "code": "fr"},
    {"name": "German", "description": "German", "code": "german"},
    {"name": "Japanese", "description": "Japanese", "code": "japan"},
    {"name": "Korean", "description": "Korean", "code": "korean"},
    {"name": "Traditional Chinese", "description": "Chinese Traditional", "code": "chinese_cht"},
    {"name": "Italian", "description": "Italian", "code": "it"},
    {"name": "Spanish", "description": "Spanish", "code": "es"},
    {"name": "Portuguese", "description": "Portuguese", "code": "pt"},
    {"name": "Russian", "description": "Russian", "code": "ru"},
    {"name": "Arabic", "description": "Arabic", "code": "ar"},
    {"name": "Hindi", "description": "Hindi", "code": "hi"},
    {"name": "Uyghur", "description": "Uyghur", "code": "ug"},
    {"name": "Persian", "description": "Persian", "code": "fa"},
    {"name": "Urdu", "description": "Urdu", "code": "ur"},
    {"name": "Serbian (Latin)", "description": "Serbian(latin)", "code": "rs_latin"},
    {"name": "Occitan", "description": "Occitan", "code": "oc"},
    {"name": "Marathi", "description": "Marathi", "code": "mr"},
    {"name": "Nepali", "description": "Nepali", "code": "ne"},
    {
        "name": "Serbian (Cyrillic)",
        "description": "Serbian(cyrillic)",
        "code": "rs_cyrillic",
    },
    {"name": "Maori", "description": "Maori", "code": "mi"},
    {"name": "Malay", "description": "Malay", "code": "ms"},
    {"name": "Maltese", "description": "Maltese", "code": "mt"},
    {"name": "Dutch", "description": "Dutch", "code": "nl"},
    {"name": "Norwegian", "description": "Norwegian", "code": "no"},
    {"name": "Polish", "description": "Polish", "code": "pl"},
    {"name": "Romanian", "description": "Romanian", "code": "ro"},
    {"name": "Slovak", "description": "Slovak", "code": "sk"},
    {"name": "Slovenian", "description": "Slovenian", "code": "sl"},
    {"name": "Albanian", "description": "Albanian", "code": "sq"},
    {"name": "Swedish", "description": "Swedish", "code": "sv"},
    {"name": "Swahili", "description": "Swahili", "code": "sw"},
    {"name": "Tagalog", "description": "Tagalog", "code": "tl"},
    {"name": "Turkish", "description": "Turkish", "code": "tr"},
    {"name": "Uzbek", "description": "Uzbek", "code": "uz"},
    {"name": "Vietnamese", "description": "Vietnamese", "code": "vi"},
    {"name": "Mongolian", "description": "Mongolian", "code": "mn"},
    {"name": "Chechen", "description": "Chechen", "code": "che"},
    {"name": "Haryanvi", "description": "Haryanvi", "code": "bgc"},
    {"name": "Bulgarian", "description": "Bulgarian", "code": "bg"},
    {"name": "Ukranian", "description": "Ukranian", "code": "uk"},
    {"name": "Belarusian", "description": "Belarusian", "code": "be"},
    {"name": "Telugu", "description": "Telugu", "code": "te"},
    {"name": "Abaza", "description": "Abaza", "code": "abq"},
    {"name": "Tamil", "description": "Tamil", "code": "ta"},
    {"name": "Afrikaans", "description": "Afrikaans", "code": "af"},
    {"name": "Azerbaijani", "description": "Azerbaijani", "code": "az"},
    {"name": "Bosnian", "description": "Bosnian", "code": "bs"},
    {"name": "Czech", "description": "Czech", "code": "cs"},
    {"name": "Welsh", "description": "Welsh", "code": "cy"},
    {"name": "Danish", "description": "Danish", "code": "da"},
    {"name": "Estonian", "description": "Estonian", "code": "et"},
    {"name": "Irish", "description": "Irish", "code": "ga"},
    {"name": "Croatian", "description": "Croatian", "code": "hr"},
    {"name": "Hungarian", "description": "Hungarian", "code": "hu"},
    {"name": "Indonesian", "description": "Indonesian", "code": "id"},
    {"name": "Icelandic", "description": "Icelandic", "code": "is"},
    {"name": "Kurdish", "description": "Kurdish", "code": "ku"},
    {"name": "Lithuanian", "description": "Lithuanian", "code": "lt"},
    {"name": "Latvian", "description": "Latvian", "code": "lv"},
    {"name": "Dargwa", "description": "Dargwa", "code": "dar"},
    {"name": "Ingush", "description": "Ingush", "code": "inh"},
    {"name": "Lak", "description": "Lak", "code": "lbe"},
    {"name": "Lezghian", "description": "Lezghian", "code": "lez"},
    {"name": "Tabassaran", "description": "Tabassaran", "code": "tab"},
    {"name": "Bihari", "description": "Bihari", "code": "bh"},
    {"name": "Maithili", "description": "Maithili", "code": "mai"},
    {"name": "Angika", "description": "Angika", "code": "ang"},
    {"name": "Bhojpuri", "description": "Bhojpuri", "code": "bho"},
    {"name": "Magahi", "description": "Magahi", "code": "mah"},
    {"name": "Nagpur", "description": "Nagpur", "code": "sck"},
    {"name": "Newari", "description": "Newari", "code": "new"},
    {"name": "Goan Konkani", "description": "Goan Konkani", "code": "gom"},
    {"name": "Sanskrit", "description": "Sanskrit", "code": "sa"},
    {"name": "Avar", "description": "Avar", "code": "ava"},
    {"name": "阿瓦尔文", "description": "Avar", "code": "ava"},
    {"name": "Adyghe", "description": "Adyghe", "code": "ady"},
    {"name": "Pali", "description": "Pali", "code": "pi"},
    {"name": "Latin", "description": "Latin", "code": "la"},
]

# Build mapping dict from language code to language info for quick lookup
LANGUAGES_DICT: Dict[str, Dict[str, str]] = {lang["code"]: lang for lang in LANGUAGES}


def get_language_list() -> List[Dict[str, str]]:
    """Get list of all supported languages."""
    return LANGUAGES


def get_language_by_code(code: str) -> Dict[str, str]:
    """Get language information by code."""
    return LANGUAGES_DICT.get(
        code, {"name": "Unknown", "description": "Unknown", "code": code}
    )
