'''Dataclass objects and enumerations used by `fontfinder`.
'''
from collections import Counter
import csv
import dataclasses
from dataclasses import dataclass, field
import functools
from enum import Enum, Flag, auto
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlparse


@dataclass
class TextInfo:
    '''Stories Unicode script information about a string of text, suitable for selecting the best font to display
    the text.
    '''
    main_script: str = ""
    '''Name of the most frequently used Unicode script in a piece of text. This is the long Unicode script value
    (known as a property value alias), rather than the short 4-character script code.'''

    script_variant: str = ""
    '''A secondary string used when the value of `main_script` is insufficient for choosing an appropriate font.
    This is not a Unicode property, but a scheme only used by `fontfinder`. See `FontFinder.analyse()` for examples.'''

    emoji_count: int = 0
    '''Count of characters who have either the Emoji Presentation property or the Extended_Pictographic property set
    (independent of script).'''

    script_count: Counter = field(default_factory=Counter)
    '''A [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter) of the count
    of each Unicode script in the text. The keys are the string names of each script that appears in the text.'''


@dataclasses.dataclass(order=True)
class FontInfo:
    '''Stores fonta metadata about an individual font file.'''

    main_script: str
    '''Primary Unicode script covered by the font. The same format as `TextInfo.main_script`.'''

    script_variant: str
    '''Script variant covered by the font. The same format as `TextInfo.script_variant`.'''

    family_name: str
    '''Font family name.'''

    subfamily_name: str
    '''Font subfamily name (sometimes also referred to as the style name).'''

    postscript_name: str
    '''Font PostScript name.'''

    form: 'FontForm'
    '''Enum of the font form.'''

    width: 'FontWidth'
    '''Enum of the font width.'''

    weight: 'FontWeight'
    '''Enum of the font weight.'''

    style: 'FontStyle'
    '''Enum of the font style.'''

    format: 'FontFormat'
    '''Enum of the font file format.'''

    build: 'FontBuild'
    '''Enum of the font build (mainly for Google Noto fonts).'''

    tags: 'FontTag'
    '''Enum of extra tags describing the font file.'''

    url: str = ""
    '''URL download source for the font. Empty string if download is not available.'''

    downloaded_path: Path = Path()
    '''Path to the downloaded font on the local filesystem for installation. Empty if not set.'''

    def __init__(self, main_script: str | None = None, script_variant: str | None = None,
                 family_name: str | None = None, subfamily_name: str | None = None,
                 postscript_name: str | None = None, form: 'FontForm | None' = None,
                 width: 'FontWidth | None' = None, weight: 'FontWeight | None' = None,
                 style: 'FontStyle | None' = None, format: 'FontFormat | None' = None,
                 build: 'FontBuild | None' = None, tags: 'FontTag | None' = None, url: str | None  = None,
                 downloaded_path: Path | None = None 
                ):

        self.main_script = "" if main_script is None else main_script
        self.script_variant = "" if script_variant is None else script_variant
        self.family_name = "" if family_name is None else family_name
        self.subfamily_name = "" if subfamily_name is None else subfamily_name
        self.postscript_name = "" if postscript_name is None else postscript_name
        self.form = FontForm.UNSET if form is None else form
        self.width = FontWidth.NORMAL if width is None else width
        self.weight = FontWeight.REGULAR if weight is None else weight
        self.style = FontStyle.UPRIGHT if style is None else style
        self.format = FontFormat.UNSET if format is None else format
        self.build = FontBuild.UNSET if build is None else build
        self.tags = FontTag(0) if tags is None else tags
        self.url = "" if url is None else url
        self.downloaded_path = Path() if downloaded_path is None else downloaded_path

    def init_from_noto_url(self, url):
        '''Uses the url of a Google Noto font to set as much of the font metadata as possible.'''
        url_path = urlparse(url).path
        self.form = FontForm.from_str(url_path)
        self.width = FontWidth.from_str(url_path)
        self.weight = FontWeight.from_str(url_path)
        self.style = FontStyle.from_str(url_path)
        self.format = FontFormat.from_str(url_path)
        self.build = FontBuild.from_str(url_path)
        
        stem = PurePosixPath(url_path).stem
        self.postscript_name = re.sub(r"\[.*\]", "", stem)
        # Previously: self.subfamily_name = self.postscript_name.split('-')[-1]
        self.subfamily_name = " ".join([self.width.text, self.weight.text, self.style.text]).strip()

        if self.width is FontWidth.VARIABLE or self.weight is FontWeight.VARIABLE:
            self.subfamily_name = FontWeight.REGULAR.text
            self.postscript_name += "-" + FontWeight.REGULAR.text
        
        if "/slim".casefold() in url_path.casefold():
            self.tags |= FontTag.SLIM
        if "Mono".casefold() in self.postscript_name.casefold():
            self.tags |= FontTag.MONO
        if "UI" in self.postscript_name:
            self.tags |= FontTag.UI
        if "Display".casefold() in self.postscript_name.casefold():
            self.tags |= FontTag.DISPLAY
        if "Looped".casefold() in self.family_name.casefold():
            self.tags |= FontTag.LOOPED
        if self.postscript_name.startswith("NotoSansNotoSansTifinagh"):
            pass
        match = re.match(r"NotoSansTifinagh(?P<variant>.*?)-", self.postscript_name)
        if match is not None:
            self.script_variant = match['variant']
        self.url = url

    @property
    def filename(self):
        '''Returns just the filename component of this font file, using the path if it has one, or otherwise its
        URL.'''
        if self.downloaded_path is not None and self.downloaded_path != Path():
            filename = self.downloaded_path.name
        elif self.url is not None and self.url != "":
            filename = PurePosixPath(urlparse(self.url).path).name
        else:
            filename = None
        return filename 

    @property
    def fullname(self):
        '''Returns a string of the family and subfamily named combined (separated by a space).'''
        return f"{self.family_name} {self.subfamily_name}".strip()

    def copy(self):
        '''Returns a copy of this `FontInfo`.'''
        return FontInfo(**dataclasses.asdict(self))

    def str_dict(self):
        '''Returns a dictionary of strings representing this object.'''
        str_dict = dataclasses.asdict(self)
        # Convert Enum-type fields to their string names without the Enum type-name
        for field_name, field_value in str_dict.items():
            if isinstance(field_value, Flag):
                name_list = []
                for member in type(field_value):
                    if member in field_value:
                        name_list.append(member.name)
                str_dict[field_name] = "|".join(name_list)
            elif isinstance(field_value, Enum):
                str_dict[field_name] = str(field_value.name)
            elif isinstance(field_value, Path):
                if field_value == Path():
                    str_dict[field_name] = ""
                else:
                    str_dict[field_name] = str(field_value)
        return str_dict
    
    @classmethod
    def from_str_dict(cls, str_dict):
        '''Takes a dictionary of strings and returns a new FontInfo object.'''
        # Convert the string names of Enum-type fields to Enum instances
        # Use an empty (but initialized) instance to confirm actual field types. (This is because we've used forward
        # references for their type declaration, which results in their dataclasses.field type showing
        # as str, not Enum)
        blank_obj_dict = dataclasses.asdict(cls())
        for field_name, field_value in blank_obj_dict.items():
            if isinstance(field_value, Flag):
                new_value = type(field_value)(0)
                for member_name in str_dict[field_name].split("|"):
                    if len(member_name) > 0:
                        new_value |= type(field_value)[member_name]
                str_dict[field_name] = new_value
            elif isinstance(field_value, Enum):
                # Indexing an Enum with the string member name returns the member
                str_dict[field_name] = type(field_value)[str_dict[field_name]]
            elif isinstance(field_value, bool):
                str_dict[field_name] = (str_dict[field_name].upper() == "TRUE")
            elif isinstance(field_value, Path):
                print(str_dict[field_name])
                if str_dict[field_name] == "":
                    str_dict[field_name] = Path()
                else:
                    str_dict[field_name] = Path(str_dict[field_name])
        return cls(**str_dict)


