'''
## Overview

**fontfinder is a Python package for finding and installing fonts for Unicode scripts. It's useful
when generating documents that must specify a font family and will be viewed across multiple platforms.**
For now, `fontfinder` mostly locates fonts in the [Google Noto font collection](https://fonts.google.com/noto).

Font enumeration and installation is currently supported on macOS (using CoreText) and Windows (using DirectWrite).

Most functionality is provided by instantiating the `FontFinder` class.

## Examples

```python
>>> from fontfinder import FontFinder
>>> ff = FontFinder()
>>> text = 'الشمس (رمزها: ☉) هي النجم المركزي للمجموعة الشمسية.' # From Arabic Wikipedia article about the Sun
>>> ff.analyse(text)
TextInfo(main_script='Arabic', script_variant='', emoji_count=1, script_count=Counter({'Arabic': 39, 'Common': 12}))
>>> known_families = ff.find_families(text) # Available font families for the given text
>>> print(known_families)
['Noto Kufi Arabic', 'Noto Naskh Arabic', 'Noto Naskh Arabic UI', 'Noto Sans Arabic']
>>> preferred_family = ff.find_family(text) # Selects a single preferred font family for the text
>>> print(preferred_family)
Noto Naskh Arabic
>>> print(ff.installed_families(preferred_family)) # The font family is not yet installed
[]
>>> family_fonts = ff.find_family_fonts(preferred_family)
>>> print([font_info.postscript_name for font_info in family_fonts]) # The individual fonts in the family
['NotoNaskhArabic-Bold', 'NotoNaskhArabic-Medium', 'NotoNaskhArabic-Regular', 'NotoNaskhArabic-SemiBold']
>>> from tempfile import TemporaryDirectory
>>> tempdir = TemporaryDirectory()
>>> fonts_for_download = ff.find_family_fonts_to_download(preferred_family) # The indiv fonts that can be downloaded
>>> fonts_for_install = ff.download_fonts(fonts_for_download, tempdir.name) # The downloaded fonts
>>> ff.install_fonts(fonts_for_install) # Actually install each individual font
>>> print(ff.installed_families(preferred_family)) # The font family is now installed
['Noto Naskh Arabic']
>>> ff.uninstall_fonts(fonts_for_install) # Uninstall each individual font
>>> print(ff.installed_families(preferred_family)) # The font family is once again not installed
[]
>>> tempdir.cleanup()
```

## Attribution

Parts of this library are derived from code in the FindSystemFontsFilename
library by moi15moi (https://github.com/moi15moi/FindSystemFontsFilename/), under the MIT Licence.

See ACKNOWLEDGEMENTS for more detail.

## Installation

   `pip install fontfinder`

## Build Instructions

Use these instructions if you’re building from the source. `fontfinder` has been developed on Python 3.10, but should
work on other versions as well.

1. `git clone https://github.com/multiscript/fontfinder/`
1. `cd fontfinder`
1. `python3 -m venv venv` (Create a virtual environment.)
   - On Windows: `python -m venv venv`
1. `source venv/bin/activate` (Activate the virtual environment.)
   - In Windows cmd.exe: `venv\\Scripts\\activate.bat`
   - In Windows powershell: `.\\venv\\Scripts\\Activate.ps1` You may first need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
1. For development work...
   - `pip install -e .` (Creates an editable local install)
1. ...or to build the package:
   - `pip install build`
   - `python -m build`

## Top-Level Objects
'''
from collections import Counter
import json
from pathlib import Path
import tempfile
from typing import Iterable

import platformdirs
import requests
import unicodedataplus as udp

from fontfinder.model import TextInfo
from fontfinder.filters import *
from fontfinder.model import *
from fontfinder import _platforms


_REF_DATA_DIR_PATH = Path(__file__, "../data").resolve()
'''Path to reference font data (within package)'''
_REF_DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)

_USER_DATA_DIR_PATH = platformdirs.user_data_path("fontfinder")
'''Path to user data path for fontfinder (outside of package)'''
_USER_DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)

_SMALL_UNIHAN_PATH = Path(_REF_DATA_DIR_PATH, "small_unihan.json").resolve()
'''Path to subset of Unihan data needed for CJK font selection.'''

_SCRIPT_METADATA_URL = "https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-core/scriptMetadata.json"
'''URL of script metadata from the Unicode Common Locale Data Repository (CLDR).'''

