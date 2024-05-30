availableTranslationLanguages = [
    {"code": "ar", "name": "Arabic", "nativeName": "العربية"},
    {"code": "bg", "name": "Bulgarian", "nativeName": "български език"},
    {"code": "nl", "name": "Dutch", "nativeName": "Nederlands"},
    {"code": "fr", "name": "French", "nativeName": "français"},
    {"code": "de", "name": "German", "nativeName": "Deutsch"},
    {"code": "el", "name": "Greek", "nativeName": "Ελληνικά"},
    {"code": "id", "name": "Indonesian", "nativeName": "Bahasa Indonesia"},
    {"code": "it", "name": "Italian", "nativeName": "Italiano"},
    {"code": "ja", "name": "Japanese", "nativeName": "日本語"},
    {"code": "pl", "name": "Polish", "nativeName": "polski"},
    {"code": "pt", "name": "Portuguese", "nativeName": "Português"},
    {
        "code": "pt-br",
        "name": "Portuguese (Brazil)",
        "nativeName": "Português do Brasil",
    },
    {"code": "ro", "name": "Romanian", "nativeName": "română"},
    {"code": "ru", "name": "Russian", "nativeName": "русский язык"},
    {"code": "es", "name": "Spanish (Spain)", "nativeName": "español (España)"},
    {
        "code": "es-la",
        "name": "Spanish (Latin America)",
        "nativeName": "español (Latinoamérica)",
    },
    {"code": "zh", "name": "Chinese", "nativeName": "中文"},
    {"code": "cs", "name": "Czech", "nativeName": "česky"},
    {"code": "da", "name": "Danish", "nativeName": "dansk"},
    {"code": "en-gb", "name": "English (British)", "nativeName": "English (UK)"},
    {"code": "fi", "name": "Finnish", "nativeName": "suomi"},
    {"code": "fr-ca", "name": "French (Canada)", "nativeName": "français canadien"},
    {"code": "iw", "name": "Hebrew", "nativeName": "עברית"},
    {"code": "hu", "name": "Hungarian", "nativeName": "magyar"},
    {"code": "ko", "name": "Korean", "nativeName": "한국어"},
    {"code": "ms", "name": "Malay", "nativeName": "Bahasa Melayu"},
    {"code": "no", "name": "Norwegian", "nativeName": "norsk"},
    {"code": "sr", "name": "Serbian", "nativeName": "српски језик"},
    {"code": "sk", "name": "Slovak", "nativeName": "slovenčina"},
    {"code": "sv", "name": "Swedish", "nativeName": "svenska"},
    {"code": "tl", "name": "Tagalog", "nativeName": "Wikang Tagalog"},
    {"code": "th", "name": "Thai", "nativeName": "ไทย"},
    {"code": "uk", "name": "Ukrainian", "nativeName": "українська"},
    {"code": "vi", "name": "Vietnamese", "nativeName": "Tiếng Việt"},
    {"code": "fa", "name": "Persian", "nativeName": "فارسی"},
    {"code": "tr", "name": "Turkish", "nativeName": "Türkçe"},
]

languageEnglish2Code = {
    item["name"].lower(): item["code"] for item in availableTranslationLanguages
}
languageCode2English = {
    item["code"]: item["name"].lower() for item in availableTranslationLanguages
}
