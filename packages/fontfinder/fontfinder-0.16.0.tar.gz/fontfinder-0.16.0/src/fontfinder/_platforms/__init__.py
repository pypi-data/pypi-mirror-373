from ctypes import CFUNCTYPE
import ctypes.util
import platform
from typing import Iterable

import fontfinder

class CTypesLibrary:
    IN:  int    = 1
    OUT: int    = 2
    IN0: int    = 4

    def __init__(self, library_loader, library_name: str, find_library: bool = False, alt_pathname: str = None):
        '''`alt_pathname` is an alternative pathname to try if a library named `library_name` cannot be found.
        '''
        if find_library:
            library_name = ctypes.util.find_library(library_name)
            if library_name is None:
                library_name = alt_pathname
        self.lib = library_loader.LoadLibrary(library_name)

    # Inspired by https://www.cs.unc.edu/~gb/blog/2007/02/11/ctypes-tricks/
    def prototype(self, functype, result_type, func_name, *arg_items):
        '''
        Each arg_item should be
        (in_or_out_const, arg_type[, param_name_str[, default_value]])
        '''
        arg_types = []
        param_flags = []
        for arg_item in arg_items:
            arg_types.append(arg_item[1])
            param_flag = [arg_item[0]]
            if len(arg_item) > 2:
                param_flag.append(arg_item[2])
            if len(arg_item) > 3:
                param_flag.append(arg_item[3])
            param_flags.append(tuple(param_flag))
        return functype(result_type, *arg_types)((func_name, self.lib), tuple(param_flags))

    def c_prototype(self, result_type, func_name, *arg_items):
        '''
        Each arg_item should be
        (in_or_out_const, arg_type[, param_name_str[, default_value]])
        '''
        return self.prototype(CFUNCTYPE, result_type, func_name, *arg_items)

    def w_prototype(self, result_type, func_name, *arg_items):
        '''
        Each arg_item should be
        (in_or_out_const, arg_type[, param_name_str[, default_value]])
        '''
        from ctypes import WINFUNCTYPE
        return self.prototype(WINFUNCTYPE, result_type, func_name, *arg_items)


class FontPlatform:
    def __init__(self):
        pass

    def all_installed_families():
        '''Return a list of font family names available on this platform.'''
        pass

    def install_fonts(self, font_infos: Iterable[fontfinder.FontInfo]) -> None:
        '''Install the font files in `font_infos`. The `downloaded_path` of each `FontInfo` must point to the
        actual font file in the filesystem.
        
        Font are installed to the user font collection, rather than the system-wide font collection.'''
        pass

    def uninstall_fonts(self, font_infos: Iterable[fontfinder.FontInfo]) -> None:
        '''Uninstall the font files in `font_infos`. The fonts must exist in the user font collection, otherwise they
        will not be uninstalled.
        '''
        pass

    def known_platform_fonts(self) -> list[fontfinder.FontInfo]:
        '''Returns a list of FontInfo objects for all fonts known to this library that are unique to this platform.
        '''
        pass

    def set_platform_prefs(self, font_finder: 'fontfinder.FontFinder') -> None:
        pass


def get_font_platform():
    if platform.system() == "Darwin":
        import fontfinder._platforms.mac
        return fontfinder._platforms.mac.MacPlatform()
    elif platform.system() == "Windows":
        import fontfinder._platforms.windows
        return fontfinder._platforms.windows.WindowsPlatform()
    else:
        raise fontfinder.UnsupportedPlatformException()

