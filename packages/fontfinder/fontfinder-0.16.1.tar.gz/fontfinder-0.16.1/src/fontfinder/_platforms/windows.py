# Code in this module derived from FindSystemFontFilename project, under the MIT Licence:
# https://github.com/moi15moi/FindSystemFontsFilename/
#
# See ACKNOWLEDGEMENTS file.
#
import platform
if platform.system() == "Windows":
    import comtypes
    from comtypes import COMError, GUID, HRESULT, IUnknown, STDMETHOD, WINFUNCTYPE
    from sys import getwindowsversion
    import winreg
    from ctypes import wintypes

    import ctypes
    from ctypes import byref, POINTER
    import os
    from pathlib import Path
    import shutil

    from fontfinder import FontFinder, FontFinderException
    import fontfinder._platforms


    USER_FONT_DIR = Path("~\\AppData\\Local\\Microsoft\\Windows\\Fonts").expanduser()
    USER_FONT_REG_PATH = "Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts"


    class WindowsPlatform(fontfinder._platforms.FontPlatform):
        def all_installed_families(self):
            dw = DirectWriteLibrary()
            dw_factory = POINTER(IDWriteFactory)()
            dw.DWriteCreateFactory(dw.DWRITE_FACTORY_TYPE_ISOLATED, IDWriteFactory._iid_, byref(dw_factory))

            fonts = POINTER(IDWriteFontCollection)()
            dw_factory.GetSystemFontCollection(byref(fonts), False)

            # Use a dict as an ordered set
            family_names = {}
            for i in range(fonts.GetFontFamilyCount()):
                font_family = POINTER(IDWriteFontFamily)()
                fonts.GetFontFamily(i, byref(font_family))

                family_name_strings = POINTER(IDWriteLocalizedStrings)()
                font_family.GetFamilyNames(byref(family_name_strings))

                name_index = 0
                name_len = ctypes.c_uint32()
                family_name_strings.GetStringLength(name_index, byref(name_len))

                name_buffer = ctypes.create_unicode_buffer(name_len.value+1)
                family_name_strings.GetString(name_index, name_buffer, name_len.value+1)
                family_names[name_buffer.value] = 1
            return list(family_names.keys())

        def install_fonts(self, font_infos):
            user32 = User32Library()
            reg_font_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, USER_FONT_REG_PATH)
            for font_info in font_infos:
                dest_path = USER_FONT_DIR / font_info.filename
                font_family_subfamily = f"{font_info.family_name} {font_info.subfamily_name}".strip()
                if font_info.downloaded_path is not None and font_info.downloaded_path != Path():
                    shutil.copy2(font_info.downloaded_path, USER_FONT_DIR)
                else:
                    raise FontFinderException("Can't install font without a path to the downloaded font file")
                winreg.SetValueEx(reg_font_key, font_family_subfamily, 0, winreg.REG_SZ, str(dest_path))
            reg_font_key.Close()
            user32.SendNotifyMessageW(user32.HWND_BROADCAST, user32.WM_FONTCHANGE, 0, 0)

        def uninstall_fonts(self, font_infos):
            user32 = User32Library()
            reg_font_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, USER_FONT_REG_PATH)
            for font_info in font_infos:
                if font_info.family_name is None or font_info.family_name == "":
                    raise FontFinderException("Can't uninstall font without a family name")
                winreg.DeleteValue(reg_font_key, font_info.fullname)
                if font_info.filename is None:
                    raise FontFinderException("Can't uninstall font without a filename")
                os.remove(USER_FONT_DIR / font_info.filename)
            reg_font_key.Close()
            user32.SendNotifyMessageW(user32.HWND_BROADCAST, user32.WM_FONTCHANGE, 0, 0)

        def known_platform_fonts(self) -> list[fontfinder.FontInfo]:
            # Use Segoe UI Emoji for emoji.
            font_infos = []
            font_infos.append(fontfinder.FontInfo(main_script="Common", script_variant="Emoji",
                            family_name="Segoe UI Emoji",
                            subfamily_name="Regular", postscript_name="SegoeUIEmoji",
                            form=fontfinder.FontForm.UNSET, width=fontfinder.FontWidth.NORMAL,
                            weight=fontfinder.FontWeight.REGULAR, style=fontfinder.FontStyle.UPRIGHT,
                            format=fontfinder.FontFormat.TTF, build=fontfinder.FontBuild.UNSET,
                            url=""))
            return font_infos
        
        def set_platform_prefs(self, font_finder: FontFinder) -> None:
            # Use Segoe UI Emoji for emoji.
            font_finder.family_prefs[("Common", "Emoji")] = [fontfinder.filters.attr_in("family_name",
                                                                                        ["Segoe UI Emoji"])]


    class IDWriteLocalizedStrings(IUnknown):
        _iid_ = GUID("{08256209-099a-4b34-b86d-c22b110e7771}")
        _methods_ = [
            STDMETHOD(ctypes.c_uint32, "GetCount"),
            STDMETHOD(HRESULT, "FindLocaleName"),
            STDMETHOD(HRESULT, "GetLocaleNameLength"),
            STDMETHOD(HRESULT, "GetLocaleName"),
            STDMETHOD(HRESULT, "GetStringLength", [ctypes.c_uint32, POINTER(ctypes.c_uint32)]),
            STDMETHOD(HRESULT, "GetString", [ctypes.c_uint32, POINTER(wintypes.WCHAR), ctypes.c_uint32])
        ]


    class IDWriteFontList(IUnknown):
        # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontlist
        _iid_ = GUID("{1a0d8438-1d97-4ec1-aef9-a2fb86ed6acb}")
        _methods_ = [
            STDMETHOD(None, "GetFontCollection"),       # Not implemented here
            STDMETHOD(wintypes.UINT, "GetFontCount"),
            STDMETHOD(HRESULT, "GetFont"),              # Not implemented here
        ]


    class IDWriteFontFamily(IDWriteFontList):
        # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontfamily
        _iid_ = GUID("{da20d8ef-812a-4c43-9802-62ec4abd7add}")
        _methods_ = [
            STDMETHOD(None, "GetFamilyNames", [POINTER(POINTER(IDWriteLocalizedStrings))]),
            STDMETHOD(None, "GetFirstMatchingFont"),    # Not implemented here
            STDMETHOD(None, "GetMatchingFonts"),        # Not implemented here
        ]

    class IDWriteFontCollection(IUnknown):
        # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontcollection
        _iid_ = GUID("{a84cee02-3eea-4eee-a827-87c1a02a0fcc}")
        _methods_ = [
            STDMETHOD(wintypes.UINT, "GetFontFamilyCount"),
            STDMETHOD(HRESULT, "GetFontFamily", [wintypes.UINT, POINTER(POINTER(IDWriteFontFamily))]),
            STDMETHOD(None, "FindFamilyName"),          # Not implemented here
            STDMETHOD(None, "GetFontFromFontFace"),     # Not implemented here
        ]

    class IDWriteFactory(IUnknown):
        # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefactory
        _iid_ = GUID("{b859ee5a-d838-4b5b-a2e8-1adc7d93db48}")
        _methods_ = [
            STDMETHOD(HRESULT, "GetSystemFontCollection", [POINTER(POINTER(IDWriteFontCollection)), wintypes.BOOLEAN]),
            STDMETHOD(None, "CreateCustomFontCollection"),      # Not implemented here
            STDMETHOD(None, "RegisterFontCollectionLoader"),    # Not implemented here
            STDMETHOD(None, "UnregisterFontCollectionLoader"),  # Not implemented here
            STDMETHOD(None, "CreateFontFileReference"),         # Not implemented here
            STDMETHOD(None, "CreateCustomFontFileReference"),   # Not implemented here
            STDMETHOD(None, "CreateFontFace"),                  # Not implemented here
            STDMETHOD(None, "CreateRenderingParams"),           # Not implemented here
            STDMETHOD(None, "CreateMonitorRenderingParams"),    # Not implemented here
            STDMETHOD(None, "CreateCustomRenderingParams"),     # Not implemented here
            STDMETHOD(None, "RegisterFontFileLoader"),          # Not implemented here
            STDMETHOD(None, "UnregisterFontFileLoader"),        # Not implemented here
            STDMETHOD(None, "CreateTextFormat"),                # Not implemented here
            STDMETHOD(None, "CreateTypography"),                # Not implemented here
            STDMETHOD(None, "GetGdiInterop"),                   # Not implemented here
            STDMETHOD(None, "CreateTextLayout"),                # Not implemented here
            STDMETHOD(None, "CreateGdiCompatibleTextLayout"),   # Not implemented here
            STDMETHOD(None, "CreateEllipsisTrimmingSign"),      # Not implemented here
            STDMETHOD(None, "CreateTextAnalyzer"),              # Not implemented here
            STDMETHOD(None, "CreateNumberSubstitution"),        # Not implemented here
            STDMETHOD(None, "CreateGlyphRunAnalysis"),          # Not implemented here
        ]


    class DirectWriteLibrary(fontfinder._platforms.CTypesLibrary):
        def __init__(self):
            super().__init__(ctypes.windll, "dwrite")

            # I couldn't make this work using the ctypes function protype technique, so we just use the 
            # standard foreign function attribute technique.
            self.DWriteCreateFactory = self.lib.DWriteCreateFactory
            self.DWriteCreateFactory.restype = HRESULT
            self.DWriteCreateFactory.argtypes = [wintypes.UINT, GUID, POINTER(POINTER(IUnknown))]

            self.DWRITE_FACTORY_TYPE_SHARED = 0
            self.DWRITE_FACTORY_TYPE_ISOLATED = 1


    class User32Library(fontfinder._platforms.CTypesLibrary):
        def __init__(self):
            super().__init__(ctypes.windll, "User32")

            self.SendNotifyMessageW = self.w_prototype(
                wintypes.BOOL, "SendNotifyMessageW", (self.IN, wintypes.HWND, "hWnd"),
                                                     (self.IN, wintypes.UINT, "Msg"),
                                                     (self.IN, wintypes.WPARAM, "wParam"),
                                                     (self.IN, wintypes.LPARAM, "lParam")
            )

            self.HWND_BROADCAST = wintypes.HWND(0xffff)
            self.WM_FONTCHANGE = wintypes.UINT(0x001D)
