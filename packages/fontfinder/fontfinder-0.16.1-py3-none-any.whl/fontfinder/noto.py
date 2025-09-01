import copy
import datetime
import json
from pathlib import Path
import requests
import shutil

import fontfinder
from fontfinder.model import FontInfo, FontForm, FontWidth, FontWeight, FontStyle, FontFormat, FontBuild 


NOTO_MAIN_JSON_URL = "https://notofonts.github.io/noto.json"
'''URL of main Noto JSON font data.'''

NOTO_MAIN_BASE_URL = "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/"
'''Base URL of main Noto font download location.'''

NOTO_CJK_BASE_URL = "https://github.com/notofonts/noto-cjk/raw/main/"
'''Base URL of CJK Noto font download location.'''


_NOTO_MAIN_JSON_REF_PATH = Path(fontfinder._REF_DATA_DIR_PATH, "noto.json").resolve()
'''Path of reference copy of noto.json distributed with this package.'''

_NOTO_MAIN_JSON_USER_PATH = Path(fontfinder._USER_DATA_DIR_PATH, "cache", "noto.json").resolve()
'''Path of updated, cached copy of noto.json.'''

_NOTO_MAIN_JSON_MAX_AGE = datetime.timedelta(days=1)
'''Max age of cached copy of noto.json, after which an updated copy will be downloaded.'''


def get_noto_fonts(filter_func = None):
    '''Return a list of FontInfo records for the Google Noto fonts.'''
    font_infos = []
    font_infos.extend(_get_noto_main_fonts(filter_func))
    font_infos.extend(_get_noto_cjk_fonts(filter_func))
    font_infos.extend(_get_noto_emoji_fonts(filter_func))
    font_infos.sort()
    return font_infos

def _get_noto_main_data():
    '''Return main Noto JSON data as a Python object, handling cache as necessary.'''
    if not _NOTO_MAIN_JSON_USER_PATH.exists():
        # Copy noto.json distributed with this package
        _NOTO_MAIN_JSON_USER_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_NOTO_MAIN_JSON_REF_PATH, _NOTO_MAIN_JSON_USER_PATH)

    last_mod_time = datetime.datetime.fromtimestamp(_NOTO_MAIN_JSON_USER_PATH.stat().st_mtime)
    if (datetime.datetime.now() - last_mod_time) >= _NOTO_MAIN_JSON_MAX_AGE:
        # Update cached noto.json
        noto_json_text = requests.get(NOTO_MAIN_JSON_URL)
        with open(_NOTO_MAIN_JSON_USER_PATH, "w", encoding="utf-8") as file:
            file.write(noto_json_text.text)
    
    # Read cached noto.json
    with open(_NOTO_MAIN_JSON_USER_PATH, "r", encoding="utf-8") as file:
        noto_data = json.load(file)
    return noto_data
            
def _get_noto_main_fonts(filter_func = None):
    '''Return a list of FontInfo records for the main (non-CJK) Google Noto fonts.'''
    font_infos = []
    noto_data = _get_noto_main_data()

    # Note that the script keys in the Noto JSON data are *mostly* Unicode script names (once they are
    # changed to Titlecase and have hyphens replaced with underscores). But some of them are "pseudo-script-names"
    # for characters that formally belong under other Unicode script names. We adjust for all this below.
    for raw_script_key, script_data in noto_data.items():
        if raw_script_key == "latin-greek-cyrillic":
            # The Noto data treats these 3 scripts as one, but we duplicate the font info for all 3 indiv scripts.
            script_key_set = ['Latin', 'Greek', 'Cyrillic']
        elif raw_script_key == "meroitic":
            # The Noto data treats Meroitic as a single script, but in the Unicode data it's two separate scripts.
            script_key_set = ['Meroitic_Cursive', 'Meroitic_Hieroglyphs']
        else:
            script_key_set = [raw_script_key]

        for script_key in script_key_set:
            script_variant = ""
            if script_key == "sign-writing":
                main_script = "SignWriting" # No hyphen or underscore in the Unicode script name
            elif script_key == "nastaliq":
                # This is a Noto "pseudo-script-name" that actually is a Nastaliq Urdu variant of Arabic script.
                main_script = "Arabic"
                script_variant = "Urdu"
            elif script_key == "math" or script_key == "music" or script_key == "symbols" or \
                 script_key == "mayan-numerals" or script_key == "indic-siyaq-numbers" or \
                 script_key == "ottoman-siyaq-numbers" or script_key == "znamenny":
                # These are all "pseudo-script-names" for characters who actual script is mostly "Common".
                main_script = "Common"
                script_variant = script_key.replace('-', '_').title()
            elif script_key == "test":
                # For completeness, we include the Noto Sans Test and Noto Serif Test fonts, but without including
                # a Unicode script.
                main_script = ""
                script_variant = "Test"
            else:
                # Make the Noto script key formatting match the Unicode script name formatting.
                main_script = script_key.replace('-', '_').title()

            for family_name, family_data in script_data['families'].items():
                if family_name == "Noto Sans Symbols2":
                    family_name = "Noto Sans Symbols 2" # Fix spacing in Noto family name
                if "Syriac Western" in family_name:
                    script_variant = "Western"
                elif "Syriac Eastern" in family_name:
                    script_variant = "Eastern"
                
                form = FontForm.from_str(family_name)

                # Some font families should be added under other scripts as well. We add them here,
                # then re-iterate over the expanded script and variant names. (Most of the time this is a single
                # iteration that changes nothing.)
                expanded_scripts = [(main_script, script_variant)]
                if family_name == "Noto Sans Symbols 2":
                    # Only the Noto Sans Symbols 2 family handles the Unicode Braille script.
                    expanded_scripts.append(("Braille", ""))

                for main_script, script_variant in expanded_scripts:
                    for build, relative_url_list in family_data['files'].items():
                        build = FontBuild.from_str(build)
                        for relative_url in relative_url_list:
                            url = NOTO_MAIN_BASE_URL + relative_url
                            font_info = FontInfo(main_script=main_script, script_variant=script_variant,
                                                 family_name=family_name, url=url)
                            font_info.init_from_noto_url(url)
                            # Form and build have already been set from the URL, but we can ensure the values are
                            # correct from the other JSON data.
                            font_info.form = form
                            font_info.build = build
                            if filter_func is None or filter_func(font_info):
                                font_infos.append(font_info)
    return font_infos


