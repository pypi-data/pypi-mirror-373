from typing import Any, Dict, List


# List of languages supported by the cognitive service
# If the "iso_code" is empty, it means that the language is not supported by PowerBI.
# If the "iso_region" is empty, it means there is officially supported in powerbi service public documentation but can be used.
ISO_LANGUAGE_LIST: List[Dict[str, Any]] = [
    {
        "api_code": "af",
        "api_name": "Afrikaans",
        "iso_code": "af-ZA",
        "iso_name": "Afrikaans (South Africa)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "am",
        "api_name": "Amharic",
        "iso_code": "am-ET",
        "iso_name": "Amharic",
        "iso_region": "Ethiopia",
        "defaults": True
    },
    {
        "api_code": "ar",
        "api_name": "Arabic",
        "iso_code": "ar-AE",
        "iso_name": "Arabic",
        "iso_region": "U.A.E.",
        "defaults": True
    },
    {
        "api_code": "as",
        "api_name": "Assamese",
        "iso_code": "as-IN",
        "iso_name": "Assamese (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "az",
        "api_name": "Azerbaijani",
        "iso_code": "az-Latn-AZ",
        "iso_name": "Azerbaijan (Latin, Azerbaijan)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ba",
        "api_name": "Bashkir",
        "iso_code": "ba-RU",
        "iso_name": "Bashkir (Russia)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "be",
        "api_name": "Belarusian",
        "iso_code": "be-BY",
        "iso_name": "Belarusian (Belarus)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "bg",
        "api_name": "Bulgarian",
        "iso_code": "bg-BG",
        "iso_name": "Bulgarian",
        "iso_region": "Bulgaria",
        "defaults": True
    },
    {
        "api_code": "bho",
        "api_name": "Bhojpuri",
        "iso_code": "bho-Deva-IN",
        "iso_name": "Bhojpuri (Devanagari, India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "bn",
        "api_name": "Bangla",
        "iso_code": "bn-BD",
        "iso_name": "Bangla (Bangladesh)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "bo",
        "api_name": "Tibetan",
        "iso_code": "bo-CN",
        "iso_name": "Tibetan (China)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "brx",
        "api_name": "Bodo",
        "iso_code": "brx-IN",
        "iso_name": "Bodo (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "bs",
        "api_name": "Bosnian",
        "iso_code": "bs-Latn-BA",
        "iso_name": "Bosnian (Latin, Bosnia and Herzegovina)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ca",
        "api_name": "Catalan",
        "iso_code": "ca-ES",
        "iso_name": "Catalan",
        "iso_region": "Spain",
        "defaults": True
    },
    {
        "api_code": "cs",
        "api_name": "Czech",
        "iso_code": "cs-CZ",
        "iso_name": "Czech",
        "iso_region": "Czechia",
        "defaults": True
    },
    {
        "api_code": "cy",
        "api_name": "Welsh",
        "iso_code": "cy-GB",
        "iso_name": "Welsh (United Kingdom)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "da",
        "api_name": "Danish",
        "iso_code": "da-DK",
        "iso_name": "Danish",
        "iso_region": "Denmark",
        "defaults": True
    },
    {
        "api_code": "de",
        "api_name": "German",
        "iso_code": "de-AT",
        "iso_name": "German",
        "iso_region": "Austria",
        "defaults": False
    },
    {
        "api_code": "de",
        "api_name": "German",
        "iso_code": "de-CH",
        "iso_name": "German",
        "iso_region": "Switzerland",
        "defaults": False
    },
    {
        "api_code": "de",
        "api_name": "German",
        "iso_code": "de-DE",
        "iso_name": "German",
        "iso_region": "Germany",
        "defaults": True
    },
    {
        "api_code": "doi",
        "api_name": "Dogri",
        "iso_code": "doi-Deva-IN",
        "iso_name": "Dogri (Devanagari, India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "dsb",
        "api_name": "Lower Sorbian",
        "iso_code": "dsb-DE",
        "iso_name": "Lower Sorbian (Germany)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "dv",
        "api_name": "Divehi",
        "iso_code": "dv-MV",
        "iso_name": "Divehi (Maldives)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "el",
        "api_name": "Greek",
        "iso_code": "el-GR",
        "iso_name": "Greek",
        "iso_region": "Greece",
        "defaults": True
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-AU",
        "iso_name": "English",
        "iso_region": "Australia",
        "defaults": False
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-CA",
        "iso_name": "English",
        "iso_region": "Canada",
        "defaults": False
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-GB",
        "iso_name": "English",
        "iso_region": "United Kingdom",
        "defaults": False
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-ID",
        "iso_name": "English",
        "iso_region": "Indonesia",
        "defaults": False
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-IN",
        "iso_name": "English",
        "iso_region": "India",
        "defaults": False
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-MY",
        "iso_name": "English",
        "iso_region": "Malaysia",
        "defaults": False
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-NZ",
        "iso_name": "English",
        "iso_region": "New Zealand",
        "defaults": False
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-PH",
        "iso_name": "English",
        "iso_region": "Republic of the Philippines",
        "defaults": False
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-US",
        "iso_name": "English",
        "iso_region": "United States",
        "defaults": True
    },
    {
        "api_code": "en",
        "api_name": "English",
        "iso_code": "en-ZA",
        "iso_name": "English",
        "iso_region": "South Africa",
        "defaults": False
    },
    {
        "api_code": "es",
        "api_name": "Spanish",
        "iso_code": "es-AR",
        "iso_name": "Spanish",
        "iso_region": "Argentina",
        "defaults": False
    },
    {
        "api_code": "es",
        "api_name": "Spanish",
        "iso_code": "es-CL",
        "iso_name": "Spanish",
        "iso_region": "Chile",
        "defaults": False
    },
    {
        "api_code": "es",
        "api_name": "Spanish",
        "iso_code": "es-ES",
        "iso_name": "Spanish",
        "iso_region": "Spain",
        "defaults": True
    },
    {
        "api_code": "es",
        "api_name": "Spanish",
        "iso_code": "es-MX",
        "iso_name": "Spanish",
        "iso_region": "Mexico",
        "defaults": False
    },
    {
        "api_code": "es",
        "api_name": "Spanish",
        "iso_code": "es-US",
        "iso_name": "Spanish",
        "iso_region": "United States",
        "defaults": False
    },
    {
        "api_code": "et",
        "api_name": "Estonian",
        "iso_code": "et-EE",
        "iso_name": "Estonian (Estonia)",
        "iso_region": "Estonia",
        "defaults": True
    },
    {
        "api_code": "eu",
        "api_name": "Basque",
        "iso_code": "eu-ES",
        "iso_name": "Basque (Basque)",
        "iso_region": "Basque",
        "defaults": True
    },
    {
        "api_code": "fa",
        "api_name": "Persian",
        "iso_code": "fa-IR",
        "iso_name": "Persian",
        "iso_region": "Iran",
        "defaults": True
    },
    {
        "api_code": "fi",
        "api_name": "Finnish",
        "iso_code": "fi-FI",
        "iso_name": "Finnish",
        "iso_region": "Finland",
        "defaults": True
    },
    {
        "api_code": "fil",
        "api_name": "Filipino",
        "iso_code": "fil-PH",
        "iso_name": "Filipino (Philippines)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "fj",
        "api_name": "Fijian",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "fo",
        "api_name": "Faroese",
        "iso_code": "fo-FO",
        "iso_name": "Faroese (Faroe Islands)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "fr",
        "api_name": "French",
        "iso_code": "fr-BE",
        "iso_name": "French",
        "iso_region": "Belgium",
        "defaults": False
    },
    {
        "api_code": "fr",
        "api_name": "French",
        "iso_code": "fr-CH",
        "iso_name": "French",
        "iso_region": "Switzerland",
        "defaults": False
    },
    {
        "api_code": "fr",
        "api_name": "French",
        "iso_code": "fr-FR",
        "iso_name": "French",
        "iso_region": "France",
        "defaults": True
    },
    {
        "api_code": "fr-CA",
        "api_name": "French (Canada)",
        "iso_code": "fr-CA",
        "iso_name": "French (Canada)",
        "iso_region": "Canada",
        "defaults": False
    },
    {
        "api_code": "ga",
        "api_name": "Irish",
        "iso_code": "ga-IE",
        "iso_name": "Irish",
        "iso_region": "Ireland",
        "defaults": True
    },
    {
        "api_code": "gl",
        "api_name": "Galician",
        "iso_code": "gl-ES",
        "iso_name": "Galician (Galician)",
        "iso_region": "Galician",
        "defaults": True
    },
    {
        "api_code": "gom",
        "api_name": "Konkani",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "gu",
        "api_name": "Gujarati",
        "iso_code": "gu-IN",
        "iso_name": "Gujarati (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ha",
        "api_name": "Hausa",
        "iso_code": "ha-Latn-NG",
        "iso_name": "Hausa (Latin, Nigeria)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "he",
        "api_name": "Hebrew",
        "iso_code": "he-IL",
        "iso_name": "Hebrew",
        "iso_region": "Israel",
        "defaults": True
    },
    {
        "api_code": "hi",
        "api_name": "Hindi",
        "iso_code": "hi-IN",
        "iso_name": "Hindi",
        "iso_region": "India",
        "defaults": True
    },
    {
        "api_code": "hne",
        "api_name": "Chhattisgarhi",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "hr",
        "api_name": "Croatian",
        "iso_code": "hr-HR",
        "iso_name": "Croatian (Croatia)",
        "iso_region": "Croatia",
        "defaults": True
    },
    {
        "api_code": "hsb",
        "api_name": "Upper Sorbian",
        "iso_code": "hsb-DE",
        "iso_name": "Upper Sorbian (Germany)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ht",
        "api_name": "Haitian Creole",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "hu",
        "api_name": "Hungarian",
        "iso_code": "hu-HU",
        "iso_name": "Hungarian",
        "iso_region": "Hungary",
        "defaults": True
    },
    {
        "api_code": "hy",
        "api_name": "Armenian",
        "iso_code": "hy-AM",
        "iso_name": "Armenian (Armenia)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "id",
        "api_name": "Indonesian",
        "iso_code": "id-ID",
        "iso_name": "Indonesian",
        "iso_region": "Indonesia",
        "defaults": True
    },
    {
        "api_code": "ig",
        "api_name": "Igbo",
        "iso_code": "ig-NG",
        "iso_name": "Igbo (Nigeria)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ikt",
        "api_name": "Inuinnaqtun",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "is",
        "api_name": "Icelandic",
        "iso_code": "is-IS",
        "iso_name": "Icelandic",
        "iso_region": "Iceland",
        "defaults": True
    },
    {
        "api_code": "it",
        "api_name": "Italian",
        "iso_code": "it-IT",
        "iso_name": "Italian",
        "iso_region": "Italy",
        "defaults": True
    },
    {
        "api_code": "iu",
        "api_name": "Inuktitut",
        "iso_code": "iu-Cans-CA",
        "iso_name": "Inuktitut (Syllabics, Canada)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "iu-Latn",
        "api_name": "Inuktitut (Latin)",
        "iso_code": "iu-Latn-CA",
        "iso_name": "Inuktitut (Latin, Canada)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ja",
        "api_name": "Japanese",
        "iso_code": "ja-JP",
        "iso_name": "Japanese",
        "iso_region": "Japan",
        "defaults": True
    },
    {
        "api_code": "ka",
        "api_name": "Georgian",
        "iso_code": "ka-GE",
        "iso_name": "Georgian (Georgia)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "kk",
        "api_name": "Kazakh",
        "iso_code": "kk-KZ",
        "iso_name": "Kazakh (Kazakhstan)",
        "iso_region": "Kazakhstan",
        "defaults": True
    },
    {
        "api_code": "km",
        "api_name": "Khmer",
        "iso_code": "km-KH",
        "iso_name": "Khmer (Cambodia)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "kmr",
        "api_name": "Kurdish (Northern)",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "kn",
        "api_name": "Kannada",
        "iso_code": "kn-IN",
        "iso_name": "Kannada (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ko",
        "api_name": "Korean",
        "iso_code": "ko-KR",
        "iso_name": "Korean",
        "iso_region": "Korea",
        "defaults": True
    },
    {
        "api_code": "ks",
        "api_name": "Kashmiri",
        "iso_code": "ks-Arab-IN",
        "iso_name": "Kashmiri (Arabic)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ku",
        "api_name": "Kurdish (Central)",
        "iso_code": "ku-Arab-IQ",
        "iso_name": "Central Kurdish (Iraq)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ky",
        "api_name": "Kyrgyz",
        "iso_code": "ky-KG",
        "iso_name": "kyrgiz (Kyrgyzstan)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "lb",
        "api_name": "Luxembourgish",
        "iso_code": "lb-LU",
        "iso_name": "Luxembourgish (Luxembourg)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ln",
        "api_name": "Lingala",
        "iso_code": "ln-CD",
        "iso_name": "Lingala (Congo DRC)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "lo",
        "api_name": "Lao",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "lt",
        "api_name": "Lithuanian",
        "iso_code": "lt-LT",
        "iso_name": "Lithuanian (Lithuania)",
        "iso_region": "Lithuania",
        "defaults": True
    },
    {
        "api_code": "lug",
        "api_name": "Ganda",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "lv",
        "api_name": "Latvian",
        "iso_code": "lv-LV",
        "iso_name": "Latvian (Latvia)",
        "iso_region": "Latvia",
        "defaults": True
    },
    {
        "api_code": "lzh",
        "api_name": "Chinese (Literary)",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "mai",
        "api_name": "Maithili",
        "iso_code": "mai-IN",
        "iso_name": "Maithili (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "mg",
        "api_name": "Malagasy",
        "iso_code": "mg-MG",
        "iso_name": "Malagasy (Madagascar)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "mi",
        "api_name": "Māori",
        "iso_code": "mi-NZ",
        "iso_name": "Māori (New Zealand)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "mk",
        "api_name": "Macedonian",
        "iso_code": "mk-MK",
        "iso_name": "Macedonian (North Macedonia)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ml",
        "api_name": "Malayalam",
        "iso_code": "ml-IN",
        "iso_name": "Malayalam (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "mn-Cyrl",
        "api_name": "Mongolian (Cyrillic)",
        "iso_code": "mn-MN",
        "iso_name": "Mongolian (Mongolia)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "mn-Mong",
        "api_name": "Mongolian (Traditional)",
        "iso_code": "mn-Mong-CN",
        "iso_name": "Mongolian (Traditional Mongolian, China)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "mni",
        "api_name": "Manipuri",
        "iso_code": "mni-IN",
        "iso_name": "Manipuri (Bangla, India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "mr",
        "api_name": "Marathi",
        "iso_code": "mr-IN",
        "iso_name": "Marathi (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ms",
        "api_name": "Malay",
        "iso_code": "ms-MY",
        "iso_name": "Malay (Malaysia)",
        "iso_region": "Malaysia",
        "defaults": True
    },
    {
        "api_code": "mt",
        "api_name": "Maltese",
        "iso_code": "mt-MT",
        "iso_name": "Maltese",
        "iso_region": "Malta",
        "defaults": True
    },
    {
        "api_code": "mww",
        "api_name": "Hmong Daw",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "my",
        "api_name": "Myanmar (Burmese)",
        "iso_code": "my-MM",
        "iso_name": "Burmese (Myanmar)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "nb",
        "api_name": "Norwegian",
        "iso_code": "nb-NO",
        "iso_name": "Norwegian",
        "iso_region": "Norway",
        "defaults": True
    },
    {
        "api_code": "ne",
        "api_name": "Nepali",
        "iso_code": "ne-NP",
        "iso_name": "Nepali (Nepal)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "nl",
        "api_name": "Dutch",
        "iso_code": "nl-BE",
        "iso_name": "Dutch",
        "iso_region": "Belgium",
        "defaults": True
    },
    {
        "api_code": "nl",
        "api_name": "Dutch",
        "iso_code": "nl-NL",
        "iso_name": "Dutch",
        "iso_region": "Netherlands",
        "defaults": True
    },
    {
        "api_code": "nso",
        "api_name": "Sesotho sa Leboa",
        "iso_code": "nso-ZA",
        "iso_name": "Sesotho sa Leboa (South Africa)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "nya",
        "api_name": "Nyanja",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "or",
        "api_name": "Odia",
        "iso_code": "or-IN",
        "iso_name": "Odia (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "otq",
        "api_name": "Querétaro Otomi",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "pa",
        "api_name": "Punjabi",
        "iso_code": "pa-IN",
        "iso_name": "Punjabi (India)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "pl",
        "api_name": "Polish",
        "iso_code": "pl-PL",
        "iso_name": "Polish",
        "iso_region": "Poland",
        "defaults": False
    },
    {
        "api_code": "prs",
        "api_name": "Dari",
        "iso_code": "prs-AF",
        "iso_name": "Dari (Afghanistan)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ps",
        "api_name": "Pashto",
        "iso_code": "ps-AF",
        "iso_name": "pashto (Afghanistan)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "pt",
        "api_name": "Portuguese (Brazil)",
        "iso_code": "pt-BR",
        "iso_name": "Portuguese (Brazil)",
        "iso_region": "Brazil",
        "defaults": True
    },
    {
        "api_code": "pt-PT",
        "api_name": "Portuguese (Portugal)",
        "iso_code": "pt-PT",
        "iso_name": "Portuguese",
        "iso_region": "Portugal",
        "defaults": True
    },
    {
        "api_code": "ro",
        "api_name": "Romanian",
        "iso_code": "ro-RO",
        "iso_name": "Romanian",
        "iso_region": "Romania",
        "defaults": True
    },
    {
        "api_code": "ru",
        "api_name": "Russian",
        "iso_code": "ru-RU",
        "iso_name": "Russian",
        "iso_region": "Russia",
        "defaults": True
    },
    {
        "api_code": "run",
        "api_name": "Rundi",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "rw",
        "api_name": "Kinyarwanda",
        "iso_code": "rw-RW",
        "iso_name": "Kinyarwanda (Rwanda)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "sd",
        "api_name": "Sindhi",
        "iso_code": "sd-Arab-PK",
        "iso_name": "Sindhi (Pakistan)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "si",
        "api_name": "Sinhala",
        "iso_code": "si-LK",
        "iso_name": "Sinhala (Sri Lanka)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "sk",
        "api_name": "Slovak",
        "iso_code": "sk-SK",
        "iso_name": "Slovak",
        "iso_region": "Slovakia",
        "defaults": True
    },
    {
        "api_code": "sl",
        "api_name": "Slovenian",
        "iso_code": "sl-SI",
        "iso_name": "Slovenian",
        "iso_region": "Slovenia",
        "defaults": True
    },
    {
        "api_code": "sm",
        "api_name": "Samoan",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "sn",
        "api_name": "Shona",
        "iso_code": "sn-Latn-ZW",
        "iso_name": "Shona (Latin, Zimbabwe)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "so",
        "api_name": "Somali",
        "iso_code": "so-SO",
        "iso_name": "Somali (Somalia)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "sq",
        "api_name": "Albanian",
        "iso_code": "sq-AL",
        "iso_name": "Albanian (Albania)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "sr-Cyrl",
        "api_name": "Serbian (Cyrillic)",
        "iso_code": "sr-Cyrl-RS",
        "iso_name": "Serbian (Cyrillic, Serbia)",
        "iso_region": "Serbia",
        "defaults": True
    },
    {
        "api_code": "sr-Latn",
        "api_name": "Serbian (Latin)",
        "iso_code": "sr-Latn-RS",
        "iso_name": "Serbian (Latin, Serbia)",
        "iso_region": "Serbia",
        "defaults": True
    },
    {
        "api_code": "st",
        "api_name": "Sesotho",
        "iso_code": "st-ZA",
        "iso_name": "Sesotho (South Africa)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "sv",
        "api_name": "Swedish",
        "iso_code": "sv-SE",
        "iso_name": "Swedish",
        "iso_region": "Sweden",
        "defaults": True
    },
    {
        "api_code": "sw",
        "api_name": "Swahili",
        "iso_code": "sw-TZ",
        "iso_name": "Kiswahili (Tanzania)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ta",
        "api_name": "Tamil",
        "iso_code": "ta-IN",
        "iso_name": "Tamil",
        "iso_region": "India",
        "defaults": True
    },
    {
        "api_code": "te",
        "api_name": "Telugu",
        "iso_code": "te-IN",
        "iso_name": "Telugu",
        "iso_region": "India",
        "defaults": True
    },
    {
        "api_code": "th",
        "api_name": "Thai",
        "iso_code": "th-TH",
        "iso_name": "Thai",
        "iso_region": "Thailand",
        "defaults": True
    },
    {
        "api_code": "ti",
        "api_name": "Tigrinya",
        "iso_code": "ti-ER",
        "iso_name": "Tigrinya (Eritrea)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "tk",
        "api_name": "Turkmen",
        "iso_code": "tk-TM",
        "iso_name": "Turkmen (Turkmenistan)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "tlh-Latn",
        "api_name": "Klingon (Latin)",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "tlh-Piqd",
        "api_name": "Klingon (pIqaD)",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "tn",
        "api_name": "Setswana",
        "iso_code": "tn-BW",
        "iso_name": "Setswana (Botswana)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "to",
        "api_name": "Tongan",
        "iso_code": "to-TO",
        "iso_name": "Tongan (Tonga)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "tr",
        "api_name": "Turkish",
        "iso_code": "tr-TR",
        "iso_name": "Turkish",
        "iso_region": "Türkiye",
        "defaults": True
    },
    {
        "api_code": "tt",
        "api_name": "Tatar",
        "iso_code": "tt-RU",
        "iso_name": "Tatar (Russia)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ty",
        "api_name": "Tahitian",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "ug",
        "api_name": "Uyghur",
        "iso_code": "ug-CN",
        "iso_name": "Uyghur (China)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "uk",
        "api_name": "Ukrainian",
        "iso_code": "uk-UA",
        "iso_name": "Ukrainian",
        "iso_region": "Ukraine",
        "defaults": True
    },
    {
        "api_code": "ur",
        "api_name": "Urdu",
        "iso_code": "ur-PK",
        "iso_name": "Urdu (Pakistan)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "uz",
        "api_name": "Uzbek (Latin)",
        "iso_code": "uz-Latn-UZ",
        "iso_name": "Uzbek (Latin, Uzbekistan)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "vi",
        "api_name": "Vietnamese",
        "iso_code": "vi-VN",
        "iso_name": "Vietnamese (Vietnam)",
        "iso_region": "Vietnam",
        "defaults": True
    },
    {
        "api_code": "xh",
        "api_name": "Xhosa",
        "iso_code": "xh-ZA",
        "iso_name": "isiXhosa (South Africa)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "yo",
        "api_name": "Yoruba",
        "iso_code": "yo-NG",
        "iso_name": "Yoruba (Nigeria)",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "yua",
        "api_name": "Yucatec Maya",
        "iso_code": "",
        "iso_name": "",
        "iso_region": "",
        "defaults": True
    },
    {
        "api_code": "yue",
        "api_name": "Cantonese (Traditional)",
        "iso_code": "zh-HK",
        "iso_name": "Traditional Chinese",
        "iso_region": "Hong Kong SAR",
        "defaults": True
    },
    {
        "api_code": "zh-Hans",
        "api_name": "Chinese Simplified",
        "iso_code": "zh-CN",
        "iso_name": "Chinese",
        "iso_region": "People's republic of China",
        "defaults": True
    },
    {
        "api_code": "zh-Hant",
        "api_name": "Chinese Traditional",
        "iso_code": "zh-TW",
        "iso_name": "Traditional Chinese",
        "iso_region": "Taiwan",
        "defaults": True
    },
    {
        "api_code": "zu",
        "api_name": "Zulu",
        "iso_code": "zu-ZA",
        "iso_name": "Zulu",
        "iso_region": "South Africa",
        "defaults": True
    }
]

# Flattened reverted map for iso_code or iso_name to api_code (used by cognitive service)
ISO_LANGUAGE_MAP: Dict[str, str] = {
    **{lang["iso_code"].lower(): lang["api_code"].lower() for lang in ISO_LANGUAGE_LIST if lang["iso_code"]},
    **{lang["iso_name"].lower(): lang["api_code"].lower() for lang in ISO_LANGUAGE_LIST if lang["iso_name"]},
}

# Map for api_code to iso_code (used by cognitive service)
API_LANGUAGE_MAP: Dict[str, str] = {
   lang["api_code"]: lang["iso_code"] for lang in ISO_LANGUAGE_LIST if lang["defaults"]
}