_SCRIPT_METADATA_PATH = Path(_REF_DATA_DIR_PATH, "scriptMetadata.json").resolve()
'''Path to local copy of script metadata from the Unicode Common Locale Data Repository (CLDR).'''

# We wait until now to import Noto data so that data path constants above are set.
from fontfinder import noto 


class FontFinder:
    '''Main class for accessing this library's functionality.'''
    def __init__(self):
        self._all_known_fonts: list[FontInfo] | None = None
        self._small_unihan_data_private: dict[str, dict] | None = None
        self._script_metadata_private: dict[str, dict] | None = None
        
        self.max_analyse_chars: int = 2048
        '''Maximum number of characters examined by `FontFinder.analyse().'''
        
        self.zh_hant_use_hk = False
        '''If True, `FontFinder.analyse()` selects Hong Kong rather than Taiwanese fonts for Traditional
        Chinese script.'''

        self.family_prefs = {}
        '''Font preferences for selecting a single font-family for some text. This attribute is a dictionary of lists
        of filter functions. See `set_prefs()` for more info.'''

        self.family_font_prefs = {}
        '''Font preferences for selecting font files within a given font-family. This attribute is a dictionary of
        lists of filter functions. See `set_prefs()` for more info.'''

        self.set_prefs()
        self.set_platform_prefs()

    def set_prefs(self) -> None:
        '''Sets the font preferences. See the source code for this method to examine the built-in preferences
        that `fontfinder` uses 'out-of-the-box'. These can be replaced either by overriding this method, or editing
        the `font_family_prefs` and `family_member_prefs` instance attributes.
        
        Font preferences are dictionaries of lists of filter functions. The dictionary keys are one of:
        - A tuple of `(main_script, script_variant)`. Preferences under these keys will only apply to that particular
          script and variant combination.
        - the `fontfinder.ANY_SCRIPT` object. Preferences under this key will apply to any script.
        
        Preferences for particular script/variant combinations are applied before preferences for `ANY_SCRIPT`.
        
        The dictionary values are lists of filter functions. Filter functions take a single
        `fontfinder.model.FontInfo` argument and return True if the argument should be included in the filtered list.
        It's usually easiest to create filter functions using the filter factores in the `fontfinder.filters` module.
        
        If applying a preference would result in all remaining fonts being excluded, the preference is ignored.

        Some example preferences:
        ```python
        # For Arabic, prefer the more traditional Naskh form
        self.family_prefs[("Arabic", "")] = [attr_in("family_name", ["Noto Naskh Arabic"])]

        # Prefer sans-serif fonts, and exclude mono, display and UI forms where possible.
        self.family_prefs[ANY_SCRIPT] = [attr_in("form",           [FontForm.SANS_SERIF]),
                                         attr_not_contains("tags", [FontTag.MONO, FontTag.DISPLAY, FontTag.UI])]
        ```
        '''
        # For Adlam, prefer joined to unjoined.
        self.family_prefs[("Adlam", "")] = [attr_in("family_name", ["Noto Sans Adlam"])]
        # For Arabic, prefer the more traditional Naskh form
        self.family_prefs[("Arabic", "")] = [attr_in("family_name", ["Noto Naskh Arabic"])]
        # For Hebrew, prefer the more traditional Serif form
        self.family_prefs[("Hebrew", "")] = [attr_in("family_name", ["Noto Serif Hebrew"])]
        # For Khitan Small Script, prefer Noto Serif Khitan Small Script, as the purpose of the other fonts isn't clear
        self.family_prefs[("Khitan_Small_Script", "")] = [attr_in("family_name",
                                                                 ["Noto Serif Khitan Small Script"])]
        # For Lao, prefer more traditional looped fonts
        self.family_prefs[("Lao", "")] = [attr_contains_str("family_name", ["Looped"])]
        # For Nko, prefer Noto Sans NKo to unjoined
        self.family_prefs[("Nko", "")] = [attr_in("family_name", ["Noto Sans NKo"])]
        # For Nushu, prefer Noto Sans Nushu as it is better for smaller font sizes
        self.family_prefs[("Nushu", "")] = [attr_in("family_name", ["Noto Sans Nushu"])]
        # For Tamil, don't use the Supplement font
        self.family_prefs[("Tamil", "")] = [attr_not_contains_str("family_name", ["Supplement"])]
        # For Thai, prefer more traditional looped fonts, and Noto Sans Thai Looped in particular
        self.family_prefs[("Thai", "")] = [attr_in("family_name", ["Noto Sans Thai Looped"])]
        # Prefer sans-serif fonts, and exclude mono, display and UI forms where possible.
        self.family_prefs[ANY_SCRIPT] = [attr_in("form",           [FontForm.SANS_SERIF]),
                                         attr_not_contains("tags", [FontTag.MONO, FontTag.DISPLAY, FontTag.UI])]
        
        # With a font family, avoid variable fonts, and mono, display and UI fonts. Prefer full builds, and OTF files.
        self.family_font_prefs[ANY_SCRIPT] = [attr_not_in("width",      [FontWidth.VARIABLE]),
                                              attr_not_in("weight",     [FontWidth.VARIABLE]),
                                              attr_not_contains("tags", [FontTag.MONO, FontTag.DISPLAY, FontTag.UI]),
                                              attr_in("build",          [FontBuild.FULL]),
                                              attr_in("build",          [FontBuild.HINTED]),
                                              attr_in("format",         [FontFormat.OTF]),
                                              attr_in("format",         [FontFormat.TTF]),
                                              attr_in("format",         [FontFormat.OTC]),
                                             ]

    def set_platform_prefs(self) -> None:
        '''Sets any platform-specific font preferences. See the source code in the various sub-modules in
        `_platforms` to examine the built-in platform-specific preferences.
        
        This method is called only after `set_prefs()` has set the platform-independant font preferences.'''
        font_platform = _platforms.get_font_platform()
        font_platform.set_platform_prefs(self)       

    def analyse(self, text: str) -> TextInfo:
        '''Analyse an initial portion of `text` for the Unicode scripts it uses. Returns a
        `fontfinder.model.TextInfo` object with the results.

        The number of characters analysed is set by the instance attribute `max_analyse_chars`.

        The attributes of the `TextInfo` result object are set as follows:
        - `main_script`:    Name of the most-frequently-used Unicode script in `text`. This is the [long Unicode
                            script value (known as a property value
                            alias)](https://unicode.org/reports/tr24/#Script_Value_Aliases), rather than the shorter
                            script code.

        - `script_variant`: A secondary string used when the value of `main_script` is insufficient for choosing
                            an appropriate font. This is not a Unicode property, but a scheme only used by
                            `fontfinder`.

        - `emoji_count`:    Count of characters who have either the Emoji Presentation property or the
                            Extended_Pictographic property set (independent of script).

        - `script_count`:   A [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter)
                            of the count of each Unicode script in the text. The keys are the string names of each
                            script that appears in the text (including `Common`, `Inherited` and `Unknown`).

        In calculating `main_script`, the script values `Common`, `Inherited`, and `Unknown` are
        ignored. However if `emoji_count` is larger than the rest of the script counts, then `main_script` is set to
        `Common` and `script_variant` is set to `Emoji`. (Most emoji characters have a Unicode script value of
        `Common`.)
        
        If `main_script` is `Han`, some basic language detection is performed, and the `script_variant` is set to
        one of the following language tags:
        - For Simplified Chinese:  `zh-Hans`                   
        - For Traditional Chinese: `zh-Hant` (or `zh-Hant-HK` if the instance attribute `zh_hant_use_hk` is True)
        - For Japanese:            `ja`
        - For Korean:              `ko`
        '''
        # Do the counting
        script_count = Counter()
        unihan_counter = Counter()
        emoji_count = 0
        for char in text[0:min(len(text), self.max_analyse_chars)]:
            script_count[udp.script(char)] += 1
            if udp.is_emoji_presentation(char) or udp.is_extended_pictographic(char):
                emoji_count += 1
            if char in self._small_unihan_data:
                for key in self._small_unihan_data[char].keys():
                    unihan_counter[key] += 1
        
        # Determine main_script and script_variant
        non_generic_count = script_count.copy()
        generic_scripts = ['Common', 'Inherited', 'Unknown']
        for generic_script in generic_scripts:
            del non_generic_count[generic_script]

        if len(non_generic_count) > 0:
            main_script = non_generic_count.most_common(1)[0][0]
            script_variant = ""
        else:
            main_script = ""
            script_variant = ""

        # Handle emoji
        if (len(non_generic_count) == 0 and emoji_count > 0) or \
           (len(non_generic_count) > 0  and emoji_count > non_generic_count.most_common(1)[0][1]):
            main_script = "Common"
            script_variant = "Emoji"

        # Handle Han script
        if main_script == 'Han':
            # Han script can be used by Chinese, Japanese and Korean texts
            if 'Hangul' in script_count:
                # If Hangul characters are present, assume it's Korean
                script_variant = 'ko'
            elif 'Hiragana' in script_count or 'Katakana' in script_count:
                # If Hirogana or Katakana characters are present, assume it's Japanese
                script_variant = 'ja'
            elif unihan_counter['kSimplifiedVariant'] > unihan_counter['kTraditionalVariant']:
                # Traditional Chinese characters have simplified variants, and vice versa.
                # So if there are more simplified variants than traditional, we likely have traditional text,
                # and vice-versa.
                script_variant = 'zh-Hant-HK' if self.zh_hant_use_hk else 'zh-Hant'
            else:
                script_variant = 'zh-Hans'

        return TextInfo(main_script=main_script, script_variant=script_variant, emoji_count=emoji_count,
                        script_count=script_count)

    def find_families(self, str_or_text_info: str | TextInfo) -> list[str]:
        '''Returns a list of the family names (strings) of all fonts known to the library that are suitable for
        `str_or_text_info`. No font family preferences are applied. If no suitable family names are found,
        an empty list is returned.
        
        `str_or_text_info` should either be the text string itself, or a `TextInfo` object returned by `analyse()`.
        '''
        font_infos = self._text_info_to_font_infos(str_or_text_info)
        # We use a dictionary as a set that preserves insertion order, to return families in their original order.
        family_names = {font_info.family_name: 1 for font_info in font_infos}
        return list(family_names.keys())

    def find_family(self, str_or_text_info: str | TextInfo) -> str | None:
        '''Returns the family name (a string) of the preferred font family for `str_or_text_info`.
        The preferred font family is determined applying the filter functions in `family_prefs`.
        If, after applying these filters, more than one family remains, the first family is returned.
        If no preferred font family is found, None is returned.
        
        `str_or_text_info` should either be the text string itself, or a `TextInfo` object returned by `analyse()`.
        '''
        font_infos = self._text_info_to_font_infos(str_or_text_info)
        if len(font_infos) == 0:
            return None
        count_func = lambda font_infos: len({font_info.family_name for font_info in font_infos})
        font_infos = self._apply_pref_dict(font_infos[0].main_script, font_infos[0].script_variant,
                                           self.family_prefs, count_func, font_infos)
        family_name = font_infos[0].family_name
        return family_name

    def find_family_fonts(self, family_name_or_names: str | Iterable[str], main_script:str | None = None,
                          script_variant:str | None = None) -> list[FontInfo]:
        '''Returns a list of `FontInfo` objects for font files matching the given font family names.
        The list is filtered using the functions in `family_font_prefs`.
         
        `family_name_or_names` can be a single font family name, or an iterable of family names.

        Some font families match several Unicode scripts. In these cases, `main_script` and `script_variant`
        can optionally be specified, to ensure these fields have the correct value in the returned `FontInfo` list.
        Otherwise, `main_script` and `script_variant` will have the first values found within the given font families.
        '''
        family_names = family_name_or_names
        if isinstance(family_names, str):
            family_names = [family_names]
        
        result_font_infos = []
        for family_name in family_names:
            font_infos = self.known_fonts(lambda font_info: font_info.family_name == family_name)
            if len(font_infos) == 0:
                continue
            # font_infos can be duplicated under multiple script variants. If no script and variant is specified, we
            # just pick the first.
            if main_script is None:
                family_main_script = font_infos[0].main_script
            else:
                family_main_script = main_script
            if script_variant is None:
                family_script_variant = font_infos[0].script_variant
            else:
                family_script_variant = script_variant
            font_infos = [font_info for font_info in font_infos if font_info.main_script == family_main_script and \
                                                                font_info.script_variant == family_script_variant]
            count_func = len
            font_infos = self._apply_pref_dict(main_script, script_variant, self.family_font_prefs, count_func,
                                            font_infos)
            result_font_infos.extend(font_infos)
        return result_font_infos

    def find_family_fonts_to_download(self, family_name_or_names: str | Iterable[str], main_script:str | None = None,
                                      script_variant:str | None = None) -> list[FontInfo]:
        '''Returns a list of `FontInfo` objects for font files that need to be downloaded. This list is formed
        by finding fonts matching the given family names, where those families are not currently installed,
        the filters in `family_font_prefs` have been applied, and the fonts have download URLs provided.

        If the returned list is empty, then no fonts need to be downloaded, either because the font families are
        already installed, or no download URLs are provided.
        
        `family_name_or_names` can be a single font family name, or an iterable of family names.

        Some font families match several Unicode scripts. In these cases, `main_script` and `script_variant`
        can optionally be specified, to ensure these fields have the correct value in the resulting `FontInfo` list.
        Otherwise, `main_script` and `script_variant` will have the first values found within the given font families.
        '''
        family_names = self.not_installed_families(family_name_or_names)
        font_infos = self.find_family_fonts(family_names, main_script, script_variant)
        font_infos = self.downloadable_fonts(font_infos)
        return font_infos

    def download_fonts(self, font_infos: Iterable[FontInfo], download_dir: str | Path) -> list[FontInfo]:
        '''Downloads the font files in `font_infos`, in preparation for installation. The font files are downloaded
        to `download_dir`. Returns a list of copied `FontInfo` objects where the `downloaded_path` attribute points
        to each new file.'''
        download_dir = Path(download_dir)
        # Filter font_infos to only those that have download URLs
        font_infos = self.downloadable_fonts([font_info.copy() for font_info in font_infos])
        for font_info in font_infos:
            response = requests.get(font_info.url, stream=True)
            if font_info.filename is None:
                continue
            font_info.downloaded_path = download_dir / font_info.filename
            with open(font_info.downloaded_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
        return font_infos

    def install_fonts(self, font_infos: Iterable[FontInfo]) -> None:
        '''Install the font files in `font_infos`. The `downloaded_path` of each `FontInfo` must point to the
        actual font file in the filesystem.
        
        Font are installed to the user font collection, rather than the system-wide font collection.'''
        font_platform = _platforms.get_font_platform()
        font_platform.install_fonts(font_infos)        
     
    def uninstall_fonts(self, font_infos: Iterable[FontInfo]) -> None:
        '''Uninstall the font files in `font_infos`. The fonts must exist in the user font collection, otherwise they
        will not be uninstalled.
        '''
        font_platform = _platforms.get_font_platform()
        font_platform.uninstall_fonts(font_infos)        

    def is_rtl(self, script_or_text_info: str | TextInfo) -> bool:
        '''Returns True if the text direction of the given Unicode script is right-to-left, otherwise False.
        If the script name is not found, returns False.
        
        `script_or_text_info` must be either the long script name (i.e. the Unicode property value alias), or a
        `TextInfo` object, in which case the `main_script` attribute of the `TextInfo` will be used.
        '''
        long_script = script_or_text_info
        if isinstance(long_script, TextInfo):
            long_script = long_script.main_script

        short_script = udp.property_value_aliases["script"].get(long_script, [None])[0]
        if short_script is None:
            return False
        is_rtl = (self._script_metadata[short_script]["rtl"] == "YES")
        return is_rtl

    def known_fonts(self, filter_func = None) -> list[FontInfo]:
        '''Returns a list of FontInfo objects for all fonts known to this library.
        
        This is a large list, which is cached in memory the first time the method is called.'''
        # Even though noto.get_noto_fonts() can filter on the fly, for now we choose to optimise for speed, rather
        # than memory, by caching the full list of font_infos in memory.
        if self._all_known_fonts is None:
            self._all_known_fonts = []
            self._all_known_fonts.extend(noto.get_noto_fonts())
            font_platform = _platforms.get_font_platform()
            self._all_known_fonts.extend(font_platform.known_platform_fonts())

        return [font_info for font_info in self._all_known_fonts if (filter_func is None or filter_func(font_info))]

    def known_scripts(self, filter_func = None) -> list[str]:
        '''Returns a list of the `main_script` values for all the fonts known to this library.'''
        return sorted(set([info.main_script for info in self.known_fonts(filter_func)]))

    def known_script_variants(self, filter_func = None) -> list[tuple[str, str]]:
        '''Returns a list of `(main_script, script_variant)` tuples for all the fonts known to this library.'''
        # Use a dictionary as an ordered set
        return list({(info.main_script, info.script_variant): 1 for info in self.known_fonts(filter_func)}.keys())

    def all_unicode_scripts(self) -> list[str]:
        '''Returns a list of all script values (property value aliases) in the Unicode standard.'''
        return list(udp.property_value_aliases['script'].keys())

    def scripts_not_known(self) -> list[str]:
        '''Returns a list of all the Unicode script values not supported by the fonts known to this library.'''
        return sorted(set(self.all_unicode_scripts()) - set(self.known_scripts()) -
                      set(["Common", "Inherited", "Unknown"]))

    def all_installed_families(self) -> list[str]:
        '''Returns a list of the family names of all fonts currently installed on the system.
        '''
        font_platform = _platforms.get_font_platform()
        return font_platform.all_installed_families()        

    def installed_families(self, family_name_or_names: str | Iterable[str]) -> list[str]:
        '''For a given font family name or iterable of names, return a filtered list containing just those
        families that are currently installed on the system.'''
        family_names = family_name_or_names
        if isinstance(family_names, str):
            family_names = [family_names]
        all_installed_families = set(self.all_installed_families())
        return [family_name for family_name in family_names if family_name in all_installed_families]

    def not_installed_families(self, family_name_or_names: str | Iterable[str]) -> list[str]:
        '''For a given font family name or iterable of names, return a filtered list containing just those
        families that are not currently installed on the system.'''
        family_names = family_name_or_names
        if isinstance(family_names, str):
            family_names = [family_names]
        all_installed_families = set(self.all_installed_families())
        return [family_name for family_name in family_names if family_name not in all_installed_families]

    def downloadable_fonts(self, font_infos: Iterable[FontInfo]) -> list[FontInfo]:
        '''For a given iterable of `font_infos`, return a filtered list containing just those `FontInfo`s that
        have download URLs provided.'''
        return [font_info for font_info in font_infos if font_info.url is not None and font_info.url != ""]

    @property
    def _small_unihan_data(self) ->  dict[str, dict]:
        if self._small_unihan_data_private is None:
            with open(_SMALL_UNIHAN_PATH, "r", encoding="utf-8") as small_unihan_file:
                self._small_unihan_data_private = json.load(small_unihan_file)
            assert self._small_unihan_data_private is not None
        return self._small_unihan_data_private

    @property
    def _script_metadata(self) ->  dict[str, dict]:
        if self._script_metadata_private is None:
            with open(_SCRIPT_METADATA_PATH, "r", encoding="utf-8") as script_metadata_file:
                self._script_metadata_private = json.load(script_metadata_file)["scriptMetadata"]
            assert self._script_metadata_private is not None
        return self._script_metadata_private

    def _text_info_to_font_infos(self, str_or_text_info):
        if isinstance(str_or_text_info, str):
            text_info = self.analyse(str_or_text_info)
        else:
            text_info = str_or_text_info
        font_infos = self.known_fonts(lambda font_info: font_info.main_script == text_info.main_script and \
                                                        font_info.script_variant == text_info.script_variant)
        return font_infos

    def _apply_pref_dict(self, main_script, script_variant, pref_dict, count_func, font_infos):
        # Preferences for particular scripts are applied before preferences for any script
        pref_keys = [(main_script, script_variant), ANY_SCRIPT]
        for pref_key in pref_keys:
            if pref_key in pref_dict:
                font_infos = self._apply_pref_filters(pref_dict[pref_key], count_func, font_infos)
        return font_infos

    def _apply_pref_filters(self, filter_funcs, count_func, font_infos):
        cur_list = font_infos
        count = count_func(cur_list)
        # print(f"Initial ({count})")
        # print([info.url for info in font_infos])
        # print()
        if count < 2 or len(filter_funcs) == 0:
            # We actually don't need to filter.
            return cur_list

        # print("After each filter func")
        for filter_func in filter_funcs:
            new_list = [font_info for font_info in cur_list if filter_func(font_info)]
            count = count_func(new_list)
            # print(count)
            # print([info.url for info in new_list])
            # print()
            if count == 0:
                # This preference was too restrictive, so we ignore it by not updating cur_list
                pass
            elif count == 1:
                # Perfect! Stop filtering
                cur_list = new_list
                break
            else:
                # Keep filtering
                cur_list = new_list
        return cur_list


ANY_SCRIPT = object()
'''Sentinel for preference matching on any script.'''


class FontFinderException(Exception):
    '''Base Exception class for this library.'''
    pass


class UnsupportedPlatformException(FontFinderException):
    '''Raised when an operation is not supported on the current operating system.'''
    pass

