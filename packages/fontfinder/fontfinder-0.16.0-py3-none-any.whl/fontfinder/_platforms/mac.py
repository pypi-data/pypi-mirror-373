# Code in this module derived from FindSystemFontFilename project, under the MIT Licence:
# https://github.com/moi15moi/FindSystemFontsFilename/
#
# See ACKNOWLEDGEMENTS file.
#
import platform
if platform.system() == "Darwin":
    from ctypes import c_bool, c_char_p, c_long, c_uint32, c_void_p, create_string_buffer
    import ctypes.util
    from pathlib import Path
    import os
    import shutil

    from packaging import version

    from fontfinder import FontFinder, FontFinderException
    import fontfinder._platforms
    import fontfinder.filters


    USER_FONT_DIR = Path("~/Library/Fonts").expanduser()


    class MacPlatform(fontfinder._platforms.FontPlatform):
        def all_installed_families(self):        
            if version.Version(platform.mac_ver()[0]) < version.Version('10.6'):
                raise Exception("fontfinder.mac.all_installed_families() only supported by macOS 10.6 or later")
            
            cf = CoreFoundationLibrary()
            ct = CoreTextLibrary()

            font_collection = ct.CTFontCollectionCreateFromAvailableFonts(None)
            font_array = ct.CTFontCollectionCreateMatchingFontDescriptors(font_collection)
            font_array_len = cf.CFArrayGetCount(font_array)
            family_names = set()
            for i in range(font_array_len):
                font_descriptor = cf.CFArrayGetValueAtIndex(font_array, i)

                family_cfstr = ct.CTFontDescriptorCopyAttribute(font_descriptor, ct.kCTFontFamilyNameAttribute)
                family_name = cf.cf_string_ref_to_python_str(family_cfstr)
                cf.CFRelease(family_cfstr)

                # style_cfstr = ct.CTFontDescriptorCopyAttribute(font_descriptor, ct.kCTFontStyleNameAttribute)
                # style_name = cf.cf_string_ref_to_python_str(style_cfstr)
                # cf.CFRelease(style_cfstr)

                # display_cfstr = ct.CTFontDescriptorCopyAttribute(font_descriptor, ct.kCTFontDisplayNameAttribute)
                # display_name = cf.cf_string_ref_to_python_str(display_cfstr)
                # cf.CFRelease(display_cfstr)

                # postscript_cfstr = ct.CTFontDescriptorCopyAttribute(font_descriptor, ct.kCTFontNameAttribute)
                # postscript_name = cf.cf_string_ref_to_python_str(postscript_cfstr)
                # cf.CFRelease(postscript_cfstr)

                family_names.add(family_name)
            cf.CFRelease(font_array)
            cf.CFRelease(font_collection)
            return sorted(list(family_names))

        def install_fonts(self, font_infos):
            for font_info in font_infos:
                if font_info.downloaded_path is not None and font_info.downloaded_path != Path():
                    shutil.copy2(font_info.downloaded_path, USER_FONT_DIR)
                else:
                    raise FontFinderException("Can't install font without a path to the downloaded font file")

        def uninstall_fonts(self, font_infos):
            for font_info in font_infos:
                if font_info.filename is None:
                    raise FontFinderException("Can't uninstall font without a filename")
                os.remove(USER_FONT_DIR / font_info.filename)

        def known_platform_fonts(self) -> list[fontfinder.FontInfo]:
            # Use Apple Color Emoji for emoji.
            font_infos = []
            font_infos.append(fontfinder.FontInfo(main_script="Common", script_variant="Emoji",
                            family_name="Apple Color Emoji",
                            subfamily_name="Regular", postscript_name="AppleColorEmoji",
                            form=fontfinder.FontForm.UNSET, width=fontfinder.FontWidth.NORMAL,
                            weight=fontfinder.FontWeight.REGULAR, style=fontfinder.FontStyle.UPRIGHT,
                            format=fontfinder.FontFormat.TTF, build=fontfinder.FontBuild.UNSET,
                            url=""))
            return font_infos
        
        def set_platform_prefs(self, font_finder: FontFinder) -> None:
            # Use Apple Color Emoji for emoji.
            font_finder.family_prefs[("Common", "Emoji")] = [fontfinder.filters.attr_in("family_name",
                                                                                        ["Apple Color Emoji"])]


    class CoreFoundationLibrary(fontfinder._platforms.CTypesLibrary):
        def __init__(self):
            super().__init__(ctypes.cdll, "CoreFoundation", True,
                            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
            # Note hack for compatibility with macOS 11.0 and later
            # From: https://github.com/pyglet/pyglet/blob/a44e83a265e7df8ece793de865bcf3690f66adbd/pyglet/libs/darwin/cocoapy/cocoalibs.py#L10-L14

            self.CFRelease = self.c_prototype(
                None, "CFRelease", (self.IN, c_void_p, "cf_object"))

            self.CFArrayGetCount = self.c_prototype(
                c_long, "CFArrayGetCount", (self.IN, c_void_p, "cf_array"))

            self.CFArrayGetValueAtIndex = self.c_prototype(
                c_void_p, "CFArrayGetValueAtIndex", (self.IN, c_void_p, "cf_array"), (self.IN, c_long, "index"))

            self.CFStringGetMaximumSizeForEncoding = self.c_prototype(
                c_long, "CFStringGetMaximumSizeForEncoding", (self.IN, c_long, "length"), (self.IN, c_uint32, "encoding"))

            self.CFStringGetLength = self.c_prototype(
                c_long, "CFStringGetLength", (self.IN, c_void_p, "the_string"))

            self.CFStringGetCString = self.c_prototype(
                c_bool, "CFStringGetCString", (self.IN, c_void_p, "the_string"),
                                            (self.IN, c_char_p, "buffer"),
                                            (self.IN, c_long,   "buffer_size"),
                                            (self.IN, c_uint32, "encoding")
            )

            self.kCFStringEncodingUTF8 = c_uint32(0x08000100)

        def cf_string_ref_to_python_str(self, cf_string_ref: c_void_p):
            cf_str_len = self.CFStringGetLength(cf_string_ref)
            buffer_size = self.CFStringGetMaximumSizeForEncoding(cf_str_len, self.kCFStringEncodingUTF8)
            buffer = create_string_buffer(buffer_size)
            success = self.CFStringGetCString(cf_string_ref, buffer, buffer_size, self.kCFStringEncodingUTF8)
            if not success:
                raise Exception("Couldn't encode string as UTF-8 into buffer")
            python_str = buffer.raw.strip(b'\x00').decode(encoding='utf-8')
            return python_str


    class CoreTextLibrary(fontfinder._platforms.CTypesLibrary):
        def __init__(self):
            super().__init__(ctypes.cdll, "CoreText", True,
                            "/System/Library/Frameworks/CoreText.framework/CoreText")
            # Note hack for compatibility with macOS greater or equals to 11.0.
            # From: https://github.com/pyglet/pyglet/blob/a44e83a265e7df8ece793de865bcf3690f66adbd/pyglet/libs/darwin/cocoapy/cocoalibs.py#L520-L524

            self.CTFontCollectionCreateFromAvailableFonts = self.c_prototype(
                c_void_p, "CTFontCollectionCreateFromAvailableFonts", (self.IN, c_void_p, "options"))

            self.CTFontCollectionCreateMatchingFontDescriptors = self.c_prototype(
                c_void_p, "CTFontCollectionCreateMatchingFontDescriptors", (self.IN, c_void_p, "font_collection"))
            
            self.CTFontDescriptorCopyAttribute = self.c_prototype(
                c_void_p, "CTFontDescriptorCopyAttribute", (self.IN, c_void_p, "font_descriptor"),
                                                        (self.IN, c_void_p, "attribute_name")
            )

            self.kCTFontFamilyNameAttribute = c_void_p.in_dll(self.lib, "kCTFontFamilyNameAttribute")
            self.kCTFontStyleNameAttribute = c_void_p.in_dll(self.lib, "kCTFontStyleNameAttribute")
            self.kCTFontDisplayNameAttribute = c_void_p.in_dll(self.lib, "kCTFontDisplayNameAttribute")
            self.kCTFontNameAttribute = c_void_p.in_dll(self.lib, "kCTFontNameAttribute")