def write_font_infos_to_csv(font_infos, csv_path):
    '''Write a list of `FontInfo` objects to a CSV file with the given `csv_path`.'''
    with open(csv_path, "w", encoding="utf-8") as file:
        field_names = [field.name for field in dataclasses.fields(FontInfo)]
        writer = csv.DictWriter(file, field_names)
        writer.writeheader()
        for font in font_infos:
            writer.writerow(font.str_dict())

def read_font_infos_from_csv(csv_path):
    '''Read a CSV file at `csv_path` previously created by `write_font_infos_to_csv()` and use it to create and
    return a list of `FontInfo` objects.'''
    font_infos = []
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            font_infos.append(FontInfo.from_str_dict(row))
    return font_infos


@functools.total_ordering
class FontForm(Enum):
    '''Enum of font forms.'''
    UNSET       = auto()
    SERIF       = auto()
    SANS_SERIF  = auto()
    # Arabic forms
    NASKH       = auto()
    # Perso-Arabic forms
    NASTALIQ    = auto()
    # Hebrew forms
    RASHI       = auto()

    @property
    def text(self):
        return font_form_str_data[self][0]

    @classmethod
    def from_str(cls, string: str):
        result = FontForm.UNSET
        for font_form, data in font_form_str_data.items():
            if data[1].search(string):
                result = font_form
        return result
    
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value


