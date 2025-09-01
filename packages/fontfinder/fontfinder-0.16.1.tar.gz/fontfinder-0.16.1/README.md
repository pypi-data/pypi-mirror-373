# fontfinder

## Overview

**fontfinder is a Python package for finding and installing fonts for Unicode scripts. It's useful
when generating documents that must specify a font family and will be viewed across multiple platforms.**
For now, `fontfinder` mostly locates fonts in the [Google Noto font collection](https://fonts.google.com/noto).

Font enumeration and installation is currently supported on macOS (using CoreText) and Windows (using DirectWrite).

Most functionality is provided by instantiating the `FontFinder` class.

## Docs

See [multiscript.app/fontfinder](https://multiscript.app/fontfinder)

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
   - In Windows cmd.exe: `venv\Scripts\\activate.bat`
   - In Windows powershell: `.\\venv\Scripts\Activate.ps1` You may first need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
1. For development work...
   - `pip install -e .` (Creates an editable local install)
1. ...or to build the package:
   - `pip install build`
   - `python -m build`