_CJK_WEIGHTS =   [
    ("Black",       FontWeight.BLACK),
    ("Bold",        FontWeight.BOLD),
    ("DemiLight",   FontWeight.DEMI_LIGHT),
    ("Light",       FontWeight.LIGHT),
    ("Medium",      FontWeight.MEDIUM),
    ("Regular",     FontWeight.REGULAR),
    ("Thin",        FontWeight.THIN),                
]
'''Available weights of Noto CJK fonts.'''

# Keys for _CJK_DATA
_CJK_SCRIPT_INFO_KEY = "script_info"
_CJK_URL_COMPONENT_KEY = "url_component"
_CJK_CODE_KEY = "cjk_code"

_CJK_DATA = {
    "chinese-simplified": {
            _CJK_SCRIPT_INFO_KEY:   [("Han", "zh-Hans")],
            _CJK_URL_COMPONENT_KEY: "SimplifiedChinese/",
            _CJK_CODE_KEY:          "SC"
        },
    "chinese-traditional": {
            _CJK_SCRIPT_INFO_KEY:   [("Han", "zh-Hant"), ("Bopomofo", "")],
            _CJK_URL_COMPONENT_KEY: "TraditionalChinese/",
            _CJK_CODE_KEY:          "TC",
        },
    "chinese-hongkong": {
            _CJK_SCRIPT_INFO_KEY:   [("Han", "zh-Hant-HK")],
            _CJK_URL_COMPONENT_KEY: "TraditionalChineseHK/",
            _CJK_CODE_KEY:          "HK",
        },
    "japanese": {
            _CJK_SCRIPT_INFO_KEY:   [("Katakana", ""), ("Hiragana", ""), ("Katakana_Or_Hiragana", ""), ("Han", "ja")],
            _CJK_URL_COMPONENT_KEY: "Japanese/",
            _CJK_CODE_KEY:          "JP",
        },
    "korean": {
            _CJK_SCRIPT_INFO_KEY:   [("Hangul", ""), ("Han", "ko")],
            _CJK_URL_COMPONENT_KEY: "Korean/",
            _CJK_CODE_KEY:          "KR",
        },
}
'''Data needed to create FontInfo records for Noto CJK fonts.'''


def _get_noto_cjk_fonts(filter_func = None):
    '''Return a list of FontInfo records for the CJK Google Noto fonts.'''
    font_infos = []
    for lang, lang_data in _CJK_DATA.items():
        cjk_code = lang_data[_CJK_CODE_KEY]
        url_component = lang_data[_CJK_URL_COMPONENT_KEY]
        script_infos = lang_data[_CJK_SCRIPT_INFO_KEY]
        for form in [FontForm.SANS_SERIF, FontForm.SERIF]:
            form_name = "Sans" if form is FontForm.SANS_SERIF else "Serif"
            lang_fonts = []
            for weight_name, weight in _CJK_WEIGHTS:
                # We're using the language-specific OTF versions of the Noto CJK fonts.
                family_name = f"Noto {form_name} CJK {cjk_code.upper()}"
                postscript_name = f"Noto{form_name}CJK{cjk_code.lower()}-{weight_name}"
                url = f"{NOTO_CJK_BASE_URL}{form_name}/OTF/{url_component}{postscript_name}.otf"
                lang_fonts.append(
                    FontInfo(main_script="", script_variant="", family_name=family_name, subfamily_name=weight_name,
                            postscript_name=postscript_name, form=form, width=FontWidth.NORMAL,
                            weight=weight, style=FontStyle.UPRIGHT, format=FontFormat.OTF,
                            build=FontBuild.FULL, url=url
                            )                
                )
            
            for main_script, script_variant in script_infos:
                for font_info in lang_fonts:
                    font_info = copy.copy(font_info)
                    font_info.main_script = main_script
                    font_info.script_variant = script_variant
                    if filter_func is None or filter_func(font_info):
                        font_infos.append(font_info)
    return font_infos

def _get_noto_emoji_fonts(filter_func = None):
    '''Return a list of FontInfo records for Google Noto emoji fonts. Currently just Noto Color Emoji.'''
    font_infos = []
    font_info = FontInfo(main_script="Common", script_variant="Emoji", family_name="Noto Color Emoji",
                        subfamily_name="Regular", postscript_name="NotoColorEmoji",
                        form=FontForm.UNSET, width=FontWidth.NORMAL, weight=FontWeight.REGULAR,
                        style=FontStyle.UPRIGHT, format=FontFormat.TTF, build=FontBuild.UNSET,
                        # Note: This url may not be the fully-built version of the font:
                        url="https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf")
    if filter_func is None or filter_func(font_info):
        font_infos.append(font_info)
    return font_infos
    