font_form_str_data = {
    FontForm.SERIF:         ("Serif",       re.compile(r"Serif",    re.IGNORECASE)),
    FontForm.SANS_SERIF:    ("Sans",        re.compile(r"Sans",     re.IGNORECASE)),
    FontForm.NASKH:         ("Naskh",       re.compile(r"Naskh",    re.IGNORECASE)),
    FontForm.NASTALIQ:      ("Nastaliq",    re.compile(r"Nastaliq", re.IGNORECASE)),
    FontForm.RASHI:         ("Rashi",       re.compile(r"Rashi",    re.IGNORECASE)),
}
'''Data for string conversion to and from `FontForm`.'''


@functools.total_ordering
class FontWidth(Enum):
    '''Enum of font widths.'''
    NORMAL      = auto()
    VARIABLE    = auto()
    EXTRA_COND  = auto()
    CONDENSED   = auto()
    SEMI_COND   = auto()

    @property
    def text(self):
        if self is FontWidth.NORMAL:
            result = ""
        else:
            result = font_width_str_data[self][0]
        return result

    @classmethod
    def from_str(cls, string: str):
        result = FontWidth.NORMAL
        for font_width, data in font_width_str_data.items():
            if data[1].search(string):
                result = font_width
        return result

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value


font_width_str_data = {
    FontWidth.VARIABLE:     ("wdth",           re.compile(r"wdth",             re.IGNORECASE)),
    FontWidth.CONDENSED:    ("Condensed",      re.compile(r"Condensed",        re.IGNORECASE)),
    FontWidth.EXTRA_COND:   ("ExtraCondensed", re.compile(r"Extra.?Condensed", re.IGNORECASE)),
    FontWidth.SEMI_COND:    ("SemiCondensed",  re.compile(r"Semi.?Condensed",  re.IGNORECASE)),
}
'''Data for string conversion to and from `FontWidth`.'''


@functools.total_ordering
class FontWeight(Enum):
    '''Enum of font weights.'''
    REGULAR     = auto()
    VARIABLE    = auto()
    DEMI_LIGHT  = auto()
    EXTRA_LIGHT = auto()
    LIGHT       = auto()
    THIN        = auto()
    MEDIUM      = auto()
    SEMI_BOLD   = auto()
    BOLD        = auto()
    EXTRA_BOLD  = auto()
    BLACK       = auto()

    @property
    def text(self):
        return font_weight_str_data[self][0]

    @classmethod
    def from_str(cls, string: str):
        result = FontWeight.REGULAR
        for font_width, data in font_weight_str_data.items():
            if data[1].search(string):
                result = font_width
        return result

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value


font_weight_str_data = {
    FontWeight.VARIABLE:        ("wght",       re.compile(r"wght",             re.IGNORECASE)),
    FontWeight.REGULAR:         ("Regular",    re.compile(r"Regular",          re.IGNORECASE)),
    FontWeight.LIGHT:           ("Light",      re.compile(r"Light",            re.IGNORECASE)),
    FontWeight.DEMI_LIGHT:      ("DemiLight",  re.compile(r"Demi.?Light",      re.IGNORECASE)),
    FontWeight.EXTRA_LIGHT:     ("ExtraLight", re.compile(r"Extra.?Light",     re.IGNORECASE)),
    FontWeight.THIN:            ("Thin",       re.compile(r"Thin",             re.IGNORECASE)),
    FontWeight.MEDIUM:          ("Medium",     re.compile(r"Medium",           re.IGNORECASE)),
    FontWeight.BOLD:            ("Bold",       re.compile(r"Bold",             re.IGNORECASE)),
    FontWeight.SEMI_BOLD:       ("SemiBold",   re.compile(r"Semi.?Bold",       re.IGNORECASE)),
    FontWeight.EXTRA_BOLD:      ("ExtraBold",  re.compile(r"Extra.?Bold",      re.IGNORECASE)),
    FontWeight.BLACK:           ("Black",      re.compile(r"Black",            re.IGNORECASE)),
}
'''Data for string conversion to and from `FontWeight`.'''


@functools.total_ordering
class FontStyle(Enum):
    '''Enum of font styles.'''
    UPRIGHT     = auto()
    ITALIC      = auto()
 
    @property
    def text(self):
        if self is FontStyle.UPRIGHT:
            result = ""
        else:
            result = font_style_str_data[self][0]
        return result

    @classmethod
    def from_str(cls, string: str):
        result = FontStyle.UPRIGHT
        for font_style, data in font_style_str_data.items():
            if data[1].search(string):
                result = font_style
        return result

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value


font_style_str_data = {
    FontStyle.ITALIC:          ("Italic", re.compile(r"Italic",            re.IGNORECASE)),
}
'''Data for string conversion to and from `FontStyle`.'''


@functools.total_ordering
class FontFormat(Enum):
    '''Enum of font file formats.'''
    UNSET       = ""
    OTF         = "OTF"
    OTC         = "OTC"
    TTF         = "TTF"

    @property
    def text(self):
        return font_format_str_data[self][0]

    @classmethod
    def from_str(cls, string: str):
        result = FontFormat.UNSET
        for font_format, data in font_format_str_data.items():
            if data[1].search(string):
                result = font_format
        return result

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value


font_format_str_data = {
    FontFormat.OTF:             ("OTF", re.compile(r"\.OTF",            re.IGNORECASE)),
    FontFormat.OTC:             ("OTC", re.compile(r"\.OTC",            re.IGNORECASE)),
    FontFormat.TTF:             ("TTF", re.compile(r"\.TTF",            re.IGNORECASE)),
}
'''Data for string conversion to and from `FontFormat`.'''


@functools.total_ordering
class FontBuild(Enum):
    '''Enum of font builds (mainly for Google Noto fonts).'''
    UNSET       = auto()
    UNHINTED    = auto()
    HINTED      = auto()
    FULL        = auto()

    @property
    def text(self):
        return font_build_str_data[self][0]

    @classmethod
    def from_str(cls, string: str):
        result = FontBuild.UNSET
        for font_build, data in font_build_str_data.items():
            if data[1].search(string):
                result = font_build
        return result

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value


font_build_str_data = {
    FontBuild.HINTED:      ("Hinted",   re.compile(r"Hinted",    re.IGNORECASE)),
    FontBuild.UNHINTED:    ("Unhinted", re.compile(r"Unhinted",  re.IGNORECASE)),
    FontBuild.FULL:        ("Full",     re.compile(r"Full",      re.IGNORECASE))
}
'''Data for string conversion to and from `FontBuild`.'''


@functools.total_ordering
class FontTag(Flag):
    '''Enum of extra tags describing the font file.'''
    MONO        = auto()
    '''A monospaced font.'''
    UI          = auto()
    '''A font aimed at UI display.'''
    DISPLAY     = auto()
    '''A display font.'''
    SLIM        = auto()
    '''A Google Noto slim-build variable font.'''
    LOOPED      = auto()
    '''A looped variant (e.g. for Thai fonts)'''

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value